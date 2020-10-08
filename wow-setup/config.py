import json
from pathlib import Path


config_path = Path(__file__) / ".." / ".." / "config.json"
with open(config_path, "r") as file:
    config = json.load(file)

# Region and Locale
region = config.get("REGION", None)
REGION = region.upper() if region.upper() in ["US", "EU"] else None
if not REGION:
    raise ValueError("Invalid REGION in config.json")
locale = {"US": "enus", "EU": "engb"}
LOCALE = locale[REGION]
# Accounts info
ACCOUNTS = config.get("ACCOUNTS", None)
# Paths
GAME_PATH = config.get("GAME_PATH", None)
SETUP_PATH = config.get("SETUP_PATH", None)
BACKUP_PATH = config.get("BACKUP_PATH", None)
RESTORE_PATH = config.get("RESTORE_PATH", None)
# Default Files paths
DEFAULT_CONFIG = config.get("DEFAULT_CONFIG", None)
DEFAULT_SV = config.get("DEFAULT_SV", None)
DEFAULT_ADDONS = config.get("DEFAULT_ADDONS", None)
# Addon names, used for the copy SavedVariables feature
ADDON_NAMES = config.get("ADDON_NAMES", [])
