from pprint import pprint
from typing import List
from typing_extensions import TypedDict
from langgraph_t.hallucination import router_hallucination
from langgraph_t.index import router_retriever
from langgraph_t.generate import router_generate
from langgraph_t.question_rewriter import router_question_rewriter
from langgraph_t.grade_answer import router_grade_answer
from langgraph_t.retrieval_grader import router_retrieval_grader
from langchain.schema import Document
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import END, StateGraph
from Configuration_files import config

attempts = 0


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents
    """

    question: str
    generation: str
    documents: List[str]


def retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updated state with retrieved documents
    """
    print("---RETRIEVE---")
    question = state["question"]

    # Retrieval
    documents = router_retriever().invoke(question)
    state["documents"] = documents
    return state


def generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updated state with generation
    """
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]

    # RAG generation
    generation = router_generate().invoke({"context": documents, "question": question})
    state["generation"] = generation
    return state


def grade_documents(state):
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updated state with filtered relevant documents
    """

    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]

    # Score each doc
    filtered_docs = []
    for d in documents:
        score = router_retrieval_grader().invoke(
            {"question": question, "document": d.page_content}
        )
        grade = score.binary_score
        if grade == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            continue

    state["documents"] = filtered_docs
    return state


def transform_query(state):
    """
    Transform the query to produce a better question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updated state with re-phrased question
    """

    print("---TRANSFORM QUERY---")
    question = state["question"]

    # Re-write question
    better_question = router_question_rewriter().invoke({"question": question})
    state["question"] = better_question
    return state


def web_search(state):
    """
    Web search based on the re-phrased question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updated state with web search results
    """
    web_search_tool = TavilySearchResults(k=2)
    print("---WEB SEARCH---")
    question = state["question"]

    # Web search
    docs = web_search_tool.invoke({"query": question})
    web_results = "\n".join([d["content"] for d in docs])
    web_results = Document(page_content=web_results)

    state["documents"] = [web_results]
    return state


### Edges ###

def decide_to_generate(state):
    """
    Determines whether to generate an answer, or re-generate a question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    global attempts
    print("---ASSESS GRADED DOCUMENTS---")
    filtered_documents = state["documents"]
    if not filtered_documents and attempts < 2:
        # All documents have been filtered as irrelevant, try re-generating a new query
        attempts += 1
        print("\n\nattempts : ", attempts)
        print("---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---")
        return "transform_query"
    elif not filtered_documents:
        # If attempts are 5 or more, go to web search
        print("---DECISION: ATTEMPTS EXCEEDED, PERFORM WEB SEARCH---")
        attempts = 0
        return "web_search"
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: GENERATE---")
        return "generate"


def grade_generation_v_documents_and_question(state):
    """
    Determines whether the generation is grounded in the document and answers question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for next node to call
    """

    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = router_hallucination().invoke(
        {"documents":documents,"generation": generation}
    )
    grade = score.binary_score

    # Check hallucination
    if grade == "yes":
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        # Check question-answering
        print("---GRADE GENERATION vs QUESTION---")
        score = router_grade_answer().invoke({"question": question, "generation": generation})
        grade = score.binary_score
        if grade == "yes":
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        pprint("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"


def create_graph():
    graph_builder = StateGraph(GraphState)

    # Define the nodes
    graph_builder.add_node("web_search", web_search)  # web search
    graph_builder.add_node("retrieve", retrieve)  # retrieve
    graph_builder.add_node("grade_documents", grade_documents)  # grade documents
    graph_builder.add_node("generate", generate)  # generate
    graph_builder.add_node("transform_query", transform_query)  # transform_query

    # Build graph
    graph_builder.set_entry_point("retrieve")
    graph_builder.add_edge("retrieve", "grade_documents")
    graph_builder.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {
            "transform_query": "transform_query",
            "generate": "generate",
            "web_search": "web_search",
        },
    )
    graph_builder.add_edge("transform_query", "retrieve")
    graph_builder.add_edge("web_search", "generate")
    graph_builder.add_conditional_edges(
        "generate",
        grade_generation_v_documents_and_question,
        {
            "not supported": "generate",
            "useful": END,
            "not useful": "transform_query",
        },
    )

    # Compile
    app = graph_builder.compile()
    return app
