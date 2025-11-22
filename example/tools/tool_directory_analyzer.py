from smolagents import Tool

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
