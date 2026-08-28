# BharatBot

A FastAPI lab that answers questions from **10 local Indian history chunks**, then (if a Groq key is set) generates with `llama-3.3-70b-versatile`.

It is not a general chatbot. The corpus is one file, `data/kingdoms/early_kingdoms.json`: Indus Valley, Ikshvaku, Kuru, Magadha, the sixteen Mahajanapadas, Maurya, Vedic period, Gupta, Hinduism origins, and the Tamil Chera/Chola/Pandya kingdoms. Retrieval is ChromaDB collection `indian_history` with `all-MiniLM-L6-v2`.

This is a **lab**. Not a product. No public demo was running in this pass.

Author: **Harsha Nandhan Reddy Gajulapalli**  
Email: **harshanandhanreddy820@gmail.com**  
GitHub: [Harshanandhan](https://github.com/Harshanandhan)

## Run

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
# put a real GROQ_API_KEY in .env
python -m uvicorn main:app --host 127.0.0.1 --port 8001
```

`python start.py` is the same server, but it ingests into `./chroma_db` first if collection `indian_history` is missing. Default port is **8001** (`PORT` overrides it). `rag.py` reads `GROQ_API_KEY`. There is no Anthropic path.

## Results

Local run on Windows, Python 3.12.10, **2026-08-27** (ET). JSON: `results/http.json`. Import probe: `results/imports.json`.

`uvicorn main:app` on `127.0.0.1:8001`:

| Call | Result |
|---|---|
| `GET /health` | **200** `{"status":"ok"}` |
| `GET /` | **200** `static/index.html` (10605 bytes) |
| `POST /ask` empty question | **400** `Question cannot be empty` |
| `POST /ask` `Who was Ashoka?` | **500** — `import chromadb` failed |

`GROQ_API_KEY` was **not set**. No chat answer was generated. Do not treat this README as a model eval.

`chromadb==0.5.23` (the original pin) failed to build `chroma-hnswlib` on this machine (needs MSVC). `chromadb==1.5.9` installed from a Windows wheel, then **Windows Application Control blocked the `orjson` DLL**, so ingest and `/ask` never reached Groq or MiniLM. `anthropic` is not installed; `groq==1.7.0` imports.

`GET /health` does not load Chroma, MiniLM, or Groq. `POST /ask` does.

## Layout

```
main.py                          GET /  GET /health  POST /ask
rag.py                           retrieve + Groq llama-3.3-70b-versatile
ingest.py                        embed data/kingdoms/*.json into Chroma
start.py                         ingest if empty, then uvicorn
static/index.html                chat UI
data/kingdoms/early_kingdoms.json  10 chunks
results/                         log + JSON from the run above
```

## License

MIT. Copyright (c) 2026 Harsha Nandhan Reddy Gajulapalli.