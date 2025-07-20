# Question Re-writer

# Importing necessary modules and classes
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from Configuration_files import config


def router_question_rewriter():
    # Initialize ChatOpenAI instance for language model (LLM)
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    # Define system prompt message for guiding the question rewriting process
    system = """You a question re-writer that converts an input question to a better version that is optimized \n 
         for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning."""

    # Create ChatPromptTemplate for structured prompting and responses
    re_write_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),  # System message providing instructions
            (
                "human",
                "Here is the initial question: \n\n {question} \n Formulate an improved question.",
                # Placeholder for user input
            ),
        ]
    )

    # Construct the question rewriting pipeline: prompt -> LLM -> output parser
    question_rewriter = re_write_prompt | llm | StrOutputParser()

    # Return the configured question rewriting pipeline
    return question_rewriter
