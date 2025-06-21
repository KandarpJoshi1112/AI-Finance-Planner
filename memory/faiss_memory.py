from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.IndexFlatL2(384)

def add_texts(texts: list[str]):
    embeddings = model.encode(texts)
    index.add(np.array(embeddings))

def query_text(query: str, k=3):
    q_embedding = model.encode([query])
    D, I = index.search(np.array(q_embedding), k)
    return I.tolist()
