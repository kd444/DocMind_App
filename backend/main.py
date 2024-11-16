import os
import json
import shutil
import fitz  # PyMuPDF
import openai
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline, BartTokenizer, BartForConditionalGeneration
from transformers import T5Tokenizer, T5ForConditionalGeneration
from pydantic import BaseModel
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.llms import OpenAI
from langchain.chains import RetrievalQA
from pinecone import Pinecone, ServerlessSpec
import numpy as np

# Setup directories
load_dotenv()
UPLOAD_DIR = "uploaded_files"
EXTRACTED_TEXT_DIR = "extracted_texts"
ANALYSIS_DIR = "analysis"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXTRACTED_TEXT_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models
MODEL_PATH = "./custom_bart_model_pretrained"
bart_tokenizer = BartTokenizer.from_pretrained(MODEL_PATH)
bart_model = BartForConditionalGeneration.from_pretrained(MODEL_PATH)
summarizer = pipeline("summarization", model=bart_model, tokenizer=bart_tokenizer)

t5_model_name = "t5-base"
t5_tokenizer = T5Tokenizer.from_pretrained(t5_model_name)
t5_model = T5ForConditionalGeneration.from_pretrained(t5_model_name)
t5_summarizer = pipeline("summarization", model=t5_model, tokenizer=t5_tokenizer)

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
        spec=ServerlessSpec(cloud="aws", region=environment)
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

def generate_summary_bart(text):
    chunks = chunk_text(text)
    summaries = []
    for chunk in chunks:
        if len(chunk.split()) < 10:
            continue
        summary = summarizer(chunk, max_length=150, min_length=30, do_sample=False, num_beams=4)
        summaries.append(summary[0]['summary_text'])
    return " ".join(summaries)

def generate_summary_t5(text):
    chunks = chunk_text(text)
    summaries = []
    for chunk in chunks:
        if len(chunk.strip()) == 0:
            continue
        summary = t5_summarizer(chunk, max_length=150, min_length=30, do_sample=False)
        summaries.append(summary[0]['summary_text'])
    return " ".join(summaries)

def get_embedding(text, model="text-embedding-ada-002"):
    response = openai.Embedding.create(input=[text], model=model)
    return response['data'][0]['embedding']

def cosine_similarity(vec1, vec2):
    vec1, vec2 = np.array(vec1), np.array(vec2)
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

@app.get("/analysis")
def analyze_document():
    try:
        analysis_file_path = os.path.join(ANALYSIS_DIR, "latest_analysis.txt")
        if not os.path.exists(analysis_file_path):
            return {"error": "No analysis available."}
        with open(analysis_file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        return {"error": f"Error: {str(e)}"}

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
        doc = fitz.open(file_location)
        text = "".join([page.get_text() for page in doc])
        text_filename = os.path.splitext(file.filename)[0] + ".txt"
        text_path = os.path.join(EXTRACTED_TEXT_DIR, text_filename)
        with open(text_path, "w", encoding="utf-8") as text_file:
            text_file.write(text)
        summary_bart = generate_summary_bart(text)
        summary_t5 = generate_summary_t5(text)
        text_truncated = text[:2000]
        summary_bart_truncated = summary_bart[:2000]
        summary_t5_truncated = summary_t5[:2000]
        embedding_text = get_embedding(text_truncated)
        embedding_summary_bart = get_embedding(summary_bart_truncated)
        embedding_summary_t5 = get_embedding(summary_t5_truncated)
        cosine_sim_bart = cosine_similarity(embedding_summary_bart, embedding_text)
        cosine_sim_t5 = cosine_similarity(embedding_summary_t5, embedding_text)
        analysis_data = {
            "filename": text_filename,
            "summary_bart": summary_bart,
            "summary_t5": summary_t5,
            "cosine_similarity_bart": cosine_sim_bart,
            "cosine_similarity_t5": cosine_sim_t5,
            "statistics": {
                "word_count": len(text.split()),
                "sentence_count": len([s for s in text.split('.') if s.strip()]),
                "compression_ratio_bart": len(summary_bart.split()) / len(text.split()),
                "compression_ratio_t5": len(summary_t5.split()) / len(text.split())
            }
        }
        analysis_path = os.path.join(ANALYSIS_DIR, "latest_analysis.txt")
        with open(analysis_path, "w", encoding="utf-8") as analysis_file:
            json.dump(analysis_data, analysis_file, indent=4)
        for i, line in enumerate(text.splitlines()):
            if line.strip():
                embedding = get_embedding(line)
                index.upsert(
                    vectors=[{"id": f"{file.filename}_line_{i}", "values": embedding, "metadata": {"text": line}}],
                    namespace="real"
                )
        os.remove(file_location)
        os.remove(text_path)
        return {"message": "PDF processed", "analysis_file": analysis_path}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask_question")
async def ask_question(request: QuestionRequest):
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
        return {"answer": qa.run(request.question)}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}

@app.get("/get_vectors")
def get_vectors():
    try:
        query_response = index.query(top_k=100, include_values=True, include_metadata=True, namespace="real")
        vectors = [
            {"id": match["id"], "values": match["values"], "metadata": match.get("metadata", {})}
            for match in query_response["matches"]
        ]
        return {"vectors": vectors}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}
