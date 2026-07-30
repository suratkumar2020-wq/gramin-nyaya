import os
import shutil
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# 1. Configuration - Pointing to your directory structure
DOCS_DIR = "./legal_docs"
DB_DIR = "./chroma_db"

def ingest_data():
    print(f"\n--- Starting Ingestion Process ---")
    
    # Clean up old database directory if it exists to avoid duplicate entries
    if os.path.exists(DB_DIR):
        print(f"Removing existing vector database at: {DB_DIR} (to ensure a clean build)")
        try:
            shutil.rmtree(DB_DIR)
        except Exception as e:
            print(f"[Warning] Could not clean up old database folder: {e}")
            
    # 2. Load all TXT and PDF documents from legal_docs directory
    print(f"Scanning for legal documents in: {DOCS_DIR}")
    documents = []
    
    if not os.path.exists(DOCS_DIR):
        print(f"[Error] Source directory '{DOCS_DIR}' not found. Please create it.")
        return
        
    files = [f for f in os.listdir(DOCS_DIR) if os.path.isfile(os.path.join(DOCS_DIR, f))]
    
    for file_name in files:
        file_path = os.path.join(DOCS_DIR, file_name)
        try:
            if file_name.endswith(".txt"):
                print(f"-> Loading TXT document: {file_name}")
                loader = TextLoader(file_path, encoding="utf-8")
                documents.extend(loader.load())
            elif file_name.endswith(".pdf"):
                print(f"-> Loading PDF document: {file_name}")
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
            else:
                print(f"-> Skipping unsupported file type: {file_name}")
        except Exception as e:
            print(f"[Error] Failed to load {file_name}: {e}")

    if not documents:
        print("[Error] No text or PDF files were loaded from the directory.")
        return
        
    print(f"Successfully loaded {len(documents)} source document(s).")

    # 3. Split the Text into Chunks
    print("Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,       # Reduced from 800 — tighter chunks = smaller prompt size
        chunk_overlap=80,     # Reduced overlap keeps total DB size smaller on disk
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} text chunks.")

    # 4. Initialize Embeddings (Matching your rag_logic.py exactly)
    print("Initializing embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},  # Must match rag_logic.py for consistent similarity scores
    )

    # 5. Create and Save the Vector Database
    print("Building Chroma vector database. This may take a moment...")
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    
    print(f"--- Success! Database built and safely saved to {DB_DIR} ---")

if __name__ == "__main__":
    ingest_data()