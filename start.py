import os
import chromadb
import uvicorn


def needs_ingest() -> bool:
    try:
        client = chromadb.PersistentClient(path="./chroma_db")
        col = client.get_collection("indian_history")
        return col.count() == 0
    except Exception:
        return True


if needs_ingest():
    print("Building vector store...")
    import ingest
    ingest.ingest()
    print("Vector store ready.")

port = int(os.getenv("PORT", 8001))
uvicorn.run("main:app", host="0.0.0.0", port=port)
