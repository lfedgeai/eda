from smolagents import Tool

class FileWriter(Tool):
    name = "file_writer"
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
        with open(filename, "w") as file:
            file.write(scripts)  # Writing query as placeholder, may need to adjust logic

        return f"Code saved to {filename}."
        
