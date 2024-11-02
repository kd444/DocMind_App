from fastapi import FastAPI, UploadFile, File
import shutil
import os
import easyocr
from pdf2image import convert_from_path
import numpy as np
import openai
import json

# Set your OpenAI API key
openai.api_key = ""

# Function to generate embeddings using OpenAI's updated Embedding API
def get_embedding(text, model="text-embedding-ada-002"):
    response = openai.Embedding.create(
        model=model,
        input=[text]  # Ensure the input is a list of strings
    )
    return response['data'][0]['embedding']

app = FastAPI()

# Directory to save the uploaded PDFs, extracted text files, and embeddings
UPLOAD_DIR = "uploaded_files"
EXTRACTED_TEXT_DIR = "extracted_texts"
EMBEDDINGS_DIR = "embeddings"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXTRACTED_TEXT_DIR, exist_ok=True)
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # Save the uploaded PDF
    pdf_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Convert PDF to images
    images = convert_from_path(pdf_path)
    reader = easyocr.Reader(['en'], gpu=False)
    extracted_text = []

    # Process each image with EasyOCR
    for i, image in enumerate(images):
        # Convert PIL image to numpy array
        image_np = np.array(image)
        text = reader.readtext(image_np, detail=0)
        extracted_text.extend(text)

    # Save the extracted text to a .txt file
    text_filename = f"{os.path.splitext(file.filename)[0]}.txt"
    text_path = os.path.join(EXTRACTED_TEXT_DIR, text_filename)
    with open(text_path, "w", encoding="utf-8") as text_file:
        text_file.write("\n".join(extracted_text))

    # Generate embeddings for each line of extracted text
    embeddings = []
    for line in extracted_text:
        if line.strip():  # Ensure non-empty lines are processed
            embedding = get_embedding(line)
            embeddings.append({"text": line, "embedding": embedding})
    
    # Save the embeddings to a JSON file
    embeddings_filename = f"{os.path.splitext(file.filename)[0]}_embeddings.json"
    embeddings_path = os.path.join(EMBEDDINGS_DIR, embeddings_filename)
    with open(embeddings_path, "w", encoding="utf-8") as embeddings_file:
        json.dump(embeddings, embeddings_file)

    return {
        "message": "PDF processed, text file saved, and embeddings generated",
        "text_file": text_path,
        "embeddings_file": embeddings_path
    }
