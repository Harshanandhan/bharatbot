import os
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_embed_model = None
_collection = None
_groq = None


def _get_embed_model():
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embed_model


def _get_collection():
    global _collection
    if _collection is None:
        db = chromadb.PersistentClient(path="./chroma_db")
        _collection = db.get_collection("indian_history")
    return _collection


def _get_groq():
    global _groq
    if _groq is None:
        _groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _groq


SYSTEM_PROMPT = """You are BharatBot — an expert guide on Indian history, kingdoms, kings, sacred cities, maps, and Hinduism.

Your answers are:
- Accurate and grounded in the provided context
- Engaging and educational
- Clear about what is mythological vs archaeological vs historical
- Structured when answering complex questions (use bullet points or short sections)

When relevant, mention:
- Time period / era (Vedic, Ancient, Medieval, etc.)
- Geographic region and key cities
- Connection to Hindu traditions, texts, or deities
- Key rulers, events, or battles

Always end by offering to go deeper: suggest 1-2 related topics the user might want to explore next."""


def retrieve(query: str, n_results: int = 5) -> list[dict]:
    model = _get_embed_model()
    collection = _get_collection()

    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    return [
        {
            "content": doc,
            "metadata": results["metadatas"][0][i],
        }
        for i, doc in enumerate(results["documents"][0])
    ]


def ask(query: str, history: list[dict] | None = None) -> dict:
    chunks = retrieve(query)

    context = "\n\n---\n\n".join(
        f"[Source: {c['metadata'].get('title', 'Unknown')} | Era: {c['metadata'].get('era', '?')} | Period: {c['metadata'].get('time_period', '?')}]\n{c['content']}"
        for c in chunks
    )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages.extend(history[-6:])

    messages.append({
        "role": "user",
        "content": f"Reference context:\n{context}\n\nUser question: {query}"
    })

    groq = _get_groq()
    response = groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1024,
        temperature=0.3
    )

    answer = response.choices[0].message.content

    sources = list({
        c["metadata"].get("title", "")
        for c in chunks
        if c["metadata"].get("title")
    })

    return {"answer": answer, "sources": sources}
