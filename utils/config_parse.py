import sys
from pathlib import Path

from utils.data_file_handle import load_data_file


def get_base_path():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


def parse_config():
    base_path = get_base_path()
    config_file = base_path / 'config.json'

    if not config_file.exists():
        raise FileNotFoundError(
            f'Config file not found: {config_file}. Please ensure copying the `config.json` to next to the executable.')

    config_data = load_data_file(config_file)
    parsed_config = {}

    for key, value in config_data.items():
        if isinstance(value, str):
            value = value.strip()
        parsed_config[key] = value

    return parsed_config


config = parse_config()
