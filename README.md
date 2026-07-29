# ⚖️ Gramin-Nyaya | AI-Powered Legal Aid

An advanced AI platform designed to promote legal awareness and democratize access to justice in rural India. Gramin-Nyaya acts as a personal legal assistant, enabling users to ask complex legal questions in Hindi, and retrieving accurate answers from complex English legal statutes using a state-of-the-art **Cross-Lingual RAG (Retrieval-Augmented Generation)** pipeline.

![Gramin-Nyaya Banner](frontend/banner_placeholder.png) <!-- Replace with a screenshot of your landing page -->

## ✨ Features
- **🗣️ Voice-to-Text Support**: Speak your legal questions natively. Integrated with OpenAI's Whisper model for highly accurate STT.
- **🌐 Cross-Lingual RAG**: Break the language barrier. Ask in simple Hindi, search against raw English legal Acts (e.g., The Registration Act, 1908), and receive answers generated in simple Hindi.
- **⚡ Edge Deployable**: Built to run entirely locally. Powered by the lightweight `Llama-3.2:1b` model via Ollama, ensuring privacy and offline capability.
- **🏛️ Accessible UI**: A highly legible, high-contrast, official "Civic-Tech" inspired frontend designed specifically for digital literacy in rural environments.

## 🏗️ Technology Stack
* **Frontend**: Vanilla HTML / CSS / JavaScript
* **Backend**: FastAPI (Python)
* **LLM Orchestration**: LangChain
* **Vector Database**: ChromaDB
* **Embeddings**: HuggingFace `all-MiniLM-L6-v2`
* **Local Inference**: Ollama (`llama3.2:1b`)
* **Speech-to-Text**: Whisper

### Core Python Libraries Used
- `fastapi` & `uvicorn`: For the backend REST API web server.
- `langchain`, `langchain-community`, `langchain-chroma`: For orchestrating the complex RAG logic.
- `chromadb`: The local vector database for storing legal document embeddings.
- `sentence-transformers`: For generating vector embeddings using HuggingFace models.
- `ollama`: The Python client to communicate with the local Llama 3.2 model.
- `faster-whisper`: A highly optimized CTranslate2 implementation of Whisper for fast local speech-to-text.

## 🚀 Getting Started

### Prerequisites
1. **Python 3.10+** installed on your system.
2. **[Ollama](https://ollama.ai/)** installed and running.
3. Download the Llama 3.2 1B model by running:
   ```bash
   ollama run llama3.2:1b
   ```

### Installation

1. **Clone the repository** (if applicable) and navigate to the project directory:
   ```bash
   cd Gramin-Nyaya
   ```

2. **Install the required Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Build the Vector Database**:
   Before running the app, you need to ingest the legal documents into ChromaDB.
   ```bash
   python ingest_docs.py
   ```
   *(Note: Ensure your raw legal text files are placed in the `legal_docs/` folder.)*

4. **Start the Application**:
   ```bash
   python app.py
   ```

5. **Access the Web Interface**:
   Open your browser and navigate to: `http://localhost:8000`

## 📁 Project Structure
```
Gramin-Nyaya/
├── app.py                 # FastAPI backend server
├── rag_logic.py           # Core Langchain & Ollama inference pipeline
├── ingest_docs.py         # Script to chunk and vectorize legal text
├── clean_script.py        # Utility to strip noise from raw legal Acts
├── stt_service.py         # Whisper Audio-to-Text processing
├── requirements.txt       # Python dependencies
├── legal_docs/            # Directory containing raw legal text files
└── static/                # Frontend assets
    ├── index.html         # Landing page & Chat interface
    ├── style.css          # UI Styling
    └── script.js          # Client-side audio handling & API calls
```

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

---
*Disclaimer: Gramin-Nyaya is an AI tool meant to provide legal information and promote legal literacy. It is not a substitute for professional legal counsel.*
