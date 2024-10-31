from fastapi import FastAPI, UploadFile, File
import shutil
import os
import easyocr
from pdf2image import convert_from_path
import numpy as np

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
    
    return {"message": "PDF processed and text file saved", "text_file": text_path}
