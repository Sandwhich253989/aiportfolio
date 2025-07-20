### Retrieval Grader

# Importing necessary modules and classes
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from Configuration_files import config


# Data model definition using Pydantic BaseModel
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )


def router_retrieval_grader():
    # Initialize ChatOpenAI instance for language model (LLM)
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    # Configure LLM to produce structured output based on GradeDocuments model
    structured_llm_grader = llm.with_structured_output(GradeDocuments)

    # Define system prompt message for guiding the document relevance grading process
    system = """You are a grader assessing relevance of a retrieved document to a user question. \n 
        If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
        It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
        Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""

    # Create ChatPromptTemplate for structured prompting and responses
    grade_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),  # System message providing instructions
            ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
            # Placeholder for user input
        ]
    )

    # Construct the retrieval grading pipeline: prompt -> LLM -> output parser
    retrieval_grader = grade_prompt | structured_llm_grader

    # Return the configured retrieval grading pipeline
    return retrieval_grader
