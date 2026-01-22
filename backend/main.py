import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from pinecone import Pinecone
from groq import Groq # Add this to your requirements.txt
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- INITIALIZATION ---
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PINECONE_INDEX_NAME = "product-recommendations"

if not all([PINECONE_API_KEY, GROQ_API_KEY]):
    raise ValueError("Missing API keys for Pinecone or Groq.")

app = FastAPI()
pc = None
index = None
llm_chain = None
groq_client = Groq(api_key=GROQ_API_KEY) # Initialize direct Groq client

@app.on_event("startup")
def startup_event():
    global pc, index, llm_chain
    print("--- Connecting to Pinecone and Groq... ---")
    
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)

    chat = ChatGroq(temperature=0.7, model_name="llama-3.1-8b-instant", groq_api_key=GROQ_API_KEY)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a creative marketing assistant for a furniture store. Write a short description (2-3 sentences max)."),
        ("human", "Generate a description for: Title: {title}, Material: {material}, Color: {color}.")
    ])
    llm_chain = prompt | chat | StrOutputParser()
    print("--- Success: Running on Groq Cloud ---")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendRequest(BaseModel):
    query: str
    top_k: int = 5

# --- API ENDPOINTS ---

@app.post("/recommend")
async def recommend_products(request: RecommendRequest):
    if not index:
        raise HTTPException(status_code=503, detail="Database not initialized.")
    
    try:
        # Using Groq's embedding model (Ensure your index was built with 384 or 1024 dims)
        # Note: If your Pinecone index was built with 'all-MiniLM-L6-v2', 
        # you MUST use a model with 384 dimensions. 
        response = groq_client.embeddings.create(
            input=request.query,
            model="nomic-embed-text-v1.5" # This is a common 768-dim model on Groq
        )
        
        query_embedding = response.data[0].embedding

        result = index.query(
            vector=query_embedding,
            top_k=request.top_k,
            include_metadata=True
        )
        
        return {"recommendations": [match['metadata'] for match in result['matches']]}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ... keep your /generate-description and / endpoint same as before ...
