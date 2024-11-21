# chat_history.py
import psycopg
import uuid
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_postgres import PostgresChatMessageHistory
from dotenv import load_dotenv
import os 

load_dotenv()

def initialize_chat_history(session_id=None):
    connection = os.environ.get("DB_CONNECTION_URL_2")
    table_name = "chat_history"
    
    sync_connection = psycopg.connect(connection)
    PostgresChatMessageHistory.create_tables(sync_connection, table_name)
    
    if session_id is None:
        session_id = str(uuid.uuid4())
    
    chat_history = PostgresChatMessageHistory(
        table_name,
        session_id,
        sync_connection=sync_connection
    )
    
    return chat_history

def get_recent_chat_history(chat_history):
    messages = chat_history.messages[-5:] if len(chat_history.messages) > 5 else chat_history.messages
    return messages

def add_message_to_history(chat_history, role, content):
    if role == "system":
        message = SystemMessage(content=content)
    elif role == "ai":
        message = AIMessage(content=content)
    elif role == "human":
        message = HumanMessage(content=content)
    else:
        raise ValueError("Invalid role specified")
    
    chat_history.add_message(message)
