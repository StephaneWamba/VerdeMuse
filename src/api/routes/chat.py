from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any, Optional
import uuid

from src.domain.models.message import ChatRequest, ChatResponse, MessageRole
from src.infrastructure.llm.mistral_client import get_mistral_client, MistralClient
from src.infrastructure.vector_store.vector_store import get_vector_store, VectorStore

router = APIRouter()

# In-memory store for conversation histories
# Will be replaced with a proper database in later phases
conversation_histories: Dict[str, List[Dict[str, Any]]] = {}

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    mistral_client: MistralClient = Depends(get_mistral_client),
    vector_store: VectorStore = Depends(get_vector_store)
):
    """
    Process a chat message and return a response.
    
    This endpoint:
    1. Retrieves or creates a conversation history
    2. Searches the vector store for relevant information
    3. Sends the user message and context to the LLM
    4. Returns the LLM's response
    """
    # Get or create conversation ID
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    # Get or initialize conversation history
    conversation_history = conversation_histories.get(conversation_id, [])
    
    # Add user message to history
    user_message = {
        "role": MessageRole.USER,
        "content": request.message
    }
    conversation_history.append(user_message)
    
    # Try to get relevant context from vector store
    relevant_documents = []
    try:
        # If vector store is initialized, search for relevant information
        search_results = vector_store.similarity_search(request.message, k=3)
        relevant_documents = [doc.page_content for doc in search_results]
    except Exception as e:
        # If no results or error, proceed without context
        print(f"Vector search error: {e}")
        pass
    
    # Generate response with or without context
    if relevant_documents:
        assistant_response = mistral_client.generate_answer_with_context(
            request.message,
            relevant_documents,
            conversation_history
        )
        sources = [{"content": doc, "confidence": 0.9} for doc in relevant_documents]
    else:
        # No relevant documents found, generate response based just on conversation
        assistant_response = mistral_client.generate_response(
            request.message,
            conversation_history
        )
        sources = None
    
    # Add assistant response to history
    conversation_history.append({
        "role": MessageRole.ASSISTANT,
        "content": assistant_response
    })
    
    # Update conversation history
    conversation_histories[conversation_id] = conversation_history
    
    # Prepare response
    response = ChatResponse(
        message=assistant_response,
        conversation_id=conversation_id,
        sources=sources
    )
    
    return response

@router.get("/{conversation_id}", response_model=List[Dict[str, Any]])
async def get_conversation_history(conversation_id: str):
    """
    Retrieve the conversation history for a given conversation ID.
    """
    if conversation_id not in conversation_histories:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation_histories[conversation_id]

@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete a conversation history.
    """
    if conversation_id in conversation_histories:
        del conversation_histories[conversation_id]
    
    return {"status": "success", "message": "Conversation deleted"}