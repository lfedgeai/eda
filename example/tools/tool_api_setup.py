import os
import subprocess
from smolagents import tool

@tool
def api_setup(MODEL_API_KEY_NAME: str, API_KEY: str) -> str:
    """
    Sets an environment variable for the API key.
    """
    try:
        os.environ[MODEL_API_KEY_NAME] = API_KEY
        subprocess.run(f"export {MODEL_API_KEY_NAME}={API_KEY}", shell=True, check=True)
        return "Successfully installed API key"
    except Exception as e:
        return f"Error setting API key: {str(e)}"