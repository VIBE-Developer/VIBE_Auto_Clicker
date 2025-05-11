import os
import json

BASE_DIR = "data/macros"
def save_app_config(config):
    os.makedirs("data", exist_ok=True)  # 🛠 гарантируем, что папка есть
    with open("data/config.json", "w") as f:
        json.dump(config, f, indent=4)

def ensure_folder(mode):
    path = os.path.join(BASE_DIR, mode)
    os.makedirs(path, exist_ok=True)
    return path

def save_macro(name, data, mode="active"):
    path = ensure_folder(mode)
    full_path = os.path.join(path, f"{name}.json")
    with open(full_path, "w") as f:
        json.dump(data, f, indent=2)

def load_macro(name, mode="active"):
    path = os.path.join(BASE_DIR, mode, f"{name}.json")
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)

def list_macros(mode="active"):
    path = ensure_folder(mode)
    return [f.replace(".json", "") for f in os.listdir(path) if f.endswith(".json")]

def load_app_config():
    path = "data/config.json"
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(path):
        default = {"first_run": True, "last_mode": "active"}
        save_app_config(default)
        return default
    with open(path, "r") as f:
        return json.load(f)

def save_app_config(config):
    os.makedirs("data", exist_ok=True)
    with open("data/config.json", "w") as f:
        json.dump(config, f, indent=4)
