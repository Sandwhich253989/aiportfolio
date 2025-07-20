### Hallucination Grader

# Importing necessary modules and classes
from langchain_core.outputs import generation
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import Field, BaseModel

# Importing configuration from a Configuration_files module
from Configuration_files import config


# Data model using Pydantic BaseModel for defining the structure of graded hallucinations
class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generation answer."""

    binary_score: str = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )


# Function definition for grading hallucinations in generated answers
def router_hallucination():
    # Initializing ChatOpenAI with a specific model and temperature setting
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    # Configuring the language model to output structured data defined by GradeHallucinations
    structured_llm_grader = llm.with_structured_output(GradeHallucinations)

    # Prompt template for collecting user inputs (set of facts and LLM generated answer)
    system = """You are a grader assessing whether an LLM generation is hallucinating or not. \n Give a binary score 
    'yes' or 'no'. 'Yes' means that the LLM model is not hallucinating in case if you think the model is 
    hallucinating , check whether the LLM generation is supported by a set of facts from the document provided . If 
    so , give a binary score of yes"""
    hallucination_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),  # System message presenting the grading task
            ("human", "documents: {documents} LLM generation: {generation}"),  # User input placeholder
        ]
    )

    # Chaining the hallucination grading process: prompting user, using LLM, and grading output
    hallucination_grader = hallucination_prompt | structured_llm_grader

    # Returning the configured hallucination grading pipeline
    return hallucination_grader
