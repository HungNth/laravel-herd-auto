import json
import sys
from pathlib import Path


def load_data_file(file):
    if Path(file).exists():
        try:
            with open(file, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    else:
        print(f"File does not exist: {file}")
        sys.exit(0)


def save_data_file(file, data: dict):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)
