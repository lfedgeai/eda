import os
import yaml
import datetime
import chromadb
from chromadb.config import Settings as ChromaSettings
from smolagents import Tool
from sentence_transformers import SentenceTransformer

# Registry helper functions
REGISTRY_FILE = "data_registry.yaml"

def load_registry():
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, "r") as f:
            return yaml.safe_load(f) or []
    return []

def find_entry(data_dir, registry):
    abs_data_dir = os.path.abspath(data_dir)
    return next((e for e in registry if os.path.abspath(e["data_directory"]) == abs_data_dir), None)

class ChromaRAGTool(Tool):
    name = "chroma_rag_tool"
    description = "Performs RAG using ChromaDB and manages data via registry."
    
    inputs = {
        "data_dir": {"type": "string", "description": "Directory with data files."},
        "question": {"type": "string", "description": "Query question."},
        "top_k": {"type": "integer", "description": "Number of similar docs to retrieve."}
    }
    output_type = "string"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    def forward(self, data_dir: str, question: str, top_k: int) -> str:
        # Load registry and check for an existing entry
        registry = load_registry()
        entry = find_entry(data_dir, registry)
        
        # Determine cache directory: use registry entry if exists; otherwise, create one.
        cache_dir = entry["cache_file_directory"] if entry else os.path.join(data_dir, ".cache/chroma_db")
        os.makedirs(cache_dir, exist_ok=True)

        # Initialize Chroma client with local persistence.
        client = chromadb.Client(ChromaSettings(persist_directory=cache_dir))
        collection_name = "rag_collection"

        # If no registry entry or the collection doesn't exist, build a new index.
        if not entry or collection_name not in [c.name for c in client.list_collections()]:
            if collection_name in [c.name for c in client.list_collections()]:
                client.delete_collection(collection_name)
            collection = client.create_collection(collection_name)

            documents = []
            doc_ids = []
            for root, _, files in os.walk(data_dir):
                for file in files:
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            text = f.read()
                            documents.append(text)
                            doc_ids.append(path)
                    except Exception as e:
                        print(f"Error reading {path}: {e}")
                        continue

            if documents:
                embeddings = self.embedding_model.encode(documents).tolist()
                collection.add(documents=documents, embeddings=embeddings, ids=doc_ids)
            else:
                return "No valid text documents found to index."
        else:
            collection = client.get_collection(collection_name)

        # Encode the query and retrieve results.
        query_embedding = self.embedding_model.encode(question).tolist()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "distances"]
        )

        # Format the output.
        output = "RAG Query Results:\n"
        for doc, dist in zip(results["documents"][0], results["distances"][0]):
            output += f"Doc (score {dist:.3f}): {doc[:150]}...\n\n"
        return output
