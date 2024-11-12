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
from pydantic import BaseModel

# Import necessary modules from LangChain
from langchain.vectorstores import Pinecone as PineconeVectorStore
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

# Load environment variables and setup directories
load_dotenv()
UPLOAD_DIR = "uploaded_files"
EXTRACTED_TEXT_DIR = "extracted_texts"
ANALYSIS_DIR = "analysis"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXTRACTED_TEXT_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)

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

# Initialize Pinecone
pinecone_api_key = os.getenv("PINECONE_API_KEY")
environment = "us-east-1"
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

def chunk_text(text, max_chunk_size=1024):
    words = text.split()
    chunks, current_chunk = [], []
    current_size = 0
    for word in words:
        if current_size + len(word) + 1 > max_chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk, current_size = [word], len(word)
        else:
            current_chunk.append(word)
            current_size += len(word) + 1
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks

def generate_summary(text):
    chunks = chunk_text(text)
    summaries = []
    for chunk in chunks:
        if len(chunk.split()) < 10:
            continue
        summary = summarizer(chunk, max_length=150, min_length=30, do_sample=False, num_beams=4)
        summaries.append(summary[0]['summary_text'])
    return " ".join(summaries)

def get_embedding(text, model="text-embedding-ada-002"):
    response = openai.Embedding.create(input=[text], model=model)
    return response['data'][0]['embedding']

@app.get("/analysis")
def analyze_document():
    """Endpoint to return the latest analysis"""
    try:
        analysis_file_path = os.path.join(ANALYSIS_DIR, "latest_analysis.txt")
        if not os.path.exists(analysis_file_path):
            return {"error": "No analysis available. Please upload a document first."}
        
        with open(analysis_file_path, "r", encoding="utf-8") as file:
            analysis = file.read()
        
        return {"analysis": analysis}
    except Exception as e:
        return {"error": f"Error during analysis retrieval: {str(e)}"}

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
        text = "".join([page.get_text() for page in doc])

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

        # Store the latest analysis in a file
        analysis_data = {
            "filename": text_filename,
            "summary": summary,
            "statistics": {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "compression_ratio": (len(summary.split()) / word_count if word_count > 0 else 0)
            }
        }

        # Save analysis to a file
        analysis_path = os.path.join(ANALYSIS_DIR, "latest_analysis.txt")
        with open(analysis_path, "w", encoding="utf-8") as analysis_file:
            json.dump(analysis_data, analysis_file, indent=4)

        # Generate and upsert embeddings for each line of extracted text
        pinecone_success = True
        for i, line in enumerate(text.splitlines()):
            if line.strip():
                embedding = get_embedding(line)
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

        return {
            "message": "PDF processed, analysis saved, and embeddings generated",
            "analysis_file": analysis_path,
            "pinecone_status": "Success" if pinecone_success else "Failed"
        }
    except Exception as e:
        return {"error": f"Error during PDF upload or text extraction: {str(e)}"}

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask_question")
async def ask_question(request: QuestionRequest):
    """Endpoint to answer questions based on the uploaded documents"""
    try:
        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        docsearch = PineconeVectorStore.from_existing_index(
            index_name=index_name,
            embedding=embeddings,
            text_key="text",
            namespace="real"
        )

        qa = RetrievalQA.from_chain_type(
            llm=OpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY")),
            chain_type="stuff",
            retriever=docsearch.as_retriever(search_kwargs={"k": 6})
        )

        answer = qa.run(request.question)

        return {"answer": answer}

    except Exception as e:
        return {"error": f"Error during question answering: {str(e)}"}

@app.get("/get_vectors")
def get_vectors():
    try:
        query_response = index.query(
            top_k=100,
            include_values=True,
            include_metadata=True,
            namespace="real"
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