import os
from typing import Any

import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

_embed_model = None
_collection = None
_groq = None
_groq_init_attempted = False

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


def collection_count() -> int | None:
    """Return chunk count, or None if Chroma is cold / unavailable."""
    try:
        return _get_collection().count()
    except Exception:
        return None


def groq_configured() -> bool:
    key = (os.getenv("GROQ_API_KEY") or "").strip()
    return bool(key) and key != "your_groq_api_key_here"


def _get_groq():
    global _groq, _groq_init_attempted
    if not groq_configured():
        return None
    if _groq is None and not _groq_init_attempted:
        _groq_init_attempted = True
        try:
            from groq import Groq

            _groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
        except Exception:
            _groq = None
    return _groq


def retrieve(query: str, n_results: int = 5) -> list[dict]:
    model = _get_embed_model()
    collection = _get_collection()

    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    return [
        {
            "content": doc,
            "metadata": results["metadatas"][0][i],
        }
        for i, doc in enumerate(results["documents"][0])
    ]


def _source_list(chunks: list[dict]) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    seen: set[str] = set()
    for c in chunks:
        meta = c.get("metadata") or {}
        title = str(meta.get("title") or "Unknown")
        if title in seen:
            continue
        seen.add(title)
        snippet = (c.get("content") or "")[:220].strip()
        if len(c.get("content") or "") > 220:
            snippet += "…"
        sources.append(
            {
                "title": title,
                "era": str(meta.get("era") or "?"),
                "snippet": snippet,
            }
        )
    return sources


def _retrieval_only_answer(query: str, chunks: list[dict]) -> str:
    if not chunks:
        return (
            "No matching chunks were found in the lab corpus "
            "(10 local Indian history passages). "
            "Full LLM answers need a working GROQ_API_KEY."
        )

    parts = [
        f"**Retrieval-only answer** for: _{query}_",
        "",
        "Groq generation is unavailable (missing `GROQ_API_KEY` or the model call failed). "
        "Below are the top matching lab chunks, concatenated extractively — not an LLM synthesis.",
        "",
    ]
    for i, c in enumerate(chunks[:3], 1):
        meta = c.get("metadata") or {}
        title = meta.get("title", "Unknown")
        era = meta.get("era", "?")
        period = meta.get("time_period", "?")
        text = (c.get("content") or "").strip()
        # Short extractive slice
        extract = text if len(text) <= 480 else text[:477] + "…"
        parts.append(f"**{i}. {title}** ({era} · {period})")
        parts.append(extract)
        parts.append("")

    parts.append(
        "_Full conversational answers need a working `GROQ_API_KEY` on the server "
        "(Railway Variables → GROQ_API_KEY)._"
    )
    return "\n".join(parts)


def ask(query: str, history: list[dict] | None = None) -> dict[str, Any]:
    chunks = retrieve(query)
    sources = _source_list(chunks)

    context = "\n\n---\n\n".join(
        f"[Source: {c['metadata'].get('title', 'Unknown')} | "
        f"Era: {c['metadata'].get('era', '?')} | "
        f"Period: {c['metadata'].get('time_period', '?')}]\n{c['content']}"
        for c in chunks
    )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history[-6:])
    messages.append(
        {
            "role": "user",
            "content": f"Reference context:\n{context}\n\nUser question: {query}",
        }
    )

    client = _get_groq()
    if client is None:
        return {
            "answer": _retrieval_only_answer(query, chunks),
            "sources": sources,
            "generation": "retrieval_only",
            "mode": "retrieval_only",
        }

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1024,
            temperature=0.3,
        )
        answer = response.choices[0].message.content
        return {
            "answer": answer,
            "sources": sources,
            "generation": "groq",
            "mode": "groq",
        }
    except Exception as exc:
        fallback = _retrieval_only_answer(query, chunks)
        note = (
            f"\n\n_(Groq call failed: {type(exc).__name__}. "
            "Showing retrieval-only extract instead. "
            "Full LLM answers need a working GROQ_API_KEY / model access.)_"
        )
        return {
            "answer": fallback + note,
            "sources": sources,
            "generation": "retrieval_only",
            "mode": "retrieval_only",
            "groq_error": type(exc).__name__,
        }
