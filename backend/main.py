import os
import json
import shutil
import fitz  # PyMuPDF
import openai
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
from pinecone import Pinecone, ServerlessSpec
import numpy as np

# Import necessary modules from LangChain and Pydantic
from langchain.vectorstores import Pinecone as PineconeVectorStore
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from pydantic import BaseModel

# Load environment variables and setup directories
load_dotenv()
UPLOAD_DIR = "uploaded_files"
EXTRACTED_TEXT_DIR = "extracted_texts"
EMBEDDINGS_DIR = "embeddings"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXTRACTED_TEXT_DIR, exist_ok=True)
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize summarizer pipeline
MODEL_NAME = "facebook/bart-large-cnn"
summarizer = pipeline("summarization", model=MODEL_NAME)

# Global variable to store the latest analysis
latest_analysis = {}

# Initialize Pinecone
pinecone_api_key = os.getenv("PINECONE_API_KEY")
environment = "us-east-1"  # Replace with your specific environment if different
pc = Pinecone(api_key=pinecone_api_key)
index_name = "docmindapp"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region=environment
        )
    )
index = pc.Index(index_name)

# Function to generate embeddings using OpenAI's updated Embedding API
def get_embedding(text, model="text-embedding-ada-002"):
    response = openai.Embedding.create(input=[text], model=model)
    return response['data'][0]['embedding']

def chunk_text(text, max_chunk_size=1024):
    """Split text into smaller chunks for processing"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0

    for word in words:
        if current_size + len(word) + 1 > max_chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_size = len(word)
        else:
            current_chunk.append(word)
            current_size += len(word) + 1

    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks

def generate_summary(text):
    """Generate summary using the summarization pipeline"""
    # Split text into chunks if it's too long
    chunks = chunk_text(text)
    summaries = []

    for chunk in chunks:
        # Skip empty or very short chunks
        if len(chunk.split()) < 10:
            continue

        summary = summarizer(
            chunk,
            max_length=150,
            min_length=30,
            do_sample=False,
            num_beams=4,
            early_stopping=True
        )
        summaries.append(summary[0]['summary_text'])

    # Combine summaries if multiple chunks were processed
    final_summary = " ".join(summaries)
    return final_summary

@app.get("/analysis")
def analyze_document():
    """Endpoint to return the latest analysis"""
    try:
        if not latest_analysis:
            return {"error": "No analysis available. Please upload a document first."}

        return latest_analysis
    except Exception as e:
        return {"error": f"Error during analysis: {str(e)}"}

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Endpoint to upload a PDF file and extract its text"""
    try:
        # Save uploaded file
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        # Extract text from PDF
        doc = fitz.open(file_location)
        text = ""
        for page in doc:
            text += page.get_text()

        # Save extracted text to a file
        text_filename = os.path.splitext(file.filename)[0] + ".txt"
        text_path = os.path.join(EXTRACTED_TEXT_DIR, text_filename)
        with open(text_path, "w", encoding="utf-8") as text_file:
            text_file.write(text)

        # Generate summary
        summary = generate_summary(text)

        # Get document statistics
        word_count = len(text.split())
        sentence_count = len([s for s in text.split('.') if s.strip()])

        # Store the latest analysis in the global variable
        global latest_analysis
        latest_analysis = {
            "filename": text_filename,
            "summary": summary,
            "statistics": {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "compression_ratio": (
                    len(summary.split()) / word_count if word_count > 0 else 0
                )
            }
        }

        # Generate and upsert embeddings for each line of extracted text
        embeddings = []
        pinecone_success = True
        for i, line in enumerate(text.splitlines()):
            if line.strip():  # Ensure non-empty lines are processed
                embedding = get_embedding(line)
                embeddings.append({"text": line, "embedding": embedding})
                try:
                    index.upsert(
                        vectors=[
                            {
                                "id": f"{file.filename}_line_{i}",
                                "values": embedding,
                                "metadata": {"text": line}
                            }
                        ],
                        namespace="real"
                    )
                except Exception as e:
                    pinecone_success = False
                    print(f"Error upserting to Pinecone: {str(e)}")

        # Save the embeddings to a JSON file
        embeddings_filename = f"{os.path.splitext(file.filename)[0]}_embeddings.json"
        embeddings_path = os.path.join(EMBEDDINGS_DIR, embeddings_filename)
        with open(embeddings_path, "w", encoding="utf-8") as embeddings_file:
            json.dump(embeddings, embeddings_file)

        return {
            "message": "PDF processed, text file saved, and embeddings generated",
            "text_file": text_path,
            "embeddings_file": embeddings_path,
            "pinecone_status": "Success" if pinecone_success else "Failed"
        }
    except Exception as e:
        return {"error": f"Error during PDF upload or text extraction: {str(e)}"}

# Define a request model for the question
class QuestionRequest(BaseModel):
    question: str

@app.post("/ask_question")
async def ask_question(request: QuestionRequest):
    """Endpoint to answer questions based on the uploaded documents"""
    try:
        # Initialize the OpenAI embeddings
        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

        # Initialize the Pinecone vector store
        docsearch = PineconeVectorStore.from_existing_index(
            index_name=index_name,
            embedding=embeddings,
            text_key="text",
            namespace="real"
        )

        # Create a RetrievalQA chain
        qa = RetrievalQA.from_chain_type(
            llm=OpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY")),
            chain_type="stuff",
            retriever=docsearch.as_retriever(
                search_kwargs={"k": 3}  # Retrieve top 3 most relevant documents
            )
        )

        # Get the answer
        answer = qa.run(request.question)

        return {"answer": answer}

    except Exception as e:
        return {"error": f"Error during question answering: {str(e)}"}


@app.get("/get_vectors")
def get_vectors():
    try:
        # Fetch vectors from Pinecone
        query_response = index.query(
            top_k=100,  # Adjust as needed
            include_values=True,
            include_metadata=True,
            namespace="real"  # Use the same namespace as during upsert
        )
        vectors = [
            {
                "id": match["id"],
                "values": match["values"],
                "metadata": match.get("metadata", {})
            }
            for match in query_response["matches"]
        ]
        return {"vectors": vectors}
    except Exception as e:
        return {"error": f"Error fetching vectors: {str(e)}"}