import sys

from .setup import WowSetup


def main(debug_arg=None):
    setup = WowSetup()
    action = debug_arg if len(sys.argv) == 1 else sys.argv[1]
    if action == "init":
        setup.initial_setup()
    elif action == "post":
        setup.post_setup()
    elif action == "accounts":
        setup.dump_account_ids()
    elif action == "backup":
        setup.backup()
    elif action == "restore":
        setup.restore_backup()
    else:
        setup.dump_account_ids()


if __name__ == "__main__":
    main("accounts")
