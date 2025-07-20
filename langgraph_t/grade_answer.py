### Answer Grader

# Importing necessary modules and classes
from langchain_core.outputs import generation
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import Field, BaseModel

# Importing configuration from a Configuration_files module
from Configuration_files import config


# Data model using Pydantic BaseModel for defining the structure of graded answers
class GradeAnswer(BaseModel):
    """Binary score to assess whether an answer addresses a question."""

    binary_score: str = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )


# Function definition for grading answers
def router_grade_answer():
    # Initializing ChatOpenAI with a specific model and temperature setting
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    # Configuring the language model to output structured data defined by GradeAnswer
    structured_llm_grader = llm.with_structured_output(GradeAnswer)

    # Prompt template for collecting user inputs (question and LLM generated answer)
    system = """You are a grader assessing whether an answer addresses / resolves a question \n 
         Give a binary score 'yes' or 'no'. 'Yes' means that the answer resolves the question."""
    answer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),  # System message presenting the grading task
            ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),  # User input placeholder
        ]
    )

    # Chaining the answer grading process: prompting user, using LLM, and grading output
    answer_grader = answer_prompt | structured_llm_grader

    # Returning the configured answer grading pipeline
    return answer_grader
