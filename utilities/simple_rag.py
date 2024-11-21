# simple_rag.py
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from utilities.chat_history import initialize_chat_history, add_message_to_history, get_recent_chat_history
from utilities.db_operations import get_retriever

def simple_rag_call(query, session_id=None):
    # Initialize chat history
    chat_history = initialize_chat_history(session_id)
    add_message_to_history(chat_history, "human", query)
    
    # Retrieve the most recent chat history
    recent_messages = get_recent_chat_history(chat_history)
    
    # Get the retriever for searching embeddings in the database
    retriever = get_retriever()

    # Format the documents to send to the model
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    # Define the system and prompt for the LLM
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant. Use the following context to answer the question, "
                  "taking into account the chat history if relevant: {context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ])
    
    # Define the language model (Groq)
    llm = ChatGroq(model="llama3-8b-8192")

    # Build the RAG chain
    rag_chain = (
        {
            "context": retriever | format_docs,
            "chat_history": lambda _: recent_messages,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # Invoke the RAG chain and get the result
    result = rag_chain.invoke(query)
    
    # Add the response to the chat history
    add_message_to_history(chat_history, "ai", result)
    
    return result, chat_history.messages, chat_history._session_id
