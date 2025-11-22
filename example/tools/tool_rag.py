"""
pip install llama-index
pip install llama-index-embeddings-huggingface
"""
import os
import datetime
import yaml
from smolagents import Tool

from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Settings,
)
from llama_index.core.llms import MockLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# ------------------------------------------------------------------------------
# Configure LlamaIndex
# ------------------------------------------------------------------------------
Settings.llm = MockLLM()
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# ------------------------------------------------------------------------------
# Registry utility functions
# ------------------------------------------------------------------------------
REGISTRY_FILE = "data_registry.yaml"

def load_registry() -> list:
    """Loads the registry from a YAML file or returns an empty list if it doesn't exist."""
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, "r") as f:
            data = yaml.safe_load(f)
        return data if data else []
    return []

def save_registry(registry: list):
    """Saves the registry back to the YAML file."""
    with open(REGISTRY_FILE, "w") as f:
        yaml.safe_dump(registry, f)

def find_registry_entry(data_directory: str, registry: list) -> dict | None:
    """
    Looks for a registry entry matching 'data_directory' (by absolute path).
    Returns the entry if found, else None.
    """
    abs_data_dir = os.path.abspath(data_directory)
    for entry in registry:
        if os.path.abspath(entry.get("data_directory", "")) == abs_data_dir:
            return entry
    return None

def update_registry_entry(
    data_directory: str,
    cache_file_directory: str,
    last_data_update: float,
    status: str = "rag_indexed",
    data_format: str = "",
):
    """
    Inserts or updates a registry entry for this data_directory. 
    Also stores the last_data_update (timestamp in seconds).
    """
    registry = load_registry()
    abs_data_dir = os.path.abspath(data_directory)
    abs_cache_dir = abs_data_dir + "/.cache"

    # Minimal new/updated entry
    new_entry = {
        "data_directory": abs_data_dir,
        "cache_file_directory": abs_cache_dir,
        "data_format": data_format,
        "timestamp": datetime.datetime.now().isoformat(),  # When this registry entry was updated
        "status": status,
        "last_data_update": last_data_update,             # float -> last mod time in seconds
        "metadata": {},  # Optionally fill with more details
    }

    updated = False
    for i, entry in enumerate(registry):
        if os.path.abspath(entry.get("data_directory", "")) == abs_data_dir:
            registry[i] = new_entry
            updated = True
            break

    if not updated:
        registry.append(new_entry)

    save_registry(registry)

def get_latest_mod_time(data_directory: str) -> float:
    """
    Returns the most recent (max) last-modified time (in seconds) 
    of all files under data_directory.
    """
    latest_time = 0.0
    for root, _, files in os.walk(data_directory):
        for f in files:
            filepath = os.path.join(root, f)
            mtime = os.path.getmtime(filepath)
            if mtime > latest_time:
                latest_time = mtime
    return latest_time

# ------------------------------------------------------------------------------
# RAGTool with data update checks
# ------------------------------------------------------------------------------
class RAGTool(Tool):
    name = "rag_tool"
    description = "A RAG tool that queries a document using a vector index, integrating with the data registry."

    inputs = {
        "data_dir": {
            "type": "string",
            "description": "The directory of data to be retrieved and indexed."
        },
        "question": {
            "type": "string",
            "description": "The query question for retrieval."
        },
        "similarity_top_k": {
            "type": "string",
            "description": "Number of top similar docs to retrieve (string -> int)."
        }
    }
    output_type = "string"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def forward(self, data_dir: str, question: str, similarity_top_k: str) -> str:
        """
        Main entry point for the RAG tool.
        1. Determine the cache directory from the registry (or create it).
        2. Check if raw data is updated (compare directory's last mod time to registry).
        3. Load or rebuild the vector index accordingly.
        4. Query with 'similarity_top_k' and return result text.
        """
        registry = load_registry()
        entry = find_registry_entry(data_dir, registry)

        # 1. Determine the relevant cache directory
        if entry and "cache_file_directory" in entry and entry["cache_file_directory"]:
            persist_dir = entry["cache_file_directory"]
            print(f"Found registry entry for {data_dir}. Using cache: {persist_dir}")
        else:
            # No entry found, create a new .cache directory under data_dir
            persist_dir = os.path.join(data_dir, ".cache", "storage")
            os.makedirs(persist_dir, exist_ok=True)
            print(f"No registry entry found for {data_dir}. Created new cache folder: {persist_dir}")

        # 2. Check if raw data is updated
        latest_data_mtime = get_latest_mod_time(data_dir)  # in seconds
        registry_last_data_update = entry["last_data_update"] if entry else 0.0

        need_rebuild = False
        reason = ""

        # If no index folder, or raw data has new modifications, we must rebuild
        if not os.path.exists(persist_dir) or not os.listdir(persist_dir):
            reason = "No existing index found"
            need_rebuild = True
        elif latest_data_mtime > registry_last_data_update:
            reason = "Data directory has been updated"
            need_rebuild = True

        if need_rebuild:
            print(f"[INFO] Rebuilding index because: {reason}")
            documents = SimpleDirectoryReader(data_dir).load_data()
            index = VectorStoreIndex.from_documents(documents)
            index.storage_context.persist(persist_dir=persist_dir)

            # Update the registry
            update_registry_entry(
                data_directory=data_dir,
                cache_file_directory=persist_dir,
                last_data_update=latest_data_mtime, 
                status="rag_indexed"
            )
        else:
            # 3. Otherwise, load the existing index
            print(f"[INFO] Loading existing index from {persist_dir} ...")
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            index = load_index_from_storage(storage_context)

        # 4. Query with top_k
        k = int(similarity_top_k)
        query_engine = index.as_query_engine(similarity_top_k=k)
        response = query_engine.query(question)

        # 5. Compile output with source info
        output = "-----\n"
        for node in response.source_nodes:
            text_fmt = node.node.get_content().strip().replace("\n", " ")
            output += f"Text:\t {text_fmt}\n"
            output += f"Metadata:\t {node.node.metadata}\n"
            output += f"Score:\t {node.score:.3f}\n"
        return output