import json
from pathlib import Path


config_path = Path(__file__) / '..' / '..' / 'config.json'
with open(config_path, 'r') as file:
    config = json.load(file)

SETUP_PATH = config.get('SETUP_PATH', None)
GAME_PATH = config.get('GAME_PATH', None)
ACCOUNTS = config.get('ACCOUNTS', None)