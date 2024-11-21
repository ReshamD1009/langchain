# pdf_embeddings.py
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
import os

def generate_embeddings():
    # Path to your example.pdf in the 'assets' folder
    pdf_file = os.path.join(os.path.dirname(__file__), '..', 'assets', 'example.pdf')  # Relative path to example.pdf
    loader = PyPDFLoader(pdf_file)
    docs = loader.load()
    
    # Split the document into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    
    return splits

def get_embedding_model():
    model_name = "BAAI/bge-small-en"
    hf = HuggingFaceBgeEmbeddings(model_name=model_name)
    return hf



