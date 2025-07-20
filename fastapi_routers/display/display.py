from fastapi import APIRouter
from util.db_manager import connect_db, display_all_files_with_index
from RAG_files.RAG_file_retriever import retrieve_file_info
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get('/rag/display/display-all-files/')
async def get_all_files():
    sqlite_conn = None
    try:
        sqlite_conn = connect_db()  # Connect to the database
        result = display_all_files_with_index(sqlite_conn)  # Retrieve and display all files and links
        return result
    except Exception as e:
        logger.error(f"Error displaying all files: {e}\n\nError id : ETF-DPY-2")
        return {"result": "There was an error displaying all files", "error_id": "ETF-DPY-2"}
    finally:
        if sqlite_conn:
            sqlite_conn.close()  # Close the database connection


@router.get('/rag/display/retrieve-file/')
async def retrieve_file(index):
    sqlite_conn = None
    try:
        sqlite_conn = connect_db()  # Connect to the database
        result = retrieve_file_info(index, sqlite_conn)  # Retrieve the file/link information
        return result
    except Exception as e:
        logger.error(f"Error retrieving file: {e}\n\nError id : ETF-DPY-5")
        return {"result": "There was an error retrieving the file", "error_id": "ETF-DPY-5"}
    finally:
        if sqlite_conn:
            sqlite_conn.close()  # Close the database connection
