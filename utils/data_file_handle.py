import json
from pathlib import Path


def load_data_file(data_file):
    if Path(data_file).exists():
        try:
            with open(data_file, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_data_file(data_file, data: dict):
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)
