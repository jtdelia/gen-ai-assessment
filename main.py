import os
import yaml
from flask import Flask, render_template, request

import firebase_admin
#rom firebase_admin import firestore
from google.cloud import firestore

from google.cloud import aiplatform

import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

from langchain_community.embeddings import VertexAIEmbeddings

## Set up 
PROJECT_ID = "johnd-test-01"
LOCATION = "us-central1"

# Instantiating the Firebase client
#firebase_app = firebase_admin.initialize_app()
db = firestore.Client()

# Instantiate an embedding model here
embedding_model = None

# Set up Vertex AI Embeddings
embeddings = VertexAIEmbeddings(
    model_name="textembedding-gecko@002",
    project=PROJECT_ID,
    location=LOCATION,
)


# Instantiate a Generative AI model here
gen_model = None

# Helper function that reads from the config file. 
def get_config_value(config, section, key, default=None):
    """
    Retrieve a configuration value from a section with an optional default value.
    """
    try:
        return config[section][key]
    except:
        return default

# Open the config file (config.yaml)
with open('config.yaml') as f:
    config = yaml.safe_load(f)

# Read application variables from the config fle
TITLE = get_config_value(config, 'app', 'title', 'Ask Google')
SUBTITLE = get_config_value(config, 'app', 'subtitle', 'Your friendly Bot')
CONTEXT = get_config_value(config, 'palm', 'context',
                           'You are a bot who can answer all sorts of questions')
BOTNAME = get_config_value(config, 'palm', 'botname', 'Google')
TEMPERATURE = get_config_value(config, 'palm', 'temperature', 0.8)
MAX_OUTPUT_TOKENS = get_config_value(config, 'palm', 'max_output_tokens', 256)
TOP_P = get_config_value(config, 'palm', 'top_p', 0.8)
TOP_K = get_config_value(config, 'palm', 'top_k', 40)


app = Flask(__name__)

# The Home page route
@app.route("/", methods=['POST', 'GET'])
def main():

    # The user clicked on a link to the Home page
    # They haven't yet submitted the form
    if request.method == 'GET':
        question = ""
        answer = "Hi, I'm FreshBot. How may I be of assistance to you?"

    # The user asked a question and submitted the form
    # The request.method would equal 'POST'
    else: 
        question = request.form['input']

        # Get the data to answer the question that 
        # most likely matches the question based on the embeddings
        data = search_vector_database(question)

        # Ask Gemini to answer the question using the data 
        # from the database
        answer = ask_gemini(question, data)
        
    # Display the home page with the required variables set
    model = {"title": TITLE, "subtitle": SUBTITLE,
             "botname": BOTNAME, "message": answer, "input": question}
    return render_template('index.html', model=model)


def search_vector_database(question):

    # 1. Convert the question into an embedding
    embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@002")
    embedding = embedding_model.get_embeddings([question])
    embedding_vector = embedding[0].values
    

    # 2. Search the Vector database for the 5 closest embeddings to the user's question

    # change these in the lab
    API_ENDPOINT="2135746267.us-central1-306419495665.vdb.vertexai.goog"
    INDEX_ENDPOINT="projects/306419495665/locations/us-central1/indexEndpoints/7004773076281851904"
    DEPLOYED_INDEX_ID="vs_quickstart_deployed_07051559"

    my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
        index_endpoint_name=INDEX_ENDPOINT
    )

    search_response = my_index_endpoint.find_neighbors(
    deployed_index_id = DEPLOYED_INDEX_ID,
    queries = [embedding_vector],
    num_neighbors = 5
    )

    print (search_response)

    # 3. Get the IDs for the five embeddings that are returned
    for idx, neighbor in enumerate(search_response[0]):
      print(f"{neighbor.id}") 

    data = search_response
    id_list = [neighbor.id for neighbor_list in data for neighbor in neighbor_list]

    print(id_list)


    # 4. Get the five documents from Firestore that match the IDs

    collection_ref = db.collection("page_content")

    docs =[]
    embedding_ids = id_list
    for doc_id in embedding_ids:
        doc_ref = db.collection('page_content').document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            docs.append(doc.to_dict())

    # 5. Concatenate the documents into a single string and return it
    data = ""
    for doc in docs:
        data += doc['text'] + "\n"

    print (data)
    return data



def ask_gemini(question, data):
    # You will need to change the code below to ask Gemni to
    # answer the user's question based on the data retrieved
    # from their search
    #response = "Not implemented!"

    prompt = """
    Instructions: Answer the question using the following Context.
    
    Context: {0}
    
    Question: {1}
    """.format(data, question)

    print (prompt)

    model = GenerativeModel("gemini-pro")
    response = model.generate_content(
    prompt,
    generation_config={
        "max_output_tokens": 8192,
        "temperature": 0.5,
        "top_p": 0.5,
        "top_k": 10,
    },
    stream=False,
    )
    print (response.text)
    return response.text


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
