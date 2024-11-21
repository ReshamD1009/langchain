from langchain_postgres import PGVector
import os
from dotenv import load_dotenv
from utilities.pdf_embeddings import get_embedding_model
from utilities.pdf_embeddings import generate_embeddings

load_dotenv()

def establish_connection():
    connection = os.environ.get("DB_CONNECTION_URL")
    collection_name = os.environ.get("COLLECTION_NAME")
    embeddings = get_embedding_model()

    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection,
        use_jsonb=True,
    )
    return vector_store

def create_table_if_not_exists():
    """
    Create the necessary table for storing embeddings if it doesn't exist.
    """
    connection = os.environ.get("DB_CONNECTION_URL")
    if not connection:
        raise ValueError("Database connection URL is not set.")
    
    # SQL query to ensure the table and extension are set up
    table_creation_query = f"""
    CREATE TABLE IF NOT EXISTS {os.environ.get('COLLECTION_NAME')} (
        id SERIAL PRIMARY KEY,
        vector VECTOR(1536), -- Adjust dimensionality to match your embedding model
        metadata JSONB
    );
    """
    extension_query = "CREATE EXTENSION IF NOT EXISTS vector;"
    
    try:
        # Use PGVector's connection to execute raw SQL
        vector_store = establish_connection()
        with vector_store.connection.cursor() as cursor:
            cursor.execute(extension_query)
            cursor.execute(table_creation_query)
        print("Table and extension setup successfully.")
    except Exception as e:
        print(f"Error setting up the database table: {e}")

def store_embeddings():
    """
    Store embeddings into the database.
    """
    vector_store = establish_connection()
    data = generate_embeddings()  # Make sure this generates valid embeddings
    vector_store.add_documents(data)

def get_data(query):
    vector_store = establish_connection()
    docs = vector_store.similarity_search(query=query, k=1)
    return docs[0].page_content

def get_retriever():
    vector_store = establish_connection()
    retriever = vector_store.as_retriever()
    return retriever

if __name__ == "__main__":
    try:
        # Ensure table exists
        create_table_if_not_exists()
        
        # Store embeddings
        store_embeddings()
        print("Embeddings stored successfully.")
    except Exception as e:
        print(f"Error: {e}")
