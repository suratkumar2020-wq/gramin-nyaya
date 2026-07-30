from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import shutil

from rag_logic import ask_gramin_nyaya
from stt_service import transcribe_audio_file

app = FastAPI()

# Ensure vector DB exists on startup
if not os.path.exists("./chroma_db"):
    print("[Startup] Vector database not found. Ingesting documents...")
    try:
        from ingest_docs import ingest_data
        ingest_data()
    except Exception as e:
        print(f"[Startup Warning] Could not ingest documents: {e}")

# Mount the static directory
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class QueryRequest(BaseModel):
    query: str

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/ask")
def ask_question(req: QueryRequest):
    try:
        answer = ask_gramin_nyaya(req.query)
        return {"answer": answer}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/transcribe")
def transcribe_audio(file: UploadFile = File(...)):
    try:
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        transcription = transcribe_audio_file(temp_file_path)
        
        # Cleanup
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
        return {"transcription": transcription}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    print("Starting Web UI on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
