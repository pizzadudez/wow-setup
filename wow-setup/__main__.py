import sys
import ctypes
import shutil
from pathlib import Path

from .config import (SETUP_PATH, GAME_PATH, ACCOUNTS, DEFAULT_CONFIG,
        DEFAULT_SV, DEFAULT_ADDONS, REGION, LOCALE)

class Setup:
    def __init__(self):
        self.is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

        # Account folders parent directory pathj
        self.setup_path = Path(SETUP_PATH)
        # Game installation paths
        self.game_path = Path(GAME_PATH)
        self.data_path = self.game_path / 'Data'
        self.interface_path = self.game_path / '_retail_' / 'Interface'
        self.exe_path = self.game_path / '_retail_' / 'Wow.exe'

        # Account properties dicts
        self.accounts = self._accounts()
        # Config template used to create Config.wtf files
        self._config_template = self._create_config_template()
        # Default saved variables lua files
        self.default_sv_files = [x for x in Path(DEFAULT_SV).glob('*.lua') if x.is_file()]

    def _accounts(self):
        """Generate list of account dictionaries."""

        _accounts = []
        for idx, info in enumerate(ACCOUNTS):
            account_path = self.setup_path / f'wow{idx}'
            # account_id folder only gets created after first login into acc
            account_id = info.get('account_id', None) or self.find_account_id(idx)
            # Saved Variables folder path
            sv_path = (account_path / '_retail_' / 'WTF' / 'Account' /
                    account_id / 'SavedVariables') if account_id else None

            _accounts.append({
                'path': account_path,
                'email': info.get('email', ''),
                'license_num': info.get('license_num', 1),
                'sv_path': sv_path         
            })
        
        return _accounts

    def _create_config_template(self):
        """Create template string from default Config.wtf file."""

        important_variables = ['accountName', 'accountList', 'portal', 'agentUID']
        # Lines we want to modify
        format_lines = '\n'.join([
            'SET portal "{region}"',
            'SET agentUID "wow_{locale}"',
            'SET accountName "{email}"',
            'SET accountList "{license_num}"'
        ])
        new_lines = [format_lines]
        with open(Path(DEFAULT_CONFIG)) as f:
            config_lines = f.read().splitlines()
            for line in config_lines:
                variable_name = line.split(' ')[1]
                if variable_name not in important_variables:
                    new_lines.append(line)

        return '\n'.join(new_lines)

    def get_config_string(self, email, license_num):
        "Return modified config string for specific account."

        substitutes = {
            'region': REGION,
            'locale': LOCALE,
            'email': email,
            'license_num': f'!WoW{license_num}'
        }

        return self._config_template.format(**substitutes)
        
    def find_account_id(self, account_idx):
        "Find account_id folder."
        
        #TODO will break if multiple accounts present

        account_folder = (self.setup_path / f'wow{account_idx}' / '_retail_' /
                'WTF' / 'Account')
        if not account_folder.exists():
            return None
        account_ids = [f.name for f in account_folder.iterdir() if f.is_dir() and '#' in f.name]
        
        return account_ids[0]

    def copy_executables(self):
        for account in self.accounts:
            root_path = account['path']
            shutil.copy2(self.exe_path, root_path / '_retail_')

    def copy_default_sv(self):
        "Copy or replace saved variables with defaults."

        for account in self.accounts:
            sv_path = account['sv_path'] or None
            if sv_path:
                for file in self.default_sv_files:
                    shutil.copy(file, sv_path)

    def create_multibox_utils(self):
        """Create MultiboxUtils.lua files to store acc_idx for in game use."""

        lua_table = 'MultiboxUtilsDB = {{ ["accountNumber"] = {acc_idx} }}'

        for acc_idx, account in enumerate(self.accounts):
            sv_path = account['sv_path'] or None
            if sv_path:
                with (sv_path / 'MultiboxUtils.lua').open('w') as f:
                    f.write(lua_table.format(acc_idx=acc_idx))

    def initial_setup(self):
        if not self.is_admin:
            raise Exception('Requires administrator privilleges')

        for account in self.accounts:
            root_path = account['path']
            # Create account folder tree
            wtf_path = (root_path / '_retail_' / 'WTF')
            wtf_path.mkdir(parents=True, exist_ok=True)
            # Create Config.wtf file
            with (wtf_path / 'Config.wtf').open('w') as f:
                email = account['email']
                license_num = account['license_num']
                config_string = self.get_config_string(email, license_num)
                f.write(config_string)
            # Create symbolic links (Data + Interface)
            (root_path / '_retail_' / 'Interface').symlink_to(
                    self.interface_path, target_is_directory=True)
            (root_path / 'Data').symlink_to(
                    self.data_path, target_is_directory=True)
                    
        # Copy wow.exe to each account folder
        self.copy_executables()

    def post_setup(self, copy_addons=False):
        if not self.is_admin:
            raise Exception('Requires administrator privilleges')

        # Automatically create MultiboxUtils.lua with corresponding accNumber
        self.create_multibox_utils()
        # Copy default SVs
        self.copy_default_sv()
        # Copy or replace game addons with default addons (from default folder)
        if copy_addons:
            addons_path = self.interface_path / 'AddOns'
            default_addons_path = Path(DEFAULT_ADDONS)
            shutil.rmtree(addons_path, ignore_errors=True)
            shutil.copytree(default_addons_path, addons_path)

        # SV folder shortcuts (symlinks)
        for account in self.accounts:
            sv_path = account['sv_path']
            sv_link_path = account['path'] / 'SavedVariables'
            if sv_path and not sv_link_path.is_symlink():
                sv_link_path.symlink_to(sv_path, target_is_directory=True)
        # addon folder shortcut (symlink) in setup folder
        addon_link_path = self.setup_path / 'AddOns'
        if not addon_link_path.is_symlink():
            addon_path = self.setup_path / 'AddOns'
            addon_link_path.symlink_to(addon_path, target_is_directory=True)

    def backup(self):
        # TODO implement wtf folders backup
        pass

    def restore_backup(self):
        # TODO implement wtf folders restore from backup
        pass

        
def main():
    s = Setup()
    action = sys.argv[1]
    if action == 'init':
        s.initial_setup()
    elif action == 'post':
        s.post_setup()


if __name__ == '__main__':
    main()
    
    