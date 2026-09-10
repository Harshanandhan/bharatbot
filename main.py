from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="BharatBot — Indian History Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


class Query(BaseModel):
    question: str
    history: list[dict] | None = None


@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    """Richer health without failing if Chroma is cold."""
    payload = {"status": "ok", "chunks": None, "groq": False}
    try:
        from rag import collection_count, groq_configured

        payload["chunks"] = collection_count()
        payload["groq"] = groq_configured()
    except Exception:
        pass
    return payload


@app.post("/ask")
def ask_question(query: Query):
    if not query.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    from rag import ask

    return ask(query.question, query.history)
