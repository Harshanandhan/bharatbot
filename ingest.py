import json
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path


def load_chunks():
    chunks = []
    data_dir = Path("data/kingdoms")
    for f in sorted(data_dir.glob("*.json")):
        with open(f, encoding="utf-8") as fp:
            data = json.load(fp)
            chunks.extend(data["chunks"])
    return chunks


def ingest():
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Loading data chunks...")
    chunks = load_chunks()
    print(f"Found {len(chunks)} chunks across all files.")

    client = chromadb.PersistentClient(path="./chroma_db")

    try:
        client.delete_collection("indian_history")
        print("Cleared existing collection.")
    except Exception:
        pass

    collection = client.create_collection(
        name="indian_history",
        metadata={"hnsw:space": "cosine"}
    )

    texts = [c["content"] for c in chunks]
    ids = [c["id"] for c in chunks]
    metadatas = []
    for c in chunks:
        # ChromaDB metadata values must be str/int/float/bool
        meta = {}
        for k, v in c["metadata"].items():
            if isinstance(v, list):
                meta[k] = ", ".join(str(i) for i in v)
            elif isinstance(v, bool):
                meta[k] = v
            else:
                meta[k] = str(v)
        metadatas.append(meta)

    print(f"Embedding {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    collection.add(
        documents=texts,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )
    print(f"\nDone. {len(texts)} chunks stored in ChromaDB at ./chroma_db")


if __name__ == "__main__":
    ingest()
