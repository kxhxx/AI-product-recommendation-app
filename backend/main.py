import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from pinecone import Pinecone
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- INITIALIZATION ---
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")
PINECONE_INDEX_NAME = "product-recommendations"

# API URL for the same model you were using, but hosted by Hugging Face
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"

if not all([PINECONE_API_KEY, GROQ_API_KEY, HF_TOKEN]):
    raise ValueError("Missing API keys for Pinecone, Groq, or Hugging Face (HF_TOKEN).")

app = FastAPI()
pc = None
index = None
llm_chain = None

@app.on_event("startup")
def startup_event():
    global pc, index, llm_chain
    print("--- Connecting to external services... ---")
    
    # Initialize Pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)

    # Initialize LangChain with Groq
    chat = ChatGroq(temperature=0.7, model_name="llama-3.1-8b-instant", groq_api_key=GROQ_API_KEY)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a creative marketing assistant for a furniture store. Write a short, appealing, and imaginative product description (2-3 sentences max). Do not use markdown or bullet points."),
        ("human", "Generate a description for the following product: Title: {title}, Material: {material}, Color: {color}.")
    ])
    output_parser = StrOutputParser()
    llm_chain = prompt | chat | output_parser
    
    print("--- Services connected. (Model offloaded to API) ---")

# --- CORS MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Broadly allowed to ensure Vercel connects
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendRequest(BaseModel):
    query: str
    top_k: int = 5

class GenDescRequest(BaseModel):
    title: str
    material: str
    color: str

# --- API ENDPOINTS ---

@app.get("/")
def read_root():
    return {"status": "API is running and lightweight."}

@app.post("/recommend")
async def recommend_products(request: RecommendRequest):
    if not index:
        raise HTTPException(status_code=503, detail="Database not initialized.")
    
    try:
        # OFF-LOADED EMBEDDING: Call Hugging Face instead of using local RAM
        async with httpx.AsyncClient() as client:
            hf_response = await client.post(
                HUGGINGFACE_API_URL,
                headers={"Authorization": f"Bearer {HF_TOKEN}"},
                json={"inputs": request.query, "options": {"wait_for_model": True}}
            )
            
            if hf_response.status_code != 200:
                raise HTTPException(status_code=500, detail="Hugging Face API error.")
            
            query_embedding = hf_response.json()

        # Query Pinecone
        result = index.query(
            vector=query_embedding,
            top_k=request.top_k,
            include_metadata=True
        )
        
        recommendations = [match['metadata'] for match in result['matches']]
        return {"recommendations": recommendations}

    except Exception as e:
        print(f"Error during recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-description")
async def generate_description(request: GenDescRequest):
    if not llm_chain:
        raise HTTPException(status_code=503, detail="Generative model not initialized.")
    try:
        description = llm_chain.invoke({
            "title": request.title, "material": request.material, "color": request.color
        })
        return {"description": description}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate description.")
