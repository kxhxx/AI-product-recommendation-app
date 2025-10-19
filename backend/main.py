import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- INITIALIZATION ---

# Load environment variables from .env file
load_dotenv()

# Load API keys from environment
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PINECONE_INDEX_NAME = "product-recommendations"

# Check if API keys are available
if not all([PINECONE_API_KEY, PINECONE_ENVIRONMENT, GROQ_API_KEY]):
    raise ValueError("API keys for Pinecone or Groq are not set in the environment.")

# Initialize global objects
app = FastAPI()
model = None
pc = None
index = None
llm_chain = None

# This startup event loads the models once when the server starts
@app.on_event("startup")
def startup_event():
    global model, pc, index, llm_chain
    print("--- Loading models and connecting to services... ---")
    
    # Load the sentence transformer model
    model = SentenceTransformer('clip-ViT-B-32')
    
    # Initialize Pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)

    # Initialize LangChain with Groq for GenAI
    # The new, recommended model from Groq
    chat = ChatGroq(temperature=0.7, model_name="llama-3.1-8b-instant", groq_api_key=GROQ_API_KEY)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a creative marketing assistant for a furniture store. Write a short, appealing, and imaginative product description (2-3 sentences max). Do not use markdown or bullet points."),
        ("human", "Generate a description for the following product: Title: {title}, Material: {material}, Color: {color}.")
    ])
    output_parser = StrOutputParser()
    llm_chain = prompt | chat | output_parser
    
    print("--- Models and services loaded successfully. ---")

# --- CORS MIDDLEWARE ---
# This allows your React frontend (running on a different port) to communicate with this backend.
app.add_middleware(
    CORSMiddleware,
allow_origins=[
    "http://localhost:5173",
    "https://ai-product-recommendation-app.vercel.app"
],    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- PYDANTIC MODELS (for request/response validation) ---
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
    return {"status": "API is running."}

@app.post("/recommend")
async def recommend_products(request: RecommendRequest):
    """
    Accepts a user query, embeds it, and returns the top_k similar products from Pinecone.
    """
    if not model or not index:
        raise HTTPException(status_code=503, detail="Model or database not initialized.")
    try:
        # Create the embedding for the user's query
        query_embedding = model.encode(request.query).tolist()

        # Query Pinecone
        result = index.query(
            vector=query_embedding,
            top_k=request.top_k,
            include_metadata=True
        )
        
        # Format the response
        recommendations = [match['metadata'] for match in result['matches']]
        return {"recommendations": recommendations}

    except Exception as e:
        print(f"Error during recommendation: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve recommendations.")

@app.post("/generate-description")
async def generate_description(request: GenDescRequest):
    """
    Generates a creative product description using LangChain and Groq's Llama3 model.
    """
    if not llm_chain:
        raise HTTPException(status_code=503, detail="Generative model not initialized.")
    try:
        # Invoke the LangChain to generate the description
        description = llm_chain.invoke({
            "title": request.title,
            "material": request.material,
            "color": request.color
        })
        return {"description": description}

    except Exception as e:
        print(f"Error during description generation: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate description.")