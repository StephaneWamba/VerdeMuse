import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

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

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        # If there are sources, display them in an expander
        if "sources" in message and message["sources"]:
            with st.expander("View sources"):
                for idx, source in enumerate(message["sources"]):
                    st.markdown(f"**Source {idx+1}:**\n{source['content']}")

# Function to call the API
def query_api(message):
    try:
        response = requests.post(
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
            st.error(f"Error: {response.status_code} - {response.text}")
            return {
                "message": "Sorry, I encountered an error while processing your request.",
                "conversation_id": st.session_state.conversation_id or "",
                "sources": None
            }
    except Exception as e:
        st.error(f"Error connecting to the API: {str(e)}")
        return {
            "message": "Sorry, I couldn't connect to the backend service.",
            "conversation_id": st.session_state.conversation_id or "",
            "sources": None
        }

# Chat input
if prompt := st.chat_input("How can I help you today?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat container
    with st.chat_message("user"):
        st.write(prompt)
    
    # Display assistant response in chat container
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
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
                with st.expander("View sources"):
                    for idx, source in enumerate(sources):
                        st.markdown(f"**Source {idx+1}:**\n{source['content']}")
    
    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response,
        "sources": sources
    })

# Sidebar with settings
with st.sidebar:
    st.header("About VerdeMuse")
    st.info("VerdeMuse is an intelligent customer support virtual assistant that provides instant support for our sustainable product line.")
    
    st.header("Settings")
    settings_use_history = st.toggle("Enable conversation history", value=True)
    settings_creativity = st.slider("Response creativity", min_value=0, max_value=100, value=50)
    
    # Add a clear conversation button
    if st.button("Clear Conversation", key="clear"):
        if st.session_state.conversation_id:
            try:
                # Delete conversation on backend
                requests.delete(f"{API_URL}/api/chat/{st.session_state.conversation_id}")
            except:
                pass
        
        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.experimental_rerun()
    
    # Add a logout button for future authentication functionality
    if st.button("Logout", key="logout"):
        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.experimental_rerun()

# Footer
st.markdown("---")
st.caption("© 2025 VerdeMuse - Powered by AI")