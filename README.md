# SETUP

- `python -m venv --system-site-packages env`
- `env\Scripts\Activate.bat`
- `pip install -U -r requirements.txt`

# Only freeze local venv packages

- `pip freeze --local > requirements.txt`

# What it needs to do

- [x] initial setup
  - [x] create folders ('wow{x}/_retail_/WTF')
  - [x] symlink data
  - [x] symlink addons
  - [x] copy exe - standalone utility for later too
  - [x] Config.wtf from base dependency
    - [x] set 'accountName', 'accountList' for each individually
- [x] post launching wow and getting account folders
  - [x] savedVariables shortcuts
  - [x] addons folder shortcut
  - [x] optional: copy addons from default to game path
  - [x] Addons default savedvariables copy (elvui, weakauras, abp, moveanything)
- [x] improvements
  - [x] MultiboxUtils account number
- [x] backup functionality
  - [x] WTF folders as a whole
  - [x] AddOns folder
- [x] individual saved var copy from main wow account to rest
  - [x] set addon names for which we want to be able to copy_sv for

# Python os utilities

- pathlib
- shutil

# Config

SET portal "US"
SET agentUID "wow_enus"
SET accountName "a@gmail.com"
SET accountList "WoW4|WoW5|WoW3|WoW2|!WoW1|"
