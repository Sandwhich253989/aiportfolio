import shutil
import os
import openai
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from RAG_files.RAG_file_retriever import retrieve_file_info, logger


def fine_tune_create(sqlite_conn, file, title):
    """
    Upload a file for fine-tuning an OpenAI model and store reference in the database.
    """
    dest = None
    openfile = None
    try:
        sqlite_cursor = sqlite_conn.cursor()  # Create a cursor object to interact with the database
        upload_dir = os.path.join(os.getcwd(), 'uploads')  # Define the upload directory

        # Create the upload directory if it doesn't exist
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Define the destination path for the uploaded file
        dest = os.path.join(upload_dir, file.filename)
        # Save the uploaded file to the destination path
        with open(dest, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        openfile = open(dest, "rb")  # Open the uploaded file for reading
        # Upload the file to OpenAI for fine-tuning
        fine_tune_file = openai.files.create(file=openfile, purpose='fine-tune')

        # Insert file reference into the database
        sqlite_cursor.execute("INSERT INTO file_references (title, file_name, reference_id) VALUES (?, ?, ?)",
                              (title, file.filename, fine_tune_file.id))
        sqlite_conn.commit()
        return {"result": "File uploaded for fine-tuning job successfully", "file_id": fine_tune_file.id}

    except Exception as e:
        logger.error(f"fine_tune_create: Error uploading file: {e}\n\nError id : ETF-FTL-55")
        return {"result": "There was an error uploading the file", "error_id": "ETF-FTL-55"}

    finally:
        if openfile:
            openfile.close()
        if dest and os.path.exists(dest):
            shutil.rmtree(os.path.dirname(dest))


def fine_tune_train(file_id):
    """
    Start a fine-tuning job with the specified file ID.
    """
    try:
        job = openai.fine_tuning.jobs.create(training_file=file_id, model="gpt-3.5-turbo")
        return {"result": "Started training", "details": job}

    except Exception as e:
        logger.error(f"fine_tune_train: Error starting fine-tuning job: {e}\n\nError id : ETF-FTJ-56")
        return {"result": "There was an error starting the fine-tuning job", "error_id": "ETF-FTJ-56"}


def fine_tune_retrieve_status(file_id):
    """
    Retrieve the status of a fine-tuning job.
    """
    try:
        job = openai.fine_tuning.jobs.retrieve(fine_tuning_job_id=file_id)
        return {"result": job}

    except Exception as e:
        logger.error(
            f"fine_tune_retrieve_status: Error retrieving fine-tuning job status: {e}\n\nError id : ETF-FTR-57")
        return {"result": "There was an error retrieving the job status", "error_id": "ETF-FTR-57"}


def generate_answer_from_model(model_name, question):
    """
    Generate an answer to a question using a fine-tuned model.
    """
    try:
        parser = StrOutputParser()
        model = ChatOpenAI(model=model_name)

        system_template = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer and analyse "
            "the question. If you don't know the answer to the question, say that you "
            "don't know. Use five sentences maximum and keep the "
            "answer concise."
        )
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", system_template), ("user", "{text}")]
        )

        chain = prompt_template | model | parser

        return {"user_input": question, "genai_response": chain.invoke(question)}

    except Exception as e:
        logger.error(f"generate_answer_from_model: Error generating answer: {e}\n\nError id : ETF-GAM-58")
        return {"result": "There was an error generating the answer", "error_id": "ETF-GAM-58"}
