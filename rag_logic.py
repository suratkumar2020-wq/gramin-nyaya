import ollama
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# ──────────────────────────────────────────────────────────────
# Lazy-loaded globals — nothing is loaded into RAM until the
# first actual query arrives. This keeps startup footprint near
# zero and is critical on a 4 GB Jetson board.
# ──────────────────────────────────────────────────────────────
_embeddings = None
_vector_db  = None

MAX_CONTEXT_CHARS = 800   # Hard cap: prevents prompt from bloating num_ctx
RETRIEVE_K        = 2     # k=2 gives tighter, more relevant chunks than k=3


def _get_vector_db():
    """Initialize embedding model and Chroma DB on first call only."""
    global _embeddings, _vector_db
    if _vector_db is None:
        print("--- Connecting to Existing Legal Database... ---")
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},  # Improves cosine similarity accuracy
        )
        _vector_db = Chroma(
            persist_directory="./chroma_db",
            embedding_function=_embeddings,
        )
    return _vector_db


def ask_gramin_nyaya(user_query):
    try:
        db = _get_vector_db()

        # 1. Retrieve the top-2 most relevant chunks (down from 3)
        #    Fewer chunks = smaller prompt = less KV cache pressure.
        relevant_chunks = db.similarity_search(user_query, k=RETRIEVE_K)

        if not relevant_chunks:
            return "क्षमा करें, यह जानकारी इस दस्तावेज़ में उपलब्ध नहीं है।"

        # 2. Join chunks and hard-cap total context length.
        #    This guarantees the final prompt stays inside num_ctx=1024.
        raw_context  = "\n\n".join([chunk.page_content for chunk in relevant_chunks])
        context_text = raw_context[:MAX_CONTEXT_CHARS]

        # 3. Build a compact, directive prompt in Hindi
        print("--- Running Llama 3.2:1b (Legal Assistant) ---")
        llama_prompt = (
            f"नीचे दिए गए कानूनी संदर्भ को पढ़कर प्रश्न का उत्तर सरल हिंदी में दें।\n\n"
            f"संदर्भ:\n{context_text}\n\n"
            f"प्रश्न: {user_query}\n\n"
            f"उत्तर:"
        )

        # 4. Generate — every option tuned for minimal RAM on 4 GB Jetson
        final_response = ollama.chat(
            model="llama3.2:1b",
            messages=[
                {
                    "role": "system",
                    "content": "You are Gramin-Nyaya, a legal assistant for rural India. Always answer in simple Hindi.",
                },
                {"role": "user", "content": llama_prompt},
            ],
            options={
                "temperature":    0.1,   # Near-deterministic; reduces sampling overhead
                "repeat_penalty": 1.1,   # Prevents looping without heavy compute
                "top_k":          10,    # Narrow beam keeps generation fast
                "top_p":          0.1,
                "num_ctx":        1024,  # KV cache capped to ~250 MB on Jetson
                "num_predict":    256,   # Stop generation after 256 tokens — prevents RAM runaway
                "keep_alive":     0,     # Unload LLM from RAM immediately after response
            },
        )

        return final_response["message"]["content"]

    except Exception as e:
        print(f"\n[Error in RAG pipeline]: {e}")
        return "तकनीकी समस्या के कारण जवाब देने में असमर्थ हूँ।"