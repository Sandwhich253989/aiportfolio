# aiportfolio

# Overview
This project provides functionalities to manage and retrieve documents and web links using a Retrieval-Augmented Generation (RAG) model. It allows you to upload documents, store web links, retrieve stored data, and generate answers based on the content of stored documents and links. The data is stored in an SQLite database, and embeddings are persisted using ChromaDB.

---
##  Features

|     | Feature           | Description                                                                                                                                            |
|-----|-------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| ⚙️  | **Architecture**  | The project employs a FastAPI-based architecture for API endpoints, supported by a SQLite and ChromaDB for data storage and retrieval.                 |
| 🔩  | **Code Quality**  | Adheres to Python coding standards, employs efficient error logging, and structured exception handling across modules. Code is modular and readable.   |
| 📄  | **Documentation** | Contains sufficiently descriptive docstrings and inline comments explaining the code logic, though external user-facing documentation is limited.      |
| 🔌  | **Integrations**  | Integrates with OpenAI and LangChain via configuration files to facilitate API interactions. Uses Tkinter for GUI elements.                            |
| 🧩  | **Modularity**    | Highly modular with distinct files for different responsibilities (e.g., API endpoints, database management, file upload UI), promoting reusability.   |
| 🧪  | **Testing**       | No explicit details on testing frameworks, but robust error logging and handling suggest consideration for reliability and debugging.                  |
| ⚡️  | **Performance**   | Efficient in handling API requests and database retrievals; uses embeddings for fast query responses; performance tuning appears to be in place.       |
| 🛡️ | **Security**      | Uses environment variables for API key protection; however, further information on access control and data encryption is not provided.                 |
| 📦  | **Dependencies**  | Relies on external libraries: `py`, `python`, `FastAPI`, `OpenAI`, `LangChain`, `Tkinter`, and database interfaces (SQLite, ChromaDB).                 |
| 🚀  | **Scalability**   | Designed to handle multiple document types and web links; depends on the efficiency of backend databases for scalability; FastAPI aids in scalability. |

---

# Capabilities

## Document and Web Link Storage:

Upload various document types (PDF, DOCX, PPTX, TXT) and store their content.
Store web links and retrieve their content.
Store data in an SQLite database with embeddings persisted in ChromaDB.

## Data Retrieval and Question Answering:

Retrieve stored documents and web links using their reference ID.
Generate answers to questions based on the content of stored documents and links using a history-aware RAG model.

## Database Management:

Display all stored files and web links with their indices.
Delete specific entries from the database.
Reset the database and clear the vector store.

## Fine Tuning with OpenAI:

The API's provide easy way to fine tune datasets with openai models. 

---
# Getting Started
## Prerequisites
1. Python 3.7+
2. Required Python packages listed in requirements.txt
   
## Installation
Clone the repository

```git
git clone https://github.com/yourusername/your-repo.git
```
Install dependencies
   
```cmd
pip install -r requirements.txt
```
Set up the SQLite database:

```cmd 
python -c "from util.db_manager import connect_db, create_db; conn = connect_db(); create_db(conn); conn.close()"
```

## Running the Application
### 1. Start the FastAPI application:
```
fastapi run ./main.py
```
### 2. Access the API documentation:
Open your browser and navigate to http://127.0.0.1:8000/docs to view and interact with the API endpoints.
___


# API Endpoints
___

## Root Endpoint
### `GET /`
  Returns a simple message indicating the API is running

___
## 1. Upload web content using link
- **URL:** `http://localhost:8000/requirements/rag/upload/link`
- **Method:** `POST`
- **Description:** Upload a web link and store its data.
- **Request Body:** (raw json)
  ```json
  {
      "title": "lliam Github",
      "data": "https://lilianweng.github.io/posts/2023-06-23-agent/"
  }
  ```
- **Sample Output Response:**
  ```json
  {"result": "web link added successfully!"}
  ```

## 2. Display all files
- **URL:** `http://localhost:8000/rag/display/display-all-files`
- **Method:** `GET`
- **Description:** Display all the files stored in the system.
- **Request Body:** None
- **Sample Response:**
  ```json
  {
      "index 1": {
          "title": "airlines_review_final",
          "file_name": "plane_final.csv",
          "reference_id": "a7f6ccbf-1a98-4d64-9b60-46ef0fa2af7e"
      },
      "index 2": {
          "title": "sentiment_analysis",
          "file_name": "train.csv",
          "reference_id": "5ab44e24-b2a0-4c80-8553-93a3dcadf7a6"
      },
      "index 3": {
          "title": "degree audit",
          "file_name": "Degree Audit.pdf",
          "reference_id": "b7497b1b-e70a-4ebc-8a62-b7d9e2a1e5a4"
      },
      "index 4": {
          "title": "Machine learning",
          "file_name": "conversation.json",
          "reference_id": "file-KFmYuVZK0zajhcajAsmXWOWf"
      },
      "index 5": {
          "title": "Fine_tuning_test1",
          "file_name": "whatis2plus2.json.json",
          "reference_id": "file-7I82PYyNWNu9B8cp7uwWn5sE"
      },
      "index 6": {
          "title": "offer letter",
          "file_name": "OFFER LETTER -IMPELOX TECH- AVANESH SATHISHKUMAR.pdf",
          "reference_id": "456169ca-8e9d-4ddd-8d54-e657fc4ba5f2"
      },
      "index 7": {
          "title": "hiring",
          "file_name": "hiring (1).csv",
          "reference_id": "32105a86-8507-4312-875e-702639531485"
      },
      "index 8": {
          "title": "hr",
          "file_name": "hr_with_ids.csv",
          "reference_id": "944f89c0-f122-46c2-b0f8-8d7f010f7a9b"
      }
  }
  ```

## 3. Retrieve file details from database with index
- **URL:** `http://localhost:8000/rag/display/retrieve-file?index={index}`
- **Method:** `GET`
- **Description:** Retrieve the details of a file from the database using its index.
- **Request Body:** 
  - **Query Parameters:**
    - `index`: The index of the file in the database.
- **Sample Input:**:
  ```http request
   http://localhost:8000/rag/display/retrieve-file?index=1 
  ```
- **Sample Response:**
  ```json
  {
      "title": "airlines_review_final",
      "file_name": "plane_final.csv",
      "reference_id": "a7f6ccbf-1a98-4d64-9b60-46ef0fa2af7e"
  }
  ```

## 4. Generate answer from question and ref id
- **URL:** `http://localhost:8000/rag/generate-answer/{ref_id}/?question={question}`
- **Method:** `GET`
- **Description:** Generate an answer based on the provided question and reference ID.
- **Request Body:** 
  - **Query Parameters:**
    - `question`: The question to be answered.
  - **Path Parameters:**
    - `ref_id`: The reference id of the file
- **Sample Response:**
  ```json
  {
      "user_input": "what does this dataset talk abt",
      "genai_response": "This dataset appears to include information about individuals' work experience, test scores, interview scores, and corresponding salaries. The data seems to represent a sample of individuals with varying levels of experience, test scores, and interview scores, along with their associated salaries. The dataset may be used to analyze the relationship between experience, test scores, interview scores, and salary levels. It provides a snapshot of how these factors may influence the salaries of individuals in a hypothetical scenario."
  }
  ```

## 5. Upload files
- **URL:** `http://localhost:8000/rag/upload/file/`
- **Method:** `POST`
- **Description:** Upload a file to the system.
- **Request Body:**
  - **Form Data:**
    - `title`: The title of the file.
    - `file`: The file to be uploaded.
  - **Reponse Output:**
    ```json
      {"result": "file added successfully!"}
    ```

## 6. Delete entry from db using index
- **URL:** `http://localhost:8000/rag/db/delete-entry-from-db/?index={index}`
- **Method:** `DELETE`
- **Description:** Delete an entry from the database using its index.
- **Request Body:** None
- **Query Parameters:**
  - `index`: The index of the entry to be deleted.
- **Sample Input:**
  ```http request
  http://localhost:8000/rag/db/delete-entry-from-db/?index=2
  ```
- **Sample Response:**
  ```json
  {
      "result": "Entry deleted successfully"
  }
  ```

## 7. Reset db
- **URL:** `http://localhost:8000/rag/db/reset-db`
- **Method:** `DELETE`
- **Description:** Reset the database.
- **Request Body:** None
- **Sample Response:**
  ```json
  {
      "result": "Database reset successfully"
  }
  ```

## 8. Feedback analysis
- **URL:** `http://localhost:8000/rag/generate-answer/{ref_id}/?question={question}`
- **Method:** `GET`
- **Description:** Perform feedback analysis based on the provided question.
- **Request Body:** None
- **Query Parameters:**
  - `question`: The question to be analyzed.
- **Path Parameters:**
  - `ref_id`: The reference ID of the file
- **Sample Input:**
  ```http request
  http://localhost:8000/rag/generate-answer/a7f6ccbf-1a98-4d64-9b60-46ef0fa2af7e/?question="Do you see a pattern with the delays in the flight with the route where it goes?"
  ```
- **Sample Response:**
  ```json
  {
      "user_input": "Do you see a pattern with the delays in the flight with the route where it goes?",
      "genai_response": "There is a pattern of delays in flights with AirAsia, especially when it comes to flights departing from or arriving at Kuala Lumpur. The delays seem to be a common occurrence on various routes, such as Langkawi to Kuala Lumpur, Penang to Kuala Lumpur, and Hanoi to Bangkok. These delays can be up to 2 hours or more, causing inconveniences to passengers. The delays are often attributed to operational circumstances or heavy air traffic over Kuala Lumpur. In some cases, the delays are communicated last minute, leading to frustrations among passengers."
  }
  ```

## 9. Sentiment analysis
- **URL:** `http://localhost:8000/rag/generate-answer/{ref_id}/?question={question}`
- **Method:** `GET`
- **Description:** Perform sentiment analysis based on the provided question.
- **Request Body:**
  - **Query Parameters:**
    - `question`: The question to be analyzed.
  - **Path Parameters:**
    - `ref_id`: The reference id of the file
- **Sample Input:**
  ```http request
  http://localhost:8000/rag/generate-answer/a7f6ccbf-1a98-4d64-9b60-46ef0fa2af7e/?question="Can you group the reviews into categories based on the context they are tweeting about and understand if they will use the service again or not"
   ```
- **Sample Response:**
  ```json
  {
    "user_input": "\"Can you group the reviews into categories based on the context they are tweeting about and understand if they will use the service again or not\"",
    "genai_response": "Based on the context of the reviews, they can be grouped into two categories:\n\n1. **Positive Experience and Likely to Use Again:**\n   - Reviews that mention smooth check-in, punctuality, and professionalism of staff.\n   - Mention of good value for money, efficient service, and overall satisfaction with the flight experience.\n   - Willingness to fly with AirAsia again due to a positive experience.\n\n2. **Negative Experience and Unlikely to Use Again:**\n   - Reviews expressing frustration with delays, poor customer service, and lack of communication.\n   - Complaints about flight cancellations, issues with refunds, and difficulty in reaching customer service.\n   - Unpleasant experiences related to booking, boarding, baggage handling, and overall service quality.\n   - Unlikelihood of using AirAsia again due to the negative encounters.\n\nThese categories provide an insight into the different sentiments and experiences shared by customers, indicating whether they are inclined to use the service again or not based on their interactions with AirAsia."
  }
  ```

## 10. Upload fine-tuning files
- **URL:** `http://localhost:8000/fine-tune/upload/`
- **Method:** `POST`
- **Description:** Upload files for fine-tuning with OpenAI.
- **Request Body:**
  - **Form Data:**
    - `title`: The title of the fine-tuning file.
    - `file`: The file to be uploaded for fine-tuning.


- **Sample Response:**
  ```json
  {
  "result": "File uploaded for fine-tuning job successfully", 
  "file_id": "file-7I82PYyNWNu9B8cp7uwWn5sE"
  }
  ```

## 11. Train uploaded fine-tuning files with file id
- **URL:** `http://localhost:8000/fine-tune/train?file_id={file_id}`
- **Method:** `GET`
- **Description:** Train the model using the uploaded fine-tuning file with the specified file ID.
- **Request Body:** None
  - **Query Parameters:**
    - `file_id`: The ID of the file to be used for training.
- **Sample Response:**
  ```json
  {"result": "Started training", "details": job} 
  ```

## 12. Retrieve status of model training
- **URL:** `http://localhost:8000/fine-tune/retrieve-status?file_id={file_job_id}`
- **Method:** `GET`
- **Description:** Retrieve the status of the fine-tuning job
- **Request Body:** None
  - **Query Parameters:**
    - `file_job_id`: The ID of the fine-tuning job
- **Sample Response:**
  ```json
  {"result": job}
  ```

## 13. Generate Answer from fine-tuned model
- **URL:** `http://localhost:8000/fine-tune/generate-answer/{fine_tuned_model_id}/?question={question}`
- **Method:** `GET`
- **Description:** Generate the answer from the fine-tuned model
- **Request Body:** None
  - **Query Parameters:**
    - `question`: question
  - **Path Parameters:**
    - `fine_tuned_model_id`: The ID of the fine-tuned model
- **Sample Input:**
  ```http request
  http://localhost:8000/fine-tune/generate-answer/ft:gpt-3.5-turbo-0125:impelox-tech-pvt-ltd::9b7Ksdoa/?question="advantage of CNNS"
  ```
- **Sample Response:**
  ```json
  {
    "user_input": "\"advantage of CNNS\"",
    "genai_response": "Convolutional Neural Networks (CNNs) have an advantage in image recognition tasks due to their ability to automatically learn spatial hierarchies of features. This is achieved through the application of convolutional filters that detect patterns at different spatial positions. CNNs are also able to reduce the number of parameters by sharing weights across the network, which can lead to better generalization. Another advantage of CNNs is their ability to handle input data of varying sizes, thanks to the use of pooling layers that downsample the input. Additionally, the hierarchical structure of CNNs allows them to capture increasingly complex features as the network goes deeper."
  }
  ```

## 14. Generate answer from langgraph
- **URL:** `http://localhost:8000/srag/generate/?question={question}`
- **Method:** `GET`
- **Description:** Generates answer with langgraph using SRAG - It tries to generate answer from documents and if not there , it uses web search to retrieve the answer.
- **Request Body:** None
  - **Query Parameters:**
    - `question`: question
- **Sample Input:**
  ```http request
  http://localhost:8000/srag/generate/?question="what is degree audit?"
  ```
- **Sample Response:**
  ```json
  {
    "user": "\"what is the grade for Linear algebra for computing? \"",
    "srag - genai_response": "The grade for Linear Algebra for Computing is A+ based on the retrieved information from the Degree Audit document."
  }
  ```


## Contributing
### Fork the repository.
> Create a new branch: git checkout -b my-feature-branch
> Commit your changes: git commit -m 'Add some feature'
> Push to the branch: git push origin my-feature-branch
> Create a Pull Request

# License
=======
This project is licensed under the MIT License. See the LICENSE file for details.
