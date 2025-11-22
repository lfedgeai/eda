import logging
import subprocess
from smolagents import Tool

class PipInstall(Tool):
    name = "tool_pip_install"
    description = "Install Python packages using pip."
    inputs = {
        "packages": {
            "type": "string",
            "description": "A space-separated string of package names to install.",
        }
    }
    output_type = "string"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def forward(self, packages: str) -> str:
        return self.install_packages(packages)
    
    def install_packages(self, packages):
        """
        Install the specified Python packages using pip.

        Args:
            packages (list or str): A list of package names or a space-separated string of package names.

        Returns:
            str: A message indicating the success or failure of the installation.
        """
        if isinstance(packages, str):
            packages = packages.split()

        try:
            # Construct the pip install command
            command = ['pip3', 'install'] + packages
            logging.info(f"Installing packages: {' '.join(packages)}")
            
            # Execute the pip install command
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            success_message = f"Successfully installed packages: {', '.join(packages)}"
            logging.info(success_message)
            return success_message

        except subprocess.CalledProcessError as e:
            error_message = f"Failed to install packages: {', '.join(packages)}\nError: {e.stderr.decode().strip()}"
            logging.error(error_message)
            return error_message
 