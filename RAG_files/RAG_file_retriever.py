import logging
import sqlite3

from chromadb.config import Settings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.vectorstores import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from Configuration_files import config

logger = logging.getLogger(__name__)

# Configure ChromaDB to use SQLite
Settings(chroma_db_impl="sqlite")

store_session = {}


def retrieve_file_info(index, sqlite_conn):
    """
    Retrieve file information from the SQLite database using the given index.
    """
    try:
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute("SELECT title, file_name, web_link, reference_id FROM file_references WHERE id=?",
                              (index,))
        result = sqlite_cursor.fetchone()
        if result:
            title, file_name, web_link, reference_id = result
            return {"title": title, "file_name": file_name, "reference_id": reference_id} if web_link is None else {
                "title": title, "web_link": web_link,
                "reference_id": reference_id}
        else:
            raise ValueError("No record found for the given index.")
    except sqlite3.DatabaseError as e:
        logger.error(f"Database error: {e}\n\nError id : RAG-FRT-35")
        return {"Error": "Database error","error_id" : "RAG-FRT-35"}
    except Exception as e:
        logger.error(f"Unexpected error: {e}\n\nError id : RAG-FRT-36")
        return {"Error": "Unexpected error","error_id" : "RAG-FRT-36"}


def retrieve_documents(reference_id):
    """
    Retrieve document embeddings and metadata from ChromaDB using the reference ID.
    """
    try:
        vector_store = Chroma(persist_directory="chromadb_persist/", embedding_function=OpenAIEmbeddings(),
                              collection_name=f"document_embeddings_{reference_id}")
        return vector_store
    except Exception as e:
        logger.error(f"Error retrieving documents: {e}\n\nError id : ETF-DBE-10")
        raise


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    Retrieve chat message history for the given session ID.
    """
    if session_id not in store_session:
        store_session[session_id] = ChatMessageHistory()
    return store_session[session_id]


def create_history_aware_rag_chain(vector_store):
    """
    Create a vector store retriever from a document or web content and set up a conversational chain.
    """
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    retriever = vector_store.as_retriever(search_type="similarity")
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer and analyse "
        "the question. If you don't know the answer to the  question ,say that you "
        "don't know. Use five sentences maximum and keep the "
        "answer concise."
        "\n\n"
        "{context}"
    )

    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    question_answer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, question_answer_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    return conversational_rag_chain


def generate_answer_api(ref_id, question):
    store_session.clear()
    try:
        vector_store = retrieve_documents(ref_id)
        conversational_rag_chain = create_history_aware_rag_chain(vector_store)
        response = conversational_rag_chain.invoke({"input": question}, config={"configurable": {"session_id": ref_id}})
        return {"user_input": question, "genai_response": response["answer"]}
    except Exception as e:
        logger.error(f"Error generating answer: {e}\n\nerror id : RAG-FRT-40")
        return {"result": "Error generating answer","error_id" : "RAG-FRT-40"}
