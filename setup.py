import os
import subprocess
from pathlib import Path
from shutil import copyfile

# -------- Project structure --------
FOLDERS = [
    "agents",
    "envs",
    "data",
    "dash",
    "api",
    "docs",
    "memory",
    "tests"
]

FILES = {
    ".env.example": """# Example environment file
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
PINECONE_API_KEY=your_key_here
PINECONE_ENV=your_env
""",
    "api/main.py": """from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"msg": "AI Planner Backend Running"}
""",
    "memory/faiss_memory.py": """from sentence_transformers import SentenceTransformer
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
""",
    "requirements.txt": """fastapi
uvicorn
pydantic
python-dotenv
pandas
numpy
requests
transformers
sentence-transformers
faiss-cpu
yfinance
alpaca-trade-api
langchain
langgraph"""
}


def create_folders():
    for folder in FOLDERS:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created folder: {folder}")


def create_files():
    for path, content in FILES.items():
        full_path = Path(path)
        if not full_path.exists():
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)
            print(f"✅ Created file: {path}")


def create_env():
    if not Path(".env").exists():
        copyfile(".env.example", ".env")
        print("✅ .env created from .env.example")
    else:
        print("ℹ️  .env already exists")



if __name__ == "__main__":
    print("🚀 Setting up Personal Financial Planner Project...")
    create_folders()
    create_files()
    create_env()
    print("\n🎉 Setup complete! You're ready to start coding.")
