from pprint import pprint  # Importing pprint for pretty-printing output

from langgraph_t.graph_route import create_graph  # Importing create_graph function from langgraph_t.graph_route


def generate_rag_answer(question):
    global value  # Declaring 'value' as a global variable

    # Creating a graph application instance using create_graph function
    app = create_graph()

    # Setting up inputs for the graph application
    inputs = {"question": question}

    # Iterating over outputs from the graph application
    for output in app.stream(inputs):
        for key, value in output.items():
            # Printing the node key using pprint for better readability
            pprint(f"Node '{key}':")

        # Printing a separator for readability
        pprint("\n---\n")

    # Printing the generated answer retrieved from the graph application's output
    print(value["generation"])

    # Returning a dictionary with the user question and the generated response
    return {"user": question,
            "srag - genai_response": value["generation"]}

