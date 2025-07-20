import logging
import os.path
import re
import shutil
import sqlite3
import uuid

import bs4
from chromadb.config import Settings
from langchain_community.document_loaders import YoutubeLoader, word_document, WebBaseLoader, PyPDFLoader, TextLoader, \
    UnstructuredPowerPointLoader, UnstructuredCSVLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from Configuration_files import config

logger = logging.getLogger(__name__)

# Configure ChromaDB to use SQLite
Settings(chroma_db_impl="sqlite")


def doc_loader(filepath):
    """
    Load a document based on its filetype.
    """
    filetype = re.findall("\.(.*)", filepath)[0]
    if filetype == "pdf":
        loader = PyPDFLoader(file_path=filepath,extract_images=True)
    elif filetype == "docx":
        loader = word_document.UnstructuredWordDocumentLoader(file_path=filepath, mode="single")
    elif filetype == "pptx":
        loader = UnstructuredPowerPointLoader(file_path=filepath)
    elif filetype == "csv":
        loader = UnstructuredCSVLoader(file_path=filepath, errors='ignore')
    else:
        loader = TextLoader(file_path=filepath)
    return loader.load()


def webloader(web_link):
    """
    Load content from a web link. Handles YouTube and other web links.
    """
    bs4_strainer = bs4.SoupStrainer(class_=("post-title", "post-header", "post-content"))
    if "youtube" in web_link:
        loader = YoutubeLoader.from_youtube_url(youtube_url=web_link)
    else:
        loader = WebBaseLoader(web_paths=(web_link,), bs_kwargs={"parse_only": bs4_strainer})
    return loader.load()


def store_chromadb(text_chunks, reference):
    """
    Store document chunks in ChromaDB with their embeddings.
    """
    # Initialize ChatOpenAI and other necessary objects
    store_docs = Chroma.from_documents(documents=text_chunks, embedding=OpenAIEmbeddings(),
                                       persist_directory="chromadb_persist/",
                                       collection_name=f"document_embeddings_{reference}")
    store_docs.persist()


def store_links_api(title, web_link, sqlite_conn):
    """
    Store a web link and its processed data in the database.

    Parameters:
    title (str): Title of the web link.
    web_link (str): URL of the web link.
    sqlite_conn: SQLite connection object.

    Returns:
    dict: Result of the operation.
    """
    sqlite_cursor = sqlite_conn.cursor()  # Create a cursor object to interact with the database
    try:
        # Load the data from the web link
        loaded_data = webloader(web_link=web_link)
        # Generate a unique reference ID
        reference_id = str(uuid.uuid4())
        # Store the loaded data in the ChromaDB with the generated reference ID
        store_chromadb(loaded_data, reference_id)
        # Insert the web link data into the database
        sqlite_cursor.execute("INSERT INTO file_references (title, web_link, reference_id) VALUES (?, ?, ?)",
                              (title, web_link, reference_id))
        # Commit the transaction
        sqlite_conn.commit()
        return {"result": "web link added successfully!"}
    except (bs4.FeatureNotFound, ValueError) as e:
        logger.error(f"Error loading web link: {e}\n\nError id : RAG-FRT-194")
        return {"result": "Error, unable to store the data!", "error_id": "RAG-FRT-194"}
    except sqlite3.DatabaseError as e:
        logger.error(f"Database error: {e}\n\nError id : RAG-FRT-294")
        return {"result": "Error, unable to store the data!", "error_id": "RAG-FRT-294"}
    except Exception as e:
        logger.error(f"Unexpected error: {e}\n\nError id : RAG-FRT-102")
        return {"result": "Error, unable to store the data!", "error_id": "RAG-FRT-102"}


def upload_docs_api(sqlite_conn, file, title):
    """
    Upload a document, process its contents, and store the data in the database.

    Parameters:
    sqlite_conn: SQLite connection object.
    file: File object to be uploaded.
    title (str): Title of the document.

    Returns:
    dict: Result of the operation.
    """
    sqlite_cursor = sqlite_conn.cursor()  # Create a cursor object to interact with the database
    upload_dir = os.path.join(os.getcwd(), 'uploads')  # Define the upload directory

    # Create the upload directory if it doesn't exist
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Define the destination path for the uploaded file
    dest = os.path.join(upload_dir, file.filename)
    try:
        # Save the uploaded file to the destination path
        with open(dest, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Load the data from the uploaded file
        data = doc_loader(filepath=dest)
        # Generate a unique reference ID
        reference_id = str(uuid.uuid4())
        # Store the loaded data in the ChromaDB with the generated reference ID
        store_chromadb(data, reference_id)
        # Insert the file data into the database
        sqlite_cursor.execute("INSERT INTO file_references (title, file_name, reference_id) VALUES (?, ?, ?)",
                              (title, file.filename, reference_id))
        # Commit the transaction
        sqlite_conn.commit()
        return {"result": "file added successfully!"}
    except FileNotFoundError as e:
        logger.error(f"File not found error: {e}\n\nError id : RAG-FRT-105")
        return {"result": "Error! file cannot be processed", "error_id": "RAG-FRT-105"}
    except sqlite3.DatabaseError as e:
        logger.error(f"Database error: {e}\n\nError id : RAG-FRT-130")
        return {"result": "Error! file cannot be processed", "error_id": "RAG-FRT-130"}
    except Exception as e:
        logger.error(f"Unexpected error: {e}\n\nError id : RAG-FRT-452")
        return {"result": "Error! file cannot be processed", "error_id": "RAG-FRT-452"}
    finally:
        # Remove the file from the destination path
        os.remove(dest)
