import os
import json
import shutil
import fitz  # PyMuPDF
import openai
import torch
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# Load environment variables and setup directories
load_dotenv()
UPLOAD_DIR = "uploaded_files"
EXTRACTED_TEXT_DIR = "extracted_texts"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXTRACTED_TEXT_DIR, exist_ok=True)

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
    """Endpoint to analyze and summarize the first document in the directory"""
    try:
        # Find available text files
        text_files = [
            f for f in os.listdir(EXTRACTED_TEXT_DIR) if f.endswith(".txt")
        ]
        if not text_files:
            return {"error": "No text files found in the directory"}

        # Use the first file found
        first_filename = text_files[0]
        text_path = os.path.join(EXTRACTED_TEXT_DIR, first_filename)

        # Read the document
        with open(text_path, "r", encoding="utf-8") as file:
            full_text = file.read()

        # Generate summary
        summary = generate_summary(full_text)

        # Get document statistics
        word_count = len(full_text.split())
        sentence_count = len([s for s in full_text.split('.') if s.strip()])

        return {
            "filename": first_filename,
            "summary": summary,
            "statistics": {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "compression_ratio": (
                    len(summary.split()) / word_count if word_count > 0 else 0
                )
            }
        }
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

        return {"filename": text_filename, "status": "Text extracted successfully"}
    except Exception as e:
        return {"error": f"Error during PDF upload or text extraction: {str(e)}"}
