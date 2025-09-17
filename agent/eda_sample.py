"""
pip install llama-index
pip install llama-index-embeddings-huggingface
"""
import os
from smolagents import ToolCallingAgent, LiteLLMModel, CodeAgent
import yaml

from smolagents import Tool

class RAGTool(Tool):
    name = "rag_tool"
    description = "Queries a document collection using a vector index with caching support."
    
    inputs = {
        "data_dir": {
            "type": "string",
            "description": "Directory containing source documents."
        },
        "question": {
            "type": "string",
            "description": "The query to execute."
        },
        "similarity_top_k": {
            "type": "string",
            "description": "The number of top similar documents to retrieve (as a string that converts to int)."
        }
    }
    output_type = "string"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set up embedding model (LLM is not needed here as the agent handles LLM calls)
        from llama_index.core import Settings       
        from llama_index.core.llms import MockLLM
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        Settings.llm = MockLLM()  # Not used in this tool
        Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

    def forward(self, data_dir: str, question: str, similarity_top_k: str) -> str:
        # Determine the cache directory for the vector index
        persist_dir = os.path.join(data_dir, ".cache", "storage")

        if not os.path.exists(persist_dir):
            print(f"[INFO] Rebuilding index for '{data_dir}'.")
            os.makedirs(persist_dir, exist_ok=True)            
            # Load documents and build the vector index
            from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
            documents = SimpleDirectoryReader(data_dir).load_data()
            index = VectorStoreIndex.from_documents(documents)
            index.storage_context.persist(persist_dir=persist_dir)
        else:
            print(f"[INFO] Loading cached index from '{persist_dir}'.")
            from llama_index.core import StorageContext, load_index_from_storage
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            index = load_index_from_storage(storage_context)

        # Execute the query with the specified top_k
        k = int(similarity_top_k)
        query_engine = index.as_query_engine(similarity_top_k=k)
        response = query_engine.query(question)

        # Format the output with source text, metadata, and similarity scores
        output = "-----\n"
        for node in response.source_nodes:
            content = node.node.get_content().strip().replace("\n", " ")
            output += f"Text:\t{content}\n"
            output += f"Metadata:\t{node.node.metadata}\n"
            output += f"Score:\t{node.score:.3f}\n"
        return output

class DirectoryAnalyzer(Tool):
    """
    A SmolAgents tool that analyzes a directory and returns detailed metadata
    including file sizes, types, and counts of files and subdirectories.
    """
    name = "directory_analyzer"
    description = "Analyzes an input directory and returns detailed file and folder info, including file types and sizes."
    inputs = {
        "directory_path": {
            "type": "string",
            "description": "The path of the directory to analyze."
        }
    }
    output_type = "string"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def forward(self, directory_path: str) -> str:
        from subprocess import check_output, CalledProcessError
        try:
            # Use the 'ls' and 'du' commands to gather detailed information
            output = check_output(['ls', '-lR', directory_path], text=True)
        except CalledProcessError as e:
            return f"An error occurred: {e}"
        return output

class CodeFileWriter(Tool):
    name = "code_file_writer"
    description = "Write the code to a file."
    inputs = {
        "filename":{
            "type": "string",
            "description": "the filename to write the code to."
        },
        "scripts": {
            "type": "string",
            "description": "the python scripts to write to a file",
        }
    }
    
    output_type = "string"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def forward(self, filename: str, scripts: str) -> str:  # Matching `inputs` key
        # Save the generated code to a file
        filename = "./generated_agent.py" #overwrite filename for now. 
        with open(filename, "w") as file:
            file.write(scripts)  # Writing query as placeholder, may need to adjust logic

        return f"Code saved to {filename}."

class FilePreviewer(Tool):
    name = "file_previewer"
    description = "Preview contents of a text file."
    inputs = {
        "file_path": {
            "type": "string",
            "description": "Path to the file to preview."
        }
    }
    output_type = "string"

    def forward(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read(1000)  # limit to first 1k characters


# 
def eda_by_smol(task):

    with open("prompts/custom_agent.yaml", 'r') as stream:
        prompt_templates = yaml.safe_load(stream)

    with open("prompts/data_analysis_agent.yaml", 'r') as stream:
        data_viewer_prompt_templates = yaml.safe_load(stream)

    coder = CodeAgent(
        name="coding_agent",
        description="implement the idea into an agent code",
        tools=[CodeFileWriter()],
        model=LiteLLMModel(model_id="xai/grok-3-latest")
        )

    viewer = ToolCallingAgent(
        prompt_templates=data_viewer_prompt_templates,
        name="data_viewer_agent",
        description="an agent can retrieve or view the file direclty, and return the data schema",
        tools=[RAGTool(), FilePreviewer()],
        model=LiteLLMModel(model_id="xai/grok-3-latest")
        )

    agent = ToolCallingAgent(
        prompt_templates=prompt_templates,
        tools=[DirectoryAnalyzer()],
        model=LiteLLMModel(model_id="xai/grok-3-latest"),#gemini/gemini-1.5-pro
        #managed_agents=[viewer, coder], #pipeline may work better
    )

    response = agent.run(task)
    response1 = viewer.run(task +response)
    response2 = coder.run(task + response1)

    return response2