### Generate
# Importing necessary modules and classes from langchain and other packages
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Importing configuration from a Configuration_files module
from Configuration_files import config


# Function definition for generating a response chain
def router_generate():
    # Prompt template for generating responses
    prompt = """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. 
                If you don't know the answer, just say that you don't know. Use 5 sentences maximum and keep the answer concise.
                Question: {question} 
                Context: {context} Answer:
                """

    # Creating a ChatPromptTemplate object using predefined messages
    system_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),  # System message with the predefined prompt
            ("human", "{context}"),  # Human message placeholder for context
            ("human", "User question: \n\n {question}"),  # Human message placeholder for user question
        ]
    )

    # Initializing a ChatOpenAI object for interaction with OpenAI's language model
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    # Chaining components together: system prompt, OpenAI model, and output parser
    rag_chain = system_prompt | llm | StrOutputParser()

    # Returning the chained response generator
    return rag_chain
