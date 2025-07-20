import logging
from typing import Annotated

from fastapi import APIRouter, File, UploadFile, Form
from pydantic import BaseModel
from util.db_manager import create_db, connect_db
from RAG_files.RAG_input_and_storage import upload_docs_api, store_links_api
from fine_tuning.file_tune import fine_tune_create

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

router = APIRouter()


class Data(BaseModel):
    title: str | None = None
    data: str


@router.post('/rag/upload/link/')
async def upload_data(data: Data):
    sqlite_conn = None
    try:
        sqlite_conn = connect_db()  # Connect to the database
        create_db(sqlite_conn)  # Ensure the database table exists
        result = store_links_api(data.title, data.data, sqlite_conn)  # Store the link in the database
        return result
    except Exception as e:
        logger.error(f"Error uploading data: {e}\n\nError id : ETF-UID-13")
        return {"result": "There was an error uploading the data", "error_id": "ETF-UID-13"}
    finally:
        if sqlite_conn:
            sqlite_conn.close()  # Close the database connection


@router.post('/rag/upload/file/')
async def upload_doc(title: Annotated[str, Form()], file: UploadFile = File(...)):
    sqlite_conn = None
    try:
        sqlite_conn = connect_db()  # Connect to the database
        result = upload_docs_api(sqlite_conn, file, title)  # Store the file in the database
        return result
    except Exception as e:
        logger.error(f"Error uploading file: {e}\n\nError id : ETF-UID-12")
        return {"result": "There was an error uploading the file", "error_id": "ETF-UID-12"}
    finally:
        if sqlite_conn:
            sqlite_conn.close()  # Close the database connection


