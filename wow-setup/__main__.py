import sys
import os
import ctypes
import shutil
from pathlib import Path

from .config import SETUP_PATH, GAME_PATH, ACCOUNTS, DEFAULT_CONFIG, REGION, LOCALE


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
        # Root paths for account folders
        self.accounts = []
        for idx, info in enumerate(ACCOUNTS):
            self.accounts.append({
                'path': self.setup_path / f'wow{idx}',
                'email': info.get('email', ''),
                'license_num': info.get('license_num', 1),
                'account_id': info.get('account_id', None)
            })
        
        # Create config.wtf string template
        important_variables = ['accountName', 'accountList', 'portal', 'agentUID']
        # Lines we want to modify
        substitution_lines = '\n'.join([
            'SET portal "{region}"',
            'SET agentUID "wow_{locale}"',
            'SET accountName "{email}"',
            'SET accountList "{license_num}"'
        ])
        other_lines = []
        with open(Path(DEFAULT_CONFIG)) as f:
            config_lines = f.read().splitlines()
            for line in config_lines:
                variable_name = line.split(' ')[1]
                if variable_name in important_variables:
                    continue
                other_lines.append(line)
        other_lines = '\n'.join(other_lines)

        self.config_template = f'{substitution_lines}\n{other_lines}'


    def create_modified_config_string(self, email, license_num):
        substitutes = {
            'region': REGION,
            'locale': LOCALE,
            'email': email,
            'license_num': f'!WoW{license_num}'
        }
        return self.config_template.format(**substitutes)

    def copy_executables(self):
        for account in self.accounts:
            root_path = account['path']
            shutil.copy2(self.exe_path, root_path / '_retail_')

    def create_folders(self):
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
                config_string = self.create_modified_config_string(email, license_num)
                f.write(config_string)
            # Create symbolic links (Data + Interface)
            (root_path / '_retail_' / 'Interface').symlink_to(
                    self.interface_path, target_is_directory=True)
            (root_path / 'Data').symlink_to(
                    self.data_path, target_is_directory=True)
        # Copy wow.exe to each account folder
        self.copy_executables()

        
def main():
    s = Setup()
    s.create_folders()
    print(ctypes.windll.shell32.IsUserAnAdmin() != 0)


if __name__ == '__main__':
    main()
    
    