from fastapi import APIRouter
from langgraph_t.main import generate_rag_answer
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get('/srag/generate/')
async def generate(question):
    try:
        result = generate_rag_answer(question)
        return result
    except Exception as e:
        logger.error(f"Error generating answer: {e}\n\nError id : ETF-RAG-482")
        return {"result": "There was an error generating the answer", "error_id": "ETF-GAI-482"}
