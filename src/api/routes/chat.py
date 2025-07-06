from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
import uuid
import hashlib
import json
import logging
from functools import lru_cache

from src.domain.models.message import ChatRequest, ChatResponse, MessageRole
from src.infrastructure.llm.mistral_client import get_mistral_client, MistralClient
from src.infrastructure.vector_store.vector_store import get_vector_store, VectorStore
from src.infrastructure.conversation_store import get_conversation_store, ConversationStore

logger = logging.getLogger(__name__)
router = APIRouter()

# LRU cache for LLM responses to avoid repeated expensive calls
@lru_cache(maxsize=1000)
def get_cached_llm_response(message_hash: str, context_hash: str) -> Optional[str]:
    """
    Cache LLM responses based on message and context hashes.
    This prevents repeated expensive LLM calls for similar queries.
    """
    # This will be populated by the chat endpoint
    return None

def set_cached_llm_response(message_hash: str, context_hash: str, response: str):
    """
    Store LLM response in cache.
    Uses a workaround since lru_cache doesn't support setting values directly.
    """
    # Create a temporary cache key storage
    cache_key = f"{message_hash}:{context_hash}"
    if not hasattr(set_cached_llm_response, 'cache'):
        set_cached_llm_response.cache = {}
    set_cached_llm_response.cache[cache_key] = response

def get_llm_response_from_cache(message_hash: str, context_hash: str) -> Optional[str]:
    """Get LLM response from cache if available."""
    cache_key = f"{message_hash}:{context_hash}"
    if hasattr(set_cached_llm_response, 'cache'):
        return set_cached_llm_response.cache.get(cache_key)
    return None

async def cleanup_old_conversations(conversation_store: ConversationStore):
    """Background task to cleanup old conversations."""
    try:
        cleaned_count = await conversation_store.cleanup_expired_conversations()
        logger.info(f"Cleaned up {cleaned_count} expired conversations")
    except Exception as e:
        logger.error(f"Error during conversation cleanup: {e}")

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    mistral_client: MistralClient = Depends(get_mistral_client),
    vector_store: VectorStore = Depends(get_vector_store),
    conversation_store: ConversationStore = Depends(get_conversation_store)
):
    """
    Process a chat message and return a response.
    
    This endpoint:
    1. Retrieves or creates a conversation history from Redis
    2. Searches the vector store for relevant information
    3. Checks cache for similar queries
    4. Sends the user message and context to the LLM
    5. Caches the response
    6. Returns the LLM's response
    """
    try:
        # Get or create conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Get conversation history from Redis
        conversation_history = await conversation_store.get_conversation(conversation_id)
        
        # Create message hash for caching
        message_hash = hashlib.md5(request.message.encode()).hexdigest()
        
        # Add user message to conversation store
        user_message = {
            "role": MessageRole.USER.value,
            "content": request.message
        }
                 await conversation_store.add_message(conversation_id, user_message)
         
         # Search for relevant context with error handling
         relevant_documents = []
         context_hash = "no_context"
         
         try:
             # If vector store is initialized, search for relevant information
             search_results = vector_store.similarity_search(request.message, k=3)
             relevant_documents = [doc.page_content for doc in search_results]
             
             # Create context hash for caching
             if relevant_documents:
                 context_content = "\n".join(relevant_documents)
                 context_hash = hashlib.md5(context_content.encode()).hexdigest()
         except Exception as e:
             logger.warning(f"Vector search error: {e}")
             # Continue without context
             pass
         
         # Check cache for LLM response
         cached_response = get_llm_response_from_cache(message_hash, context_hash)
         
         if cached_response:
             logger.debug(f"Using cached response for message: {request.message[:50]}...")
             assistant_response = cached_response
             sources = None
         else:
             # Generate response with or without context
             if relevant_documents:
                 assistant_response = mistral_client.generate_answer_with_context(
                     request.message,
                     relevant_documents,
                     conversation_history
                 )
                 sources = [
                     {"content": doc, "confidence": 0.9} 
                     for doc in relevant_documents
                 ]
             else:
                 # No relevant documents found, generate response based on conversation
                 assistant_response = mistral_client.generate_response(
                     request.message,
                     conversation_history
                 )
                 sources = None
             
             # Cache the response
             set_cached_llm_response(message_hash, context_hash, assistant_response)
             logger.debug(f"Cached new response for message: {request.message[:50]}...")
        
        # Add assistant response to conversation store
        assistant_message = {
            "role": MessageRole.ASSISTANT.value,
            "content": assistant_response
        }
        await conversation_store.add_message(conversation_id, assistant_message)
        
        # Schedule background cleanup
        background_tasks.add_task(cleanup_old_conversations, conversation_store)
        
        # Prepare response
        response = ChatResponse(
            message=assistant_response,
            conversation_id=conversation_id,
            sources=sources if relevant_documents else None
        )
        
        logger.info(f"Chat response generated for conversation {conversation_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{conversation_id}", response_model=List[Dict[str, Any]])
async def get_conversation_history(
    conversation_id: str,
    conversation_store: ConversationStore = Depends(get_conversation_store)
):
    """
    Retrieve the conversation history for a given conversation ID.
    """
    try:
        messages = await conversation_store.get_conversation(conversation_id)
        if not messages:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return messages
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    conversation_store: ConversationStore = Depends(get_conversation_store)
):
    """
    Delete a conversation history.
    """
    try:
        success = await conversation_store.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {"status": "success", "message": "Conversation deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{conversation_id}/metadata")
async def get_conversation_metadata(
    conversation_id: str,
    conversation_store: ConversationStore = Depends(get_conversation_store)
):
    """
    Get conversation metadata including message count and last update time.
    """
    try:
        metadata = await conversation_store.get_conversation_metadata(conversation_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return metadata
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving metadata for conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/cleanup")
async def manual_cleanup(
    conversation_store: ConversationStore = Depends(get_conversation_store)
):
    """
    Manually trigger cleanup of expired conversations.
    """
    try:
        cleaned_count = await conversation_store.cleanup_expired_conversations()
        return {
            "status": "success", 
            "message": f"Cleaned up {cleaned_count} expired conversations"
        }
        
    except Exception as e:
        logger.error(f"Error during manual cleanup: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats/cache")
async def get_cache_stats():
    """
    Get cache statistics for monitoring.
    """
    try:
        cache_size = 0
        if hasattr(set_cached_llm_response, 'cache'):
            cache_size = len(set_cached_llm_response.cache)
        
        return {
            "cache_size": cache_size,
            "cache_limit": 1000,
            "cache_utilization": f"{(cache_size / 1000) * 100:.1f}%"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving cache stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")