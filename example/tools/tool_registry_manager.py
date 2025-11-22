import os
import yaml
import datetime
import shutil
from smolagents import Tool

class RegistryManager(Tool):
    name = "tool_registry_manager"
    description = (
        "Manage the data registry. Actions are: "
        "'update', 'list', and 'clear'."
    )
    inputs = {
        "action": {"type": "string", "description": "'update', 'list', or 'clear'."},
        "data_directory": {"type": "string", "description": "Data directory path.", "default": "", "nullable": True},
        "status": {"type": "string", "description": "Status of data processing.", "default": "", "nullable": True},
        "cache_file_directory": {"type": "string", "description": "Cache directory path.", "default": "", "nullable": True},
        "data_format": {"type": "string", "description": "Data format (e.g., pdf, csv).", "default": "", "nullable": True}
    }
    output_type = "string"

    REGISTRY_FILE = "data_registry.yaml"

    def load_registry(self):
        if os.path.exists(self.REGISTRY_FILE):
            with open(self.REGISTRY_FILE, "r") as f:
                return yaml.safe_load(f) or []
        return []

    def save_registry(self, registry):
        with open(self.REGISTRY_FILE, "w") as f:
            yaml.safe_dump(registry, f)

    def get_latest_mod_time(self, directory):
        latest_time = 0.0
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                latest_time = max(latest_time, os.path.getmtime(file_path))
        return latest_time

    def update(self, data_directory, status, cache_file_directory, data_format):
        data_dir = os.path.abspath(data_directory)
        cache_dir = os.path.abspath(cache_file_directory)
        last_mod_time = self.get_latest_mod_time(data_directory)

        new_entry = {
            "data_directory": data_directory,
            "cache_file_directory": cache_file_directory,
            "data_format": data_format,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": status,
            "last_data_update": last_mod_time,
        }

        registry = self.load_registry()
        found = False
        for idx, entry in enumerate(registry):
            if os.path.abspath(entry["data_directory"]) == os.path.abspath(data_directory):
                registry[idx] = new_entry
                found = True
                break
        if not found:
            registry.append(new_entry)

        self.save_registry(registry)
        return f"Updated registry entry for: {data_directory}"

    def list_entries(self):
        registry = self.load_registry()
        if not registry:
            return "Registry is empty."
        return yaml.safe_dump(registry, sort_keys=False)

    def clear_entries(self):
        registry = self.load_registry()
        for entry in registry:
            cache_dir = entry.get("cache_file_directory", "")
            if cache_file_directory and os.path.exists(cache_file_directory):
                shutil.rmtree(cache_file_directory, ignore_errors=True)
        if os.path.exists(self.REGISTRY_FILE):
            os.remove(self.REGISTRY_FILE)
            return "Registry and cache cleared."
        return "No registry file found."

    def forward(self, action, data_directory="", status="", cache_file_directory="", data_format=""):
        action = action.lower().strip()
        if action == "update":
            if not (data_directory and status and cache_file_directory and data_format):
                return "Provide data_directory, status, cache_file_directory, data_format."
            return self.update(data_directory, status, cache_file_directory, data_format)
        elif action == "list":
            return self.list_entries()
        elif action == "clear":
            return self.clear_entries()
        else:
            return "Invalid action specified."
