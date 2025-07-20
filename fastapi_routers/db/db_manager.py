from fastapi import APIRouter
from util.db_manager import connect_db, delete_entry_from_db, reset_db
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
router = APIRouter()


@router.delete('/rag/db/delete-entry-from-db/')
async def delete_entry(index):
    sqlite_conn = None
    try:
        sqlite_conn = connect_db()  # Connect to the database
        result = delete_entry_from_db(index, sqlite_conn)  # Delete the entry from the database
        return result
    except Exception as e:
        logger.error(f"Error deleting entry: {e}\n\nError id : ETF-DBE-10")
        return {"result": "There was an error deleting the entry","error_id":"ETF-DBE-10"}
    finally:
        if sqlite_conn:
            sqlite_conn.close()  # Close the database connection


@router.delete('/rag/db/reset-db')
async def resetdb():
    sqlite_conn = None
    try:
        sqlite_conn = connect_db()  # Connect to the database
        result = reset_db(sqlite_conn)  # Reset the database
        return result
    except Exception as e:
        logger.error(f"Error resetting database: {e}\n\nError id : ETF-DBE-8")
        return {"result": "There was an error resetting the database","error_id":"ETF-DBE-8"}
    finally:
        if sqlite_conn:
            sqlite_conn.close()  # Close the database connection
