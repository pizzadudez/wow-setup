import ctypes
import shutil

from pathlib import Path

from .config import (
    REGION,
    LOCALE,
    ACCOUNTS,
    SETUP_PATH,
    GAME_PATH,
    BACKUP_PATH,
    RESTORE_PATH,
    DEFAULT_CONFIG,
    DEFAULT_SV,
    DEFAULT_ADDONS,
)


class WowSetup:
    def __init__(self):
        self.is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

        # Account folders parent directory pathj
        self.setup_path = Path(SETUP_PATH)
        # Game installation paths
        self.game_path = Path(GAME_PATH)
        self.data_path = self.game_path / "Data"
        self.interface_path = self.game_path / "_retail_" / "Interface"
        self.exe_path = self.game_path / "_retail_" / "Wow.exe"
        # Backup/Restore paths
        self.backup_path = Path(BACKUP_PATH)
        self.restore_path = Path(RESTORE_PATH)

        # Account properties dicts
        self.accounts = self._accounts()
        # Config template used to create Config.wtf files
        self._config_template = None
        # Default saved variables lua files
        self.default_sv_files = [
            x for x in Path(DEFAULT_SV).glob("*.lua") if x.is_file()
        ]

    def _accounts(self):
        """Generate list of account dictionaries."""

        _accounts = []
        for idx, info in enumerate(ACCOUNTS):
            account_path = self.setup_path / f"wow{idx}"
            # account_id folder only gets created after first login into acc
            account_id = info.get("account_id", None) or self.find_account_id(idx)
            # Saved Variables folder path
            sv_path = (
                (
                    account_path
                    / "_retail_"
                    / "WTF"
                    / "Account"
                    / account_id
                    / "SavedVariables"
                )
                if account_id
                else None
            )

            _accounts.append(
                {
                    "idx": idx,
                    "path": account_path,
                    "email": info.get("email", ""),
                    "license_num": info.get("license_num", 1),
                    "account_id": account_id,
                    "sv_path": sv_path,
                }
            )

        return _accounts

    def _create_config_template(self):
        """Create template string from default Config.wtf file."""

        important_variables = [
            "accountName",
            "accountList",
            "portal",
            "agentUID",
        ]
        # Lines we want to modify
        format_lines = "\n".join(
            [
                'SET portal "{region}"',
                'SET agentUID "wow_{locale}"',
                'SET accountName "{email}"',
                'SET accountList "{license_num}"',
            ]
        )
        new_lines = [format_lines]
        with open(Path(DEFAULT_CONFIG)) as f:
            config_lines = f.read().splitlines()
            for line in config_lines:
                variable_name = line.split(" ")[1]
                if variable_name not in important_variables:
                    new_lines.append(line)

        self._config_template = "\n".join(new_lines)

    def get_config_string(self, email, license_num):
        """Return modified config string for specific account."""

        substitutes = {
            "region": REGION,
            "locale": LOCALE,
            "email": email,
            "license_num": f"!WoW{license_num}",
        }
        if not self._config_template:
            self._create_config_template()

        return self._config_template.format(**substitutes)

    def find_account_id(self, account_idx):
        """Find account_id folder (account SavedVariables parent directory)"""

        # TODO will break if multiple accounts present

        account_folder = (
            self.setup_path / f"wow{account_idx}" / "_retail_" / "WTF" / "Account"
        )
        if not account_folder.exists():
            return None
        account_ids = [
            f.name for f in account_folder.iterdir() if f.is_dir() and "#" in f.name
        ]

        return account_ids[0]

    def copy_executables(self):
        """Copy game.exe to all account folders. Useful after game updates."""

        for account in self.accounts:
            root_path = account["path"]
            shutil.copy2(self.exe_path, root_path / "_retail_")

    def copy_default_sv(self):
        """Copy or replace saved variables with defaults."""

        for account in self.accounts:
            sv_path = account["sv_path"] or None
            if sv_path:
                for file in self.default_sv_files:
                    shutil.copy(file, sv_path)

    def create_multibox_utils(self):
        """Create MultiboxUtils.lua files to store acc_idx for in game use."""

        lua_table = 'MultiboxUtilsDB = {{ ["accountNumber"] = {acc_idx} }}'

        for account in self.accounts:
            acc_idx = account["idx"]
            sv_path = account["sv_path"] or None
            if sv_path:
                with (sv_path / "MultiboxUtils.lua").open("w") as f:
                    f.write(lua_table.format(acc_idx=acc_idx))

    def initial_setup(self):
        """Executes first steps in a fresh install.
        - create accounts directory tree
        - create individual Config.wtf files
        - create vital symlinks (Data, Interface)
        - copy game executable
        """

        if not self.is_admin:
            print("Requires administrator privilleges")
            return

        for account in self.accounts:
            root_path = account["path"]
            # Create account folder tree
            wtf_path = root_path / "_retail_" / "WTF"
            wtf_path.mkdir(parents=True, exist_ok=True)
            # Create Config.wtf file
            with (wtf_path / "Config.wtf").open("w") as f:
                email = account["email"]
                license_num = account["license_num"]
                config_string = self.get_config_string(email, license_num)
                f.write(config_string)
            # Create symbolic links (Data + Interface)
            (root_path / "_retail_" / "Interface").symlink_to(
                self.interface_path, target_is_directory=True
            )
            (root_path / "Data").symlink_to(self.data_path, target_is_directory=True)

        # Copy wow.exe to each account folder
        self.copy_executables()

    def post_setup(self, copy_addons=True, restoring=False):
        """Standalone post_setup steps (or helper method for .restore_backup())
        - copy default SavedVariables (addon config files)
        - create MultiboxUtils.lua files containing acc_idx for in game
        - copy default AddOns
        - create QoL shortcut symlinks for SavedVariables/Addons
        """

        if not self.is_admin:
            print("Requires administrator privilleges")
            return

        if not restoring:
            # Automatically create MultiboxUtils.lua with corresponding accNumber
            self.create_multibox_utils()
            # Copy default SVs
            self.copy_default_sv()
        # Copy or replace game addons with default addons (from default folder)
        if restoring or copy_addons:
            addons_path = self.interface_path / "AddOns"
            default_addons_path = (
                Path(DEFAULT_ADDONS) if not restoring else self.backup_path / "AddOns"
            )
            shutil.rmtree(addons_path, ignore_errors=True)
            shutil.copytree(default_addons_path, addons_path)

        # SV folder shortcuts (symlinks)
        for account in self.accounts:
            sv_path = account["sv_path"]
            sv_link_path = account["path"] / "SavedVariables"
            if sv_path and not sv_link_path.is_symlink():
                sv_link_path.symlink_to(sv_path, target_is_directory=True)
        # addon folder shortcut (symlink) in setup folder
        addon_link_path = self.setup_path / "AddOns"
        if not addon_link_path.is_symlink():
            addon_path = self.interface_path / "AddOns"
            addon_link_path.symlink_to(addon_path, target_is_directory=True)

    def backup(self):
        """Backup utility for 'WTF' and 'AddOns' folders."""

        # Prompt user if he wants to overwrite old backup
        if self.backup_path.exists():
            prompt = input("Backup folder already exists, overwrite? (y/n): ")
            if prompt.lower() != "y":
                print("Aborting backup...")
                return
        # Backup WTF folders
        for account in self.accounts:
            acc_idx = account["idx"]
            wtf_path = account["path"] / "_retail_" / "WTF"
            acc_backup_path = self.backup_path / f"wow{acc_idx}" / "WTF"
            shutil.rmtree(acc_backup_path, ignore_errors=True)
            shutil.copytree(wtf_path, acc_backup_path)
        # Backup AddOns
        addons_path = self.interface_path / "AddOns"
        addons_backup_path = self.backup_path / "AddOns"
        shutil.rmtree(addons_backup_path, ignore_errors=True)
        shutil.copytree(addons_path, addons_backup_path)

    def restore_backup(self):
        """Full restoration of previously backed up 'setup'."""

        if not self.is_admin:
            print("Requires administrator privilleges")
            return

        for account in self.accounts:
            acc_idx = account["idx"]
            root_path = account["path"]
            # Create account folder tree
            wtf_path = root_path / "_retail_" / "WTF"
            wtf_path.parent.mkdir(parents=True, exist_ok=True)
            # Copy backup WTF folders
            backup_wtf_path = self.backup_path / f"wow{acc_idx}" / "WTF"
            shutil.copytree(backup_wtf_path, wtf_path)
            # Create symbolic links (Data + Interface)
            (root_path / "_retail_" / "Interface").symlink_to(
                self.interface_path, target_is_directory=True
            )
            (root_path / "Data").symlink_to(self.data_path, target_is_directory=True)

        # Copy wow.exe to each account folder
        self.copy_executables()

        # re-run account list creation to get acc_id and sv_path
        self.accounts = self._accounts()

        self.post_setup(restoring=True)

    def dump_account_ids(self):
        """Prints list of account_ids in order. Utility method for other tools."""

        ids = []
        for account in self.accounts:
            acc_id = account["account_id"]
            if acc_id:
                ids.append(acc_id)
            else:
                path = account["path"]
                print(f"account_id folder not found for account at: {path}")

        ids_string = ",".join(ids)
        print(ids_string)

    def copy_sv(self, source_acc_idx, addon_name):
        """Copy SavedVariable from one account to all others"""

        source_path = (
            self.accounts[source_acc_idx].get("sv_path", None) / f"{addon_name}.lua"
        )
        if not source_path.exists():
            print(f"File: '{addon_name}.lua' not found...")
            return

        for account in self.accounts:
            if account["idx"] == source_acc_idx:
                continue
            else:
                sv_path = account["sv_path"] or None
                if sv_path:
                    shutil.copy(source_path, sv_path)
