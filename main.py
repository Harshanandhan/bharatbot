from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="BharatBot — Indian History Chatbot")
app.mount("/static", StaticFiles(directory="static"), name="static")


class Query(BaseModel):
    question: str
    history: list[dict] | None = None


@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask_question(query: Query):
    if not query.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    from rag import ask
    result = ask(query.question, query.history)
    return result
