# import os
# import requests
# from flask import Flask, request, jsonify, render_template
# from bs4 import BeautifulSoup
# from llama_index.core import SimpleDirectoryReader, ServiceContext, VectorStoreIndex
# from llama_index.llms.ollama import Ollama
# from llama_index.llms.groq import Groq  # Using Groq API

# # Flask setup
# app = Flask(__name__)

# # Set up Groq API key
# GROQ_API_KEY = "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"  # Replace with your actual API key

# # Function to scrape a webpage
# def scrape_website(url):
#     try:
#         headers = {"User-Agent": "Mozilla/5.0"}
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.text, "html.parser")
#         text_data = " ".join([p.get_text() for p in soup.find_all("p")])  # Extract paragraphs
        
#         # Save scraped data
#         with open("data/scraped_data.txt", "w", encoding="utf-8") as file:
#             file.write(text_data)
        
#         return text_data
#     except requests.exceptions.RequestException as e:
#         return str(e)

# # Function to process queries using LLM
# from llama_index.core.settings import Settings


# def ask_llm(question):
#     # Read scraped data
#     with open("data/scraped_data.txt", "r", encoding="utf-8") as file:
#         document_text = file.read()

#     # Convert text into a LlamaIndex Document
#     document = Document(text=document_text)

#     # Initialize LLaMA model (Groq API)
#     llm = Groq(api_key=GROQ_API_KEY, model="llama3-8b-8192")

#     # Set LLM in the global settings
#     Settings.llm = llm  

#     # Create a LlamaIndex vector store
#     index = VectorStoreIndex.from_documents([document])
#     query_engine = index.as_query_engine()

#     response = query_engine.query(question)
#     return str(response)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/scrape', methods=['POST'])
# def scrape():
#     data = request.json
#     url = data.get("url")
#     if not url:
#         return jsonify({"error": "URL is required"}), 400
    
#     scraped_text = scrape_website(url)
#     return jsonify({"message": "Scraping completed", "data": scraped_text})

# @app.route('/ask', methods=['POST'])
# def ask():
#     data = request.json
#     question = data.get("question")
#     if not question:
#         return jsonify({"error": "Question is required"}), 400
    
#     answer = ask_llm(question)
#     return jsonify({"answer": answer})

# if __name__ == '__main__':
#     if not os.path.exists("data"):
#         os.makedirs("data")
#     app.run(debug=True)
import os
import requests
from flask import Flask, request, jsonify, render_template
from bs4 import BeautifulSoup
from llama_index.core import SimpleDirectoryReader, ServiceContext, VectorStoreIndex, Document
from llama_index.llms.groq import Groq
from llama_index.core.settings import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Flask setup
app = Flask(__name__)

# Load Groq API key securely from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set! Please set it in environment variables.")

# Ensure the "data" directory exists
os.makedirs("data", exist_ok=True)

# Function to scrape a webpage
def scrape_website(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse webpage content
        soup = BeautifulSoup(response.text, "html.parser")
        text_data = " ".join([p.get_text() for p in soup.find_all("p")])

        # Save scraped data
        file_path = "data/scraped_data.txt"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(text_data)

        return text_data
    except requests.exceptions.RequestException as e:
        return f"Error fetching webpage: {str(e)}"

# Function to process queries using LLM
def ask_llm(question):
    try:
        file_path = "data/scraped_data.txt"
        if not os.path.exists(file_path):
            return "No scraped data available. Please scrape a website first."

        with open(file_path, "r", encoding="utf-8") as file:
            document_text = file.read()

        document = Document(text=document_text)

        # Initialize Groq LLaMA model
        llm = Groq(api_key=GROQ_API_KEY, model="llama3-8b-8192")
        Settings.llm = llm  
        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en")  

        # Create a LlamaIndex vector store
        index = VectorStoreIndex.from_documents([document])
        query_engine = index.as_query_engine()

        response = query_engine.query(question)
        return str(response)
    except Exception as e:
        return f"Error processing request: {str(e)}"

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400

    scraped_text = scrape_website(url)
    return jsonify({"message": "Scraping completed", "data": scraped_text})

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get("question")
    if not question:
        return jsonify({"error": "Question is required"}), 400

    answer = ask_llm(question)
    return jsonify({"answer": answer})

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
