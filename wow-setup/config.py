import json
from pathlib import Path


config_path = Path(__file__) / '..' / '..' / 'config.json'
with open(config_path, 'r') as file:
    config = json.load(file)

SETUP_PATH = config.get('SETUP_PATH', None)
GAME_PATH = config.get('GAME_PATH', None)
ACCOUNTS = config.get('ACCOUNTS', None)
DEFAULT_CONFIG = config.get('DEFAULT_CONFIG', None)
DEFAULT_SV = config.get('DEFAULT_SV', None)
DEFAULT_ADDONS = config.get('DEFAULT_ADDONS', None)

region = config.get('REGION', None)
REGION = region.upper() if region.upper() in ['US', 'EU'] else None
if not REGION:
    raise ValueError('Invalid REGION in config.json')
locale = {'US': 'enus', 'EU': 'engb'}
LOCALE = locale[REGION]
