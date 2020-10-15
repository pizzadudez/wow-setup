import questionary

from .setup import WowSetup
from .config import ADDON_NAMES

INITIAL_SETUP = "Initial Setup (directory tree, config.wtf, symlinks, copy exe)"
POST_SETUP = "Post Setup (default SV, MultiboxUtils.lua, copy AddOns, shortcuts)"
CREATE_BACKUP = "Backup (WTF folders and AddOns)"
RESTORE_FROM_BACKUP = "Restore (full setup using a backup)"
COPY_SV = "Copy SavedVariable(s) (from one account to all others)"
COPY_EXE = "After a game update, recopy the game executable"
CREATE_CONFIG_FROM_DEFAULT = "Generate Config.wtf files based on default template"
DUMP_ACCOUNT_IDS = "Print account IDs (ex: 43512345#5)"

actions = [
    INITIAL_SETUP,
    POST_SETUP,
    CREATE_BACKUP,
    RESTORE_FROM_BACKUP,
    COPY_SV,
    COPY_EXE,
    CREATE_CONFIG_FROM_DEFAULT,
    DUMP_ACCOUNT_IDS,
]


def main():
    setup = WowSetup()

    action = questionary.select(
        "Which action would you like to perform?", actions
    ).ask()

    if action == INITIAL_SETUP:
        setup.initial_setup()
    elif action == POST_SETUP:
        setup.post_setup()
    elif action == CREATE_BACKUP:
        setup.backup()
    elif action == RESTORE_FROM_BACKUP:
        setup.restore_backup()
    elif action == COPY_SV:
        # Prompt user for account index (source of saved_variable)
        acc_indices = [str(x) for x in list(range(len(setup.accounts)))]
        acc_idx_string = questionary.select(
            "Select index of source account to copy the SavedVariable from", acc_indices
        ).ask()
        acc_idx = int(acc_idx_string)
        # Prompt user for addon to copy saved_variable for
        addon_names = ADDON_NAMES
        addon_names.append("All")
        addon_name = questionary.select(
            "Which addon SavedVariable to overwrite?", addon_names
        ).ask()

        if addon_name == "All":
            for addon in ADDON_NAMES:
                setup.copy_sv(acc_idx, addon)
        else:
            setup.copy_sv(acc_idx, addon_name)
    elif action == COPY_EXE:
        setup.copy_executables()
    elif action == CREATE_CONFIG_FROM_DEFAULT:
        setup.create_config_files_from_default()
    elif action == DUMP_ACCOUNT_IDS:
        setup.dump_account_ids()


if __name__ == "__main__":
    main()
