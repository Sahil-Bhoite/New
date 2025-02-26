import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from langchain.memory import ConversationBufferWindowMemory

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Set the Streamlit page configuration
st.set_page_config(page_title="GPT Chatbot", layout="wide")
st.header("GPT Chatbot: Powered by OpenAI")

# Sidebar configuration
with st.sidebar:
    st.title("GPT Chatbot")

# Hide Streamlit's default menu
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Initialize session state for messages and memory
if "messages" not in st.session_state:
    st.session_state.messages = []

if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferWindowMemory(k=2, memory_key="chat_history", return_messages=True)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
input_prompt = st.chat_input("Type your message here...")
if input_prompt:
    # Add user message to session state and memory
    st.session_state.messages.append({"role": "user", "content": input_prompt})
    st.session_state.memory.save_context({"input": input_prompt}, {"output": ""})  # Save user input to memory
    
    with st.chat_message("user"):
        st.markdown(input_prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Get the chat history from memory
        memory_content = st.session_state.memory.load_memory_variables({})["chat_history"]
        messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        
        # Add previous conversation from memory
        for mem in memory_content:
            if mem.type == "human":  # HumanMessage for user input
                messages.append({"role": "user", "content": mem.content})
            elif mem.type == "ai":  # AIMessage for assistant response
                messages.append({"role": "assistant", "content": mem.content})
        
        # Add the current user input
        messages.append({"role": "user", "content": input_prompt})

        # Get response from OpenAI with memory context
        response = client.chat.completions.create(
            model="gpt-4o",  
            messages=messages,
            stream=True
        )

        # Stream the response
        for chunk in response:
            content = chunk.choices[0].delta.content or ""
            full_response += content
            message_placeholder.markdown(full_response + "▌")
        
        # Finalize the message without the cursor
        message_placeholder.markdown(full_response)
        
        # Add assistant response to session state and memory
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.memory.save_context({"input": input_prompt}, {"output": full_response})

# Footer (optional, kept minimal)
st.markdown("""
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: black;
        text-align: center;
    }
    </style>
    <div class="footer">
    </div>
    """, unsafe_allow_html=True)