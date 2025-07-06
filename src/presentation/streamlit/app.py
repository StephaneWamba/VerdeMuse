import streamlit as st
import httpx
import asyncio
import json
import os
from dotenv import load_dotenv
import hashlib
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

# Configure API endpoint
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Configure page
st.set_page_config(
    page_title="VerdeMuse Customer Support",
    page_icon="🌿",
    layout="wide"
)

# App title and description
st.title("🌿 VerdeMuse Customer Support")
st.markdown("### Your intelligent virtual assistant for product support")

# Initialize session state for chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

# Cache for API responses using session state
def get_cached_response(message_hash: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """Cache API responses based on message hash to avoid repeated calls."""
    cache_key = f"cache_{message_hash}"
    return st.session_state.get(cache_key, {})

# Async function to call the API
async def query_api_async(message: str) -> Dict[str, Any]:
    """
    Asynchronously query the API with improved error handling and timeout.
    """
    try:
        timeout = httpx.Timeout(30.0)  # 30 second timeout
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{API_URL}/api/chat/",
                json={
                    "message": message,
                    "conversation_id": st.session_state.conversation_id
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return {
                    "message": "Sorry, I encountered an error while processing your request.",
                    "conversation_id": st.session_state.conversation_id or "",
                    "sources": None
                }
    except httpx.TimeoutException:
        st.error("Request timed out. Please try again.")
        return {
            "message": "Sorry, the request took too long. Please try again.",
            "conversation_id": st.session_state.conversation_id or "",
            "sources": None
        }
    except httpx.ConnectError:
        st.error("Unable to connect to the backend service. Please check if the API is running.")
        return {
            "message": "Sorry, I couldn't connect to the backend service.",
            "conversation_id": st.session_state.conversation_id or "",
            "sources": None
        }
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return {
            "message": "Sorry, I encountered an unexpected error.",
            "conversation_id": st.session_state.conversation_id or "",
            "sources": None
        }

# Synchronous wrapper for async function
def query_api(message: str) -> Dict[str, Any]:
    """
    Synchronous wrapper for the async API call.
    Uses caching to avoid repeated calls for the same message.
    """
    # Create a hash of the message for caching
    message_hash = hashlib.md5(f"{message}:{st.session_state.conversation_id}".encode()).hexdigest()
    
    # Check cache first
    if f"cache_{message_hash}" in st.session_state:
        return st.session_state[f"cache_{message_hash}"]
    
    # Make the API call
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(query_api_async(message))
        loop.close()
        
        # Cache the result
        st.session_state[f"cache_{message_hash}"] = result
        return result
    except Exception as e:
        st.error(f"Error in API call: {str(e)}")
        return {
            "message": "Sorry, I encountered an error while processing your request.",
            "conversation_id": st.session_state.conversation_id or "",
            "sources": None
        }

# Display chat messages with improved rendering
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        # If there are sources, display them in an expander
        if "sources" in message and message["sources"]:
            with st.expander("📚 View sources"):
                for idx, source in enumerate(message["sources"]):
                    st.markdown(f"**Source {idx+1}:**")
                    st.markdown(f"_{source['content']}_")
                    st.markdown("---")

# Chat input with improved UX
if prompt := st.chat_input("How can I help you today?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat container
    with st.chat_message("user"):
        st.write(prompt)
    
    # Display assistant response in chat container
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            # Call API and get response
            api_response = query_api(prompt)
            response = api_response["message"]
            sources = api_response.get("sources")
            
            # Update conversation ID
            if "conversation_id" in api_response:
                st.session_state.conversation_id = api_response["conversation_id"]
            
            # Display assistant response
            st.write(response)
            
            # Display sources if available
            if sources:
                with st.expander("📚 View sources"):
                    for idx, source in enumerate(sources):
                        st.markdown(f"**Source {idx+1}:**")
                        st.markdown(f"_{source['content']}_")
                        st.markdown("---")
    
    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response,
        "sources": sources
    })

# Sidebar with settings and improved functionality
with st.sidebar:
    st.header("🌿 About VerdeMuse")
    st.info("VerdeMuse is an intelligent customer support virtual assistant that provides instant support for our sustainable product line.")
    
    st.header("⚙️ Settings")
    
    # Performance settings
    st.subheader("Performance")
    cache_enabled = st.toggle("Enable response caching", value=True)
    if not cache_enabled:
        # Clear cache if disabled
        for key in list(st.session_state.keys()):
            if key.startswith("cache_"):
                del st.session_state[key]
    
    # Conversation settings
    st.subheader("Conversation")
    max_messages = st.slider("Max messages to display", min_value=10, max_value=100, value=50)
    
    # Trim messages if over limit
    if len(st.session_state.messages) > max_messages:
        st.session_state.messages = st.session_state.messages[-max_messages:]
    
    # API settings
    st.subheader("API")
    api_timeout = st.slider("API timeout (seconds)", min_value=5, max_value=60, value=30)
    
    # Clear conversation button with confirmation
    if st.button("🗑️ Clear Conversation", key="clear"):
        if st.session_state.conversation_id:
            try:
                # Async delete call
                async def delete_conversation():
                    async with httpx.AsyncClient() as client:
                        await client.delete(f"{API_URL}/api/chat/{st.session_state.conversation_id}")
                
                # Run the async delete
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(delete_conversation())
                    loop.close()
                except:
                    pass  # Ignore errors in cleanup
            except:
                pass
        
        # Clear local state
        st.session_state.messages = []
        st.session_state.conversation_id = None
        
        # Clear cache
        for key in list(st.session_state.keys()):
            if key.startswith("cache_"):
                del st.session_state[key]
        
        st.rerun()
    
    # Performance metrics
    st.subheader("📊 Performance")
    message_count = len(st.session_state.messages)
    cache_count = len([k for k in st.session_state.keys() if k.startswith("cache_")])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Messages", message_count)
    with col2:
        st.metric("Cached", cache_count)
    
    # Connection status
    st.subheader("🔗 Connection")
    if st.button("Test API Connection"):
        try:
            async def test_connection():
                async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                    response = await client.get(f"{API_URL}/health")
                    return response.status_code == 200
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            is_connected = loop.run_until_complete(test_connection())
            loop.close()
            
            if is_connected:
                st.success("✅ API is connected")
            else:
                st.error("❌ API is not responding")
        except Exception as e:
            st.error(f"❌ Connection failed: {str(e)}")

# Footer with version info
st.markdown("---")
st.caption("© 2025 VerdeMuse - Powered by AI | Version 1.1.0 (Performance Optimized)")