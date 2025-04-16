from typing import List, Dict, Any, Optional
from langchain.llms import BaseLLM
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from config.config import settings

class MistralClient:
    """
    Client for interacting with the Mistral LLM.
    This class provides methods to generate responses and perform tasks with the LLM.
    """
    
    def __init__(self, api_key: Optional[str] = None, streaming: bool = False):
        """
        Initialize the Mistral client.
        
        Args:
            api_key: Optional API key for Mistral API. If None, uses config setting.
            streaming: Whether to stream responses or not.
        """
        self.api_key = api_key or settings.MISTRAL_API_KEY
        
        # For now, using OpenAI client with model switching as placeholder
        # Will be replaced with native Mistral client in future
        callbacks = None
        if streaming:
            callbacks = CallbackManager([StreamingStdOutCallbackHandler()])
        
        self.llm = ChatOpenAI(
            api_key=self.api_key, 
            model_name="mistral-medium",  # Will use actual Mistral model when integrated
            streaming=streaming,
            callback_manager=callbacks,
            temperature=0.7
        )
    
    def generate_response(
        self, 
        user_message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            user_message: The user's message
            conversation_history: Optional list of previous messages in the conversation
            system_prompt: Optional system prompt
            
        Returns:
            The LLM's response
        """
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        else:
            # Default system prompt for VerdeMuse assistant
            default_prompt = """You are the VerdeMuse Customer Support Assistant, an AI designed to help customers with questions 
            about VerdeMuse's sustainable products. Be friendly, concise, and helpful. Always prioritize accurate information 
            and admit when you don't know something rather than making up answers."""
            messages.append(SystemMessage(content=default_prompt))
        
        # Add conversation history
        if conversation_history:
            for message in conversation_history:
                if message["role"] == "user":
                    messages.append(HumanMessage(content=message["content"]))
                elif message["role"] == "assistant":
                    messages.append(AIMessage(content=message["content"]))
                elif message["role"] == "system":
                    messages.append(SystemMessage(content=message["content"]))
        
        # Add current user message
        messages.append(HumanMessage(content=user_message))
        
        # Generate response
        response = self.llm.invoke(messages)
        
        return response.content
    
    def generate_answer_with_context(
        self, 
        user_message: str, 
        context_documents: List[str],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate a response from the LLM with relevant context documents.
        
        Args:
            user_message: The user's message
            context_documents: List of context documents to inform the LLM
            conversation_history: Optional list of previous messages in the conversation
            
        Returns:
            The LLM's response incorporating the context
        """
        # Combine context documents into a single string
        context = "\n\n".join([f"Document {i+1}: {doc}" for i, doc in enumerate(context_documents)])
        
        # Create system prompt with context
        system_prompt = f"""You are the VerdeMuse Customer Support Assistant, an AI designed to help customers with questions 
        about VerdeMuse's sustainable products. Be friendly, concise, and helpful.
        
        Use the following context to answer the user's question. If the context doesn't contain relevant information, 
        admit that you don't know rather than making up an answer.
        
        Context:
        {context}
        """
        
        # Generate response with the context-enhanced system prompt
        return self.generate_response(user_message, conversation_history, system_prompt)

# Create a singleton instance
mistral_client = MistralClient()

def get_mistral_client() -> MistralClient:
    """
    Returns the Mistral client instance.
    This can be used as a FastAPI dependency.
    """
    return mistral_client