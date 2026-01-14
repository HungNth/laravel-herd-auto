from pathlib import Path

from utils.data_file_handle import load_data_file


def parse_config():
    config_file = Path(__file__).parent.parent / 'config.json'
    print(config_file)
    config_data = load_data_file(config_file)
    parsed_config = {}

    for key, value in config_data.items():
        if isinstance(value, str):
            value = value.strip()
        parsed_config[key] = value

    return parsed_config
