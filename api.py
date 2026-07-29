from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

# Assuming ask_gramin_nyaya can be made async, otherwise remove the 'await' below.
from rag_logic import ask_gramin_nyaya 

app = FastAPI(title="Gramin Nyaya API")

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: Change to your React app's URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def handle_query(request: QueryRequest):
    logger.info(f"User asked: {request.question}")
    
    try:
        # If your RAG function is async, use 'await'. 
        # If it's strictly synchronous, you can remove 'async' from the def and 'await' here.
        answer = ask_gramin_nyaya(request.question) 
        
        return {"answer": answer}
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        # Return a clean HTTP 500 to the frontend with a specific message
        raise HTTPException(status_code=500, detail="Sorry, we encountered an error while processing your legal query.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)