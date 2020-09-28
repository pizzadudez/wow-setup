import sys
import os
import ctypes
import shutil
from pathlib import Path

from .config import SETUP_PATH, GAME_PATH, ACCOUNTS

class Setup:
    def __init__(self):
        self.is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

        self.setup_path = Path(SETUP_PATH)
        self.game_path = Path(GAME_PATH)
        self.data_path = self.game_path / 'Data'
        self.interface_path = self.game_path / '_retail_' / 'Interface'
        self.exe_path = self.game_path / '_retail_' / 'Wow.exe'

        self.folders = [self.setup_path / f'wow{x}' for x in ACCOUNTS.keys()]
    
    def copy_executables(self):
        for folder_path in self.folders:
            shutil.copy2(self.exe_path, folder_path / '_retail_')

    def create_folders(self):
        if not self.is_admin:
            raise Exception('Requires administrator privilleges')
        for folder_path in self.folders:
            # Create folders
            (folder_path / '_retail_').mkdir(parents=True, exist_ok=True)
            # Create symbolic links
            (folder_path / '_retail_' / 'Interface').symlink_to(
                    self.interface_path, target_is_directory=True)
            (folder_path / 'Data').symlink_to(
                    self.data_path, target_is_directory=True)
            
        self.copy_executables()


        

def main():
    s = Setup()
    s.create_folders()
    print(ctypes.windll.shell32.IsUserAnAdmin() != 0)


if __name__ == '__main__':
    main()
    
    