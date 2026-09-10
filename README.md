# BharatBot

A **lab** FastAPI RAG app over **10 local Indian history chunks** (ChromaDB + `all-MiniLM-L6-v2`). Optional Groq generation (`llama-3.3-70b-versatile`) when `GROQ_API_KEY` is set and the model call succeeds. If the key is missing or Groq fails, `/ask` returns an honest **retrieval-only** extractive answer with sources — it does **not** 500 the UI.

It is not a general chatbot and not a production product. The corpus is one file, `data/kingdoms/early_kingdoms.json`: Indus Valley, Ikshvaku, Kuru, Magadha, the sixteen Mahajanapadas, Maurya, Vedic period, Gupta, Hinduism origins, and the Tamil Chera/Chola/Pandya kingdoms. Retrieval uses ChromaDB collection `indian_history`.

Author: **Harsha Nandhan Reddy Gajulapalli**  
Email: **harshanandhanreddy820@gmail.com**  
GitHub: [Harshanandhan](https://github.com/Harshanandhan)

## Live URL

Deployed on Railway (single service: FastAPI + static UI):

- **App:** https://REPLACE_AFTER_DEPLOY.up.railway.app
- **Health:** `GET /health` → `{status, chunks, groq}`
- **Ask:** `POST /ask` with `{"question":"..."}` → `{answer, sources, generation, mode}`

Without `GROQ_API_KEY`, mode is `retrieval_only`. To enable Groq generation on Railway: Project → Variables → set `GROQ_API_KEY` to a real key that can call `llama-3.3-70b-versatile`, then redeploy/restart.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
# optional: put a real GROQ_API_KEY in .env
python start.py
```

`python start.py` ingests into `./chroma_db` if collection `indian_history` is missing, then serves on `$PORT` (default **8001**).

## API

| Call | Behavior |
|---|---|
| `GET /` | Chat UI (Indian heritage theme) |
| `GET /health` | `{status, chunks, groq}` — never fails if Chroma cold (`chunks` may be `null`) |
| `POST /ask` | `{answer, sources[{title,era,snippet}], generation, mode}` — `groq` or `retrieval_only` |

## Layout

```
main.py                          GET /  GET /health  POST /ask
rag.py                           retrieve + optional Groq; retrieval_only fallback
ingest.py                        embed data/kingdoms/*.json into Chroma
start.py                         ingest if empty, then uvicorn ($PORT)
static/index.html                distinctive chat UI + source chips + mode badge
data/kingdoms/early_kingdoms.json  10 chunks
railway.toml / nixpacks.toml     Railway deploy
```

## License

MIT. Copyright (c) 2026 Harsha Nandhan Reddy Gajulapalli.