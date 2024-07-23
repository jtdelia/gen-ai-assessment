# main.py: Building a Generative AI App

This Python file is the core of the application for the Google Building Generative AI Apps Assessment. It utilizes Flask to create a web application that interacts with Google Cloud services like Firestore, Vertex AI, and Gemini.

## Functionality

The `main.py` file implements the following:

1. **Flask App:** Sets up a basic Flask web application to handle user requests.
2. **Firestore Database:** Connects to a Firestore database to store and retrieve data.
3. **Vertex AI Vector Search:** Uses Vertex AI's vector search capabilities to find relevant information in the database.
4. **Gemini API:** Interacts with the Gemini API to generate responses based on user input and retrieved data.

## Key Functions

- **`search_vector_database(query)`:** This function takes a user query as input and searches the vector database for relevant information. It returns a list of documents that match the query.
- **`ask_gemini(query, context)`:** This function sends a query to the Gemini API, providing both the user's query and relevant context from the vector database. It returns the Gemini model's response.

## Running the Application

1. **Prerequisites:** Ensure you have the necessary libraries installed (see `requirements.txt`).
2. **Virtual Environment:** Create a virtual environment and activate it.
3. **Run:** Execute `python main.py` to start the Flask application.
4. **Access:** Access the application through `localhost:8080` in your browser.

## Completing the Assessment

To complete the assessment, you need to implement the `search_vector_database` and `ask_gemini` functions. The comments within the code provide guidance on how to do so.

## Customization

You can customize the application's behavior using the `config.yaml` file. This allows you to modify the application's title, subtitle, and the Gemini model's parameters like temperature, top_p, and top_k.

## Note

This is the finished assessment.  See README-orig.md for the original instructions.
