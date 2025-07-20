from typing import Annotated

from fastapi import APIRouter, UploadFile, Form, File
import logging
from fine_tuning.file_tune import fine_tune_create, fine_tune_train, fine_tune_retrieve_status, \
    generate_answer_from_model
from util.db_manager import connect_db

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


@router.post('/fine-tune/upload/')
async def upload_doc_ft(title: Annotated[str, Form()], file: UploadFile = File(...)):
    sqlite_conn = None
    try:
        sqlite_conn = connect_db()
        result = fine_tune_create(sqlite_conn, file, title)
        return result
    except Exception as e:
        logger.error(f"Error uploading file: {e}\n\nError id : ETF-FTL-43")
        return {"result": "There was an error uploading the file", "error_id": "ETF-FTL-43"}
    finally:
        if sqlite_conn:
            sqlite_conn.close()  # Close the database connection


@router.get('/fine-tune/train/')
async def train(file_id):
    sqlite_conn = None
    try:
        sqlite_conn = connect_db()
        return fine_tune_train(file_id)
    except Exception as e:
        logger.error(f"Error uploading file: {e}\n\nError id : ETF-FTL-96")
        return {"result": "There was an error", "error_id": "ETF-FTL-34"}
    finally:
        if sqlite_conn:
            sqlite_conn.close()  # Close the database connection


@router.get('/fine-tune/retrieve-status')
async def retrieve(file_id):
    sqlite_conn = None
    try:
        sqlite_conn = connect_db()
        return fine_tune_retrieve_status(file_id)
    except Exception as e:
        logger.error(f"Error retrieving the status of file: {e}\n\nError id : ETF-FTL-96")
        return {"result": "There was an error", "error_id": "ETF-FTL-96"}
    finally:
        if sqlite_conn:
            sqlite_conn.close()  # Close the database connection


@router.get('/fine-tune/generate-answer/{model}')
async def generate(model, question):
    try:
        result = generate_answer_from_model(model, question)
        return result
    except Exception as e:
        logger.error(f"Error generating answer : {e}\n\nError id : ETF-FTL-193")
        return {"result": "Error generating answer", "error_id": "ETF-FTL-193"}
