import streamlit as st

# MUST BE THE VERY FIRST STREAMLIT COMMAND
st.set_page_config(page_title="AI Resume Matcher", layout="wide")

from dotenv import load_dotenv
import os
import uuid
import sys
from langchain_core.messages import HumanMessage, AIMessage

# SQLite fix for Streamlit Cloud (ChromaDB requirement)
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

# Load environment variables
load_dotenv()

import glob
import json
import html
import subprocess
from datetime import datetime

# Streamlit Cloud Deployment Fix: Auto-initialize DB if it doesn't exist
if not os.path.exists("chroma_db"):
    with st.spinner("Initializing vector database for the first time... Please wait a moment."):
        subprocess.run([sys.executable, "ingest_resumes.py"])

# We import the agent AFTER loading dotenv to ensure API keys are available
from matching_agent import agent

# Custom CSS for a professional, high-tech, animated look
st.markdown("""
<style>
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background-color: #0B0F19;
        color: #E2E8F0;
    }
    .main-header {
        font-family: 'Inter', monospace;
        color: #38BDF8;
        font-weight: 700;
        letter-spacing: 1px;
        margin-bottom: -15px;
        animation: fadeIn 1s ease-in-out;
    }
    .sub-header {
        font-family: 'Inter', monospace;
        color: #94A3B8;
        font-size: 1rem;
        margin-bottom: 30px;
        animation: fadeIn 1.5s ease-in-out;
    }
    .stChatInputContainer {
        border-radius: 8px;
        border: 1px solid #1E293B;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.1);
        transition: box-shadow 0.3s ease;
    }
    .stChatInputContainer:focus-within {
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
    }
    .stMarkdown {
        animation: fadeIn 0.5s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">AI Resume Matcher Pro</h1>', unsafe_allow_html=True)

# Initialize chat history and thread id for memory in session state
if "thread_id" not in st.session_state:
    if "session_id" in st.query_params:
        st.session_state.thread_id = st.query_params["session_id"]
    else:
        st.session_state.thread_id = str(uuid.uuid4())
        st.query_params["session_id"] = st.session_state.thread_id

if "messages" not in st.session_state:
    history_path = f"history/{st.session_state.thread_id}.json"
    if os.path.exists(history_path):
        with open(history_path, "r") as f:
            st.session_state.messages = json.load(f)
    else:
        st.session_state.messages = [{"role": "assistant", "content": "System Initialized. Awaiting Job Description parameters for screening workflow."}]

# Save Session Helper
def save_session():
    if len(st.session_state.messages) > 1:
        os.makedirs("history", exist_ok=True)
        with open(f"history/{st.session_state.thread_id}.json", "w") as f:
            json.dump(st.session_state.messages, f)

with st.sidebar:
    st.markdown("<h2 style='color: #E2E8F0; font-family: monospace;'>AI Matcher Pro</h2>", unsafe_allow_html=True)
    st.markdown("---")
        
    with st.expander("Session History", expanded=True):
        os.makedirs("history", exist_ok=True)
        history_files = glob.glob("history/*.json")
        
        # Sort history files by modification time, newest first
        history_files.sort(key=os.path.getmtime, reverse=True)
        
        session_options = {}
        for f in history_files:
            try:
                # Get the last modified timestamp and format it
                mtime = os.path.getmtime(f)
                dt_str = datetime.fromtimestamp(mtime).strftime('%b %d, %H:%M')
                
                with open(f, "r") as json_file:
                    msgs = json.load(json_file)
                    # Find the first user message
                    user_msgs = [m["content"] for m in msgs if m["role"] == "user"]
                    if user_msgs:
                        snippet = user_msgs[0][:25].replace("\n", " ") + "..."
                        session_options[f] = f"{dt_str} | {snippet}"
                    else:
                        session_options[f] = f"{dt_str} | Empty Session"
            except:
                session_options[f] = os.path.basename(f)
                
        if not history_files:
            st.write("No past sessions.")
        else:
            for f, label in session_options.items():
                if st.button(label, key=f"load_{f}", use_container_width=True):
                    with open(f, "r") as json_file:
                        st.session_state.messages = json.load(json_file)
                        loaded_id = os.path.basename(f).replace(".json", "")
                        st.session_state.thread_id = loaded_id
                        st.query_params["session_id"] = loaded_id
                    st.rerun()
                    
        # Dynamically show Delete/Share buttons ONLY if the active session has content
        if len(st.session_state.messages) > 1:
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            if col1.button("🗑️ Delete", use_container_width=True):
                history_path = f"history/{st.session_state.thread_id}.json"
                if os.path.exists(history_path):
                    os.remove(history_path)
                st.session_state.thread_id = str(uuid.uuid4())
                st.query_params["session_id"] = st.session_state.thread_id
                st.session_state.messages = [{"role": "assistant", "content": "System Initialized. Awaiting Job Description parameters for screening workflow."}]
                st.rerun()
                
            if col2.button("📤 Share", use_container_width=True):
                st.toast("Link copied to clipboard! (Simulation)")
                
    with st.expander("System Instructions", expanded=True):
        st.markdown("1. Input Job Description constraints.\n2. Await vector screening analysis.\n3. Input iterative queries to refine search.")
        
    st.markdown("---")
    if st.button("Initialize New Session", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.query_params["session_id"] = st.session_state.thread_id
        st.session_state.messages = [{"role": "assistant", "content": "System Initialized. Awaiting Job Description parameters for screening workflow."}]
        st.rerun()



# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        content = message["content"]
        if message["role"] == "user":
            # Sanitize user input to prevent XSS
            content = html.escape(content).replace("\n", "<br>")
        st.markdown(content, unsafe_allow_html=True)

# React to user input
if prompt := st.chat_input("Enter parameters..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    
    # Add user message to UI chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare input for the LangGraph agent
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    input_state = {"messages": [HumanMessage(content=prompt)]}
    
    with st.spinner("Executing candidate retrieval..."):
        try:
            result_state = agent.invoke(input_state, config=config)
            output_messages = result_state.get("messages", [])
            
            if output_messages:
                last_msg = output_messages[-1]
                if isinstance(last_msg, AIMessage):
                    ai_response = last_msg.content
                else:
                    ai_response = str(last_msg.content)
            else:
                ai_response = "Execution complete. No specific report generated."
                
        except Exception as e:
            ai_response = f"**System Exception:** Execution aborted.\n```\n{str(e)}\n```"
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(ai_response, unsafe_allow_html=True)
    
    # Add assistant response to UI chat history
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    # Save session to history folder
    save_session()
