# BharatBot

A **lab** FastAPI RAG app over **10 local Indian history chunks** (ChromaDB + `all-MiniLM-L6-v2`). If a Groq key is set **and** that key can call the pinned chat model, `rag.py` generates with `llama-3.3-70b-versatile`. Generation is optional and was **not** proven end-to-end in the latest local pass.

It is not a general chatbot and not a product. The corpus is one file, `data/kingdoms/early_kingdoms.json`: Indus Valley, Ikshvaku, Kuru, Magadha, the sixteen Mahajanapadas, Maurya, Vedic period, Gupta, Hinduism origins, and the Tamil Chera/Chola/Pandya kingdoms. Retrieval uses ChromaDB collection `indian_history`.

No public demo was running in this pass.

Author: **Harsha Nandhan Reddy Gajulapalli**  
Email: **harshanandhanreddy820@gmail.com**  
GitHub: [Harshanandhan](https://github.com/Harshanandhan)

## Run

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
# optional: put a real GROQ_API_KEY in .env (must have access to the pinned model)
python -m uvicorn main:app --host 127.0.0.1 --port 8001
```

`python start.py` is the same server, but it ingests into `./chroma_db` first if collection `indian_history` is missing. Default port is **8001** (`PORT` overrides it). `rag.py` reads `GROQ_API_KEY`. There is no Anthropic path.

## Results

Local run on Windows, Python **3.13.13**, **2026-09-09** (ET / America/New_York). JSON: `results/http.json`. Import probe: `results/imports.json`. Notes: `results/run.txt`.

`uvicorn main:app` on `127.0.0.1:8001`:

| Call | Result |
|---|---|
| `GET /health` | **200** `{"status":"ok"}` |
| `GET /` | **200** `static/index.html` (~10253 bytes) |
| `POST /ask` empty question | **400** |
| `POST /ask` `Who was Ashoka?` | **500** — Groq `model_not_found` for `llama-3.3-70b-versatile` |

Local-only path that **did** work this pass:

- `pip install -r requirements.txt` (pins include `chromadb==1.5.9`, `groq==1.7.0`)
- Imports: `chromadb`, `sentence_transformers`, `orjson`, `fastapi`, `uvicorn`, `groq`
- Chroma collection `indian_history` **count=10**
- Direct `retrieve("Who was Ashoka?")` → Maurya Empire, Magadha Kingdom, Sixteen Mahajanapadas (MiniLM + Chroma)

`GROQ_API_KEY` was **SET**. `models.list()` for this key did **not** include `llama-3.3-70b-versatile`, so no chat answer was generated. Do not treat this README as a model eval or production readiness claim.

Earlier pass (**2026-08-27**, Python 3.12.10): `/health` worked but `import chromadb` failed under Windows Application Control on `orjson`; that block did **not** reproduce on 2026-09-09.

`GET /health` does not load Chroma, MiniLM, or Groq. `POST /ask` loads retrieve then Groq.

## Layout

```
main.py                          GET /  GET /health  POST /ask
rag.py                           retrieve + Groq llama-3.3-70b-versatile (if key+model)
ingest.py                        embed data/kingdoms/*.json into Chroma
start.py                         ingest if empty, then uvicorn
static/index.html                chat UI
data/kingdoms/early_kingdoms.json  10 chunks
results/                         log + JSON from local runs
```

## License

MIT. Copyright (c) 2026 Harsha Nandhan Reddy Gajulapalli.
