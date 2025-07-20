### Build Index

# Importing necessary modules and classes
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from RAG_files.RAG_input_and_storage import doc_loader, webloader
from Configuration_files import config
from util.db_manager import display_all_files_with_index
from langchain_community.vectorstores import Chroma as ChromaVectorStore
from RAG_files.RAG_file_retriever import retrieve_documents
import sqlite3


# Function to determine loader based on URL type (local file or web resource)
def loader(f):
    if "http" in f:
        return webloader(f)  # Load document from web
    else:
        return doc_loader(f)  # Load document from local file


# Function to retrieve document embeddings and metadata from Chroma vector stores
def get_doc_store(ref_ids):
    dt = []
    mt = []
    for ref_id in ref_ids:
        # Initialize Chroma vector store for document embeddings
        vector_store = Chroma(
            persist_directory=r"C:\Users\avane\PycharmProjects\aiportfolio\chromadb_persist",
            embedding_function=OpenAIEmbeddings(),
            collection_name=f"document_embeddings_{ref_id}"
        )
        # Retrieve documents and metadatas from the Chroma vector store
        dt.extend(vector_store.get()["documents"])
        mt.extend(vector_store.get()["metadatas"])
    return dt, mt


# Function to retrieve reference IDs for documents from SQLite database
def get_ref_ids():
    sqlite_conn = sqlite3.connect(r"sqlite3_db/file_references.db")
    ref_ids = []
    file_info = display_all_files_with_index(sqlite_conn)
    for i, j in file_info.items():
        if "file" not in j["reference_id"]:
            ref_ids.append(j["reference_id"])
    return ref_ids


# Function to build and return a retriever for document indexing
def router_retriever():
    # Set embeddings using OpenAIEmbeddings
    embd = OpenAIEmbeddings()
    # Load documents and metadata from Chroma vector stores based on reference IDs
    docs, metadata = get_doc_store(get_ref_ids())
    # Initialize RecursiveCharacterTextSplitter for splitting documents into chunks
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=500, chunk_overlap=0
    )

    # Create document splits using text splitter and provided documents with metadata
    doc_splits = text_splitter.create_documents(texts=docs, metadatas=metadata)

    # Initialize Chroma vector store from document splits with embeddings
    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        collection_name="rag-chroma",
        embedding=embd,
    )

    # Create and configure retriever for document indexing based on similarity
    retriever = vectorstore.as_retriever(search_type="similarity")

    # Return the configured retriever for further use
    return retriever
