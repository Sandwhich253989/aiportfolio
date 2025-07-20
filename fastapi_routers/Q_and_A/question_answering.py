from fastapi import APIRouter
from RAG_files.RAG_file_retriever import generate_answer_api
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get('/rag/generate-answer/{ref_id}')
async def generate(ref_id, question):
    try:
        result = generate_answer_api(ref_id, question)  # Generate the answer using the RAG model
        return result
    except Exception as e:
        logger.error(f"Error generating answer: {e}\n\nError id : ETF-GAI-1")
        return {"result": "There was an error generating the answer", "error_id": "ETF-GAI-1"}
