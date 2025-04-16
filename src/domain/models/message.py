from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
import uuid

class MessageRole(str, Enum):
    """Enum representing the possible roles in a conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(BaseModel):
    """
    Model representing a chat message in the VerdeMuse system.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    conversation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "role": "user",
                "content": "How do I care for my VerdeMuse plant?",
                "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "metadata": {"source": "web_widget", "browser": "chrome"}
            }
        }

class ConversationHistory(BaseModel):
    """
    Model representing a conversation history.
    """
    conversation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Message] = []
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None
    
    def add_message(self, role: MessageRole, content: str) -> Message:
        """
        Add a new message to the conversation.
        
        Args:
            role: The role of the message sender
            content: The content of the message
            
        Returns:
            The created message
        """
        message = Message(
            role=role,
            content=content,
            conversation_id=self.conversation_id
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message

class ChatRequest(BaseModel):
    """
    Model representing a chat request to the API.
    """
    message: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "message": "How do I care for my VerdeMuse plant?",
                "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
            }
        }

class ChatResponse(BaseModel):
    """
    Model representing a chat response from the API.
    """
    message: str
    conversation_id: str
    sources: Optional[List[Dict[str, Any]]] = None
    confidence: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "message": "To care for your VerdeMuse plant, water it once a week and place it in indirect sunlight.",
                "conversation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "sources": [
                    {"title": "Plant Care Guide", "url": "https://verdemuse.com/care-guide"}
                ],
                "confidence": 0.95
            }
        }