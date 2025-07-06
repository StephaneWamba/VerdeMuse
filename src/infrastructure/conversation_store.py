"""
Conversation store implementation for VerdeMuse.
Provides Redis-based persistent storage for conversation histories.
"""

import redis
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import logging
from config.config import settings

logger = logging.getLogger(__name__)

class ConversationStore:
    """
    Redis-based conversation store for persistent chat histories.
    Provides async operations and automatic cleanup of old conversations.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize the conversation store.
        
        Args:
            redis_url: Redis connection URL. If None, uses environment variables.
        """
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_client = None
        self.default_ttl = 3600  # 1 hour default TTL
        
    async def connect(self):
        """Establish Redis connection."""
        if self.redis_client is None:
            try:
                self.redis_client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_keepalive=True,
                    socket_keepalive_options={},
                    health_check_interval=30
                )
                # Test connection
                await asyncio.to_thread(self.redis_client.ping)
                logger.info("Connected to Redis successfully")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                # Fallback to in-memory storage
                self.redis_client = None
    
    async def disconnect(self):
        """Close Redis connection."""
        if self.redis_client:
            await asyncio.to_thread(self.redis_client.close)
            self.redis_client = None
    
    def _get_conversation_key(self, conversation_id: str) -> str:
        """Generate Redis key for conversation."""
        return f"conversation:{conversation_id}"
    
    def _get_metadata_key(self, conversation_id: str) -> str:
        """Generate Redis key for conversation metadata."""
        return f"conversation_meta:{conversation_id}"
    
    async def get_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history.
        
        Args:
            conversation_id: Unique conversation identifier
            
        Returns:
            List of message dictionaries
        """
        if not self.redis_client:
            await self.connect()
        
        try:
            key = self._get_conversation_key(conversation_id)
            data = await asyncio.to_thread(self.redis_client.get, key)
            
            if data:
                return json.loads(data)
            return []
        except Exception as e:
            logger.error(f"Error retrieving conversation {conversation_id}: {e}")
            return []
    
    async def save_conversation(
        self, 
        conversation_id: str, 
        messages: List[Dict[str, Any]], 
        ttl: Optional[int] = None
    ) -> bool:
        """
        Save conversation history.
        
        Args:
            conversation_id: Unique conversation identifier
            messages: List of message dictionaries
            ttl: Time to live in seconds (optional)
            
        Returns:
            True if saved successfully, False otherwise
        """
        if not self.redis_client:
            await self.connect()
        
        try:
            key = self._get_conversation_key(conversation_id)
            metadata_key = self._get_metadata_key(conversation_id)
            
            # Serialize messages
            data = json.dumps(messages, default=str)
            
            # Save conversation data
            ttl = ttl or self.default_ttl
            await asyncio.to_thread(self.redis_client.setex, key, ttl, data)
            
            # Save metadata
            metadata = {
                "conversation_id": conversation_id,
                "message_count": len(messages),
                "last_updated": datetime.now().isoformat(),
                "ttl": ttl
            }
            await asyncio.to_thread(self.redis_client.setex, metadata_key, ttl, json.dumps(metadata))
            
            logger.debug(f"Saved conversation {conversation_id} with {len(messages)} messages")
            return True
            
        except Exception as e:
            logger.error(f"Error saving conversation {conversation_id}: {e}")
            return False
    
    async def add_message(
        self, 
        conversation_id: str, 
        message: Dict[str, Any], 
        ttl: Optional[int] = None
    ) -> bool:
        """
        Add a single message to conversation.
        
        Args:
            conversation_id: Unique conversation identifier
            message: Message dictionary
            ttl: Time to live in seconds (optional)
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            # Get existing conversation
            messages = await self.get_conversation(conversation_id)
            
            # Add timestamp if not present
            if "timestamp" not in message:
                message["timestamp"] = datetime.now().isoformat()
            
            # Add new message
            messages.append(message)
            
            # Save updated conversation
            return await self.save_conversation(conversation_id, messages, ttl)
            
        except Exception as e:
            logger.error(f"Error adding message to conversation {conversation_id}: {e}")
            return False
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.
        
        Args:
            conversation_id: Unique conversation identifier
            
        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.redis_client:
            await self.connect()
        
        try:
            key = self._get_conversation_key(conversation_id)
            metadata_key = self._get_metadata_key(conversation_id)
            
            # Delete both conversation and metadata
            await asyncio.to_thread(self.redis_client.delete, key, metadata_key)
            
            logger.debug(f"Deleted conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting conversation {conversation_id}: {e}")
            return False
    
    async def get_conversation_metadata(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get conversation metadata.
        
        Args:
            conversation_id: Unique conversation identifier
            
        Returns:
            Metadata dictionary
        """
        if not self.redis_client:
            await self.connect()
        
        try:
            key = self._get_metadata_key(conversation_id)
            data = await asyncio.to_thread(self.redis_client.get, key)
            
            if data:
                return json.loads(data)
            return {}
            
        except Exception as e:
            logger.error(f"Error retrieving metadata for conversation {conversation_id}: {e}")
            return {}
    
    async def cleanup_expired_conversations(self) -> int:
        """
        Clean up expired conversations.
        
        Returns:
            Number of conversations cleaned up
        """
        if not self.redis_client:
            await self.connect()
        
        try:
            # Get all conversation keys
            pattern = "conversation:*"
            keys = await asyncio.to_thread(self.redis_client.keys, pattern)
            
            cleaned_count = 0
            for key in keys:
                ttl = await asyncio.to_thread(self.redis_client.ttl, key)
                if ttl == -1:  # No expiration set
                    # Set default expiration
                    await asyncio.to_thread(self.redis_client.expire, key, self.default_ttl)
                elif ttl == -2:  # Key doesn't exist
                    cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} expired conversations")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return 0

# Singleton instance
_conversation_store = None

async def get_conversation_store() -> ConversationStore:
    """
    Get the conversation store instance.
    This can be used as a FastAPI dependency.
    """
    global _conversation_store
    if _conversation_store is None:
        _conversation_store = ConversationStore()
        await _conversation_store.connect()
    return _conversation_store