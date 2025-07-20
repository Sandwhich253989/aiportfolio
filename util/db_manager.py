import os
import shutil
import sqlite3
import logging
import sys
from langchain_community.vectorstores import Chroma
import chromadb

logger = logging.getLogger(__name__)


def connect_db():
    """
    Connect to the SQLite database. If it doesn't exist, it will be created.
    """
    # Set up SQLite database for file references
    sqlite_conn = sqlite3.connect("sqlite3_db/file_references.db")
    sqlite_conn.commit()
    return sqlite_conn


def create_db(sqlite_conn):
    """
    Create the file_references table if it doesn't exist.
    """
    try:
        sqlite_cursor = sqlite_conn.cursor()
        # Create table query
        sqlite_cursor.execute(
            "CREATE TABLE IF NOT EXISTS file_references (id INTEGER PRIMARY KEY, title TEXT, file_name TEXT, "
            "web_link TEXT,"
            "reference_id TEXT)"
        )
        sqlite_conn.commit()
    except Exception:
        logger.exception("Error creating the table ")
        sqlite_conn.close()
        sys.exit(1)  # Exit the program if the table creation fails


def reset_db(sqlite_conn):
    """
    Reset the database by deleting all entries and their associated vector store collections.
    """
    try:
        sqlite_cursor = sqlite_conn.cursor()
        # Delete all records from the table
        sqlite_cursor.execute("DELETE FROM file_references")
        sqlite_conn.commit()

        ref_ids = []
        # Retrieve all records to get the reference IDs
        sqlite_cursor.execute("SELECT id, title, file_name, web_link, reference_id FROM file_references")
        rows = sqlite_cursor.fetchall()

        for row in rows:
            ref_ids.extend(row[4])

        # Delete corresponding collections in the vector store
        for ref_id in ref_ids:
            vector_store = Chroma(persist_directory="chromadb_persist", collection_name=f"document_embeddings_{ref_id}")
            vector_store.delete_collection()

        shutil.rmtree("chromadb_persist")

        return {"result": "Database reset successfully"}
    except Exception as e:
        logger.error(str(e))
        return {"result": "Error resetting the database","error_id" : "RAG-DBM-24"}


def display_all_files_with_index(sqlite_conn):
    """
    Display all files and web links stored in the SQLite database with their indices.
    """
    file_info = {}
    sqlite_cursor = sqlite_conn.cursor()
    # Select all records from the table
    sqlite_cursor.execute("SELECT id, title, file_name, web_link, reference_id FROM file_references")
    rows = sqlite_cursor.fetchall()
    # Process each row and prepare the output dictionary
    for row in rows:
        index, title, file_name, web_link, reference_id = row
        if file_name is None:
            file_info[f"index {index}"] = {"title": title, "web_link": web_link, "reference_id": reference_id}
        else:
            file_info[f"index {index}"] = {"title": title, "file_name": file_name, "reference_id": reference_id}
    return file_info


def delete_entry_from_db(index, sqlite_conn):
    """
    Delete an entry from the SQLite database and its associated vector store collection.
    """
    try:
        sqlite_cursor = sqlite_conn.cursor()
        # Retrieve the reference ID of the entry to be deleted
        sqlite_cursor.execute("SELECT reference_id FROM file_references WHERE id=?", (index,))
        ref_id = sqlite_cursor.fetchone()


        # Delete the corresponding collection in the vector store
        # vector_store = chromadb.PersistentClient(path="chromadb_persist")
        # vector_store.delete_collection(name=f"document_embeddings_{ref_id[0]}")
        vector_store = Chroma(persist_directory="chromadb_persist",collection_name=f"document_embeddings_{ref_id[0]}")
        vector_store.delete_collection()

        # Delete the record from the table
        sqlite_cursor.execute("DELETE FROM file_references WHERE id=?", (index,))
        sqlite_conn.commit()

        return {"result": "Entry deleted successfully"}
    except Exception as e:
        logger.error(str(e))
        return {"result": f"Error! entry with index: {index} does not exist","error_id" : "RAG-DBM-43"}
