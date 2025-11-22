from smolagents import Tool

class FileReader(Tool):
    name = "file_reader"
    description = "Read the content from a file."
    inputs = {
        "filename": {
            "type": "string",
            "description": "the filename to read from."
        }
    }
    
    output_type = "string"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def forward(self, filename: str) -> str:
        # Read the content of the file and return it.
        with open(filename, "r") as file:
            content = file.read()
        return content

