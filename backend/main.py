import os
import json
import shutil
import fitz  # PyMuPDF
import openai
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from pinecone import Pinecone, ServerlessSpec

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Get Pinecone API key from environment variable
pinecone_api_key = os.getenv("PINECONE_API_KEY")

# Hardcoded Pinecone environment
environment = "us-east-1"  # Replace with your specific environment if different

# Initialize Pinecone
pc = Pinecone(
    api_key=pinecone_api_key
)

# Create or connect to the Pinecone index
index_name = "document-vectors"
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
    response = openai.Embedding.create(
        model=model,
        input=[text]  # Ensure the input is a list of strings
    )
    return response['data'][0]['embedding']

app = FastAPI()

# Directory to save the uploaded PDFs and extracted text files
UPLOAD_DIR = "uploaded_files"
EXTRACTED_TEXT_DIR = "extracted_texts"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXTRACTED_TEXT_DIR, exist_ok=True)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # Save the uploaded PDF
    pdf_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Extract text using PyMuPDF (fitz)
    extracted_text = []
    pdf_document = fitz.open(pdf_path)
    
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text = page.get_text()
        extracted_text.extend(text.splitlines())
    
    pdf_document.close()

    # Save the extracted text to a .txt file
    text_filename = f"{os.path.splitext(file.filename)[0]}.txt"
    text_path = os.path.join(EXTRACTED_TEXT_DIR, text_filename)
    with open(text_path, "w", encoding="utf-8") as text_file:
        text_file.write("\n".join(extracted_text))

    # Generate and upsert embeddings for each line of extracted text
    for i, line in enumerate(extracted_text):
        if line.strip():  # Ensure non-empty lines are processed
            embedding = get_embedding(line)
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

    return {
        "message": "PDF processed, text file saved, and embeddings generated and upserted to Pinecone",
        "text_file": text_path
    }
