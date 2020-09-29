# SETUP

- pip install venv
- install requirements.txt
- config

# What it needs to do

- [x] initial setup
  - [x] create folders ('wow{x}/_retail_/WTF')
  - [x] symlink data
  - [x] symlink addons
  - [x] copy exe - standalone utility for later too
  - [x] Config.wtf from base dependency
    - [x] set 'accountName', 'accountList' for each individually
- [ ] post launching wow and getting account folders
  - [ ] savedVariables shortcuts
  - [ ] addons folder shortcut
  - [ ] Addons default savedvariables copy (elvui, weakauras, abp, moveanything)
- [ ] improvements
  - [ ] MultiboxUtils account number
- [ ] backup functionality

# Python os utilities

- pathlib
- os.mkdirs vs pathlib.mkdir
- shutil

# Config

SET portal "US"
SET agentUID "wow_enus"
SET accountName "aschulz9494@gmail.com"
SET accountList "WoW4|WoW5|WoW3|WoW2|!WoW1|"