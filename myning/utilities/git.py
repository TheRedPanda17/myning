import os
import sys

import yaml

from myning.utilities.formatter import Formatter


def check_for_updates():
    if os.popen("git rev-parse --abbrev-ref HEAD").read().rstrip() != "main":
        return

    os.system("git fetch")

    if not os.popen("git diff HEAD origin/main").read():
        return

    print("There is a new version of Myning available. Would you like to update?")
    if input("(y/n): ").lower() == "n":
        print("\nNot updating.")
        input()
        return

    old_changelog = get_changelog()
    os.system("git pull")
    os.system("pip install -r requirements.txt > /dev/null")
    changelog = get_changelog()
    changelog.reverse()

    changed = False
    for change in changelog:
        if change in old_changelog:
            continue
        changed = True
        print(f'New Update "{change["name"]}" on {change["date"]}')
        if change["description"]:
            print(change["description"])

    if not changed:
        print("Changelog empty (probably just a patch!)")

    input(f"Press {Formatter.keybind('Enter ↩️')}")
    # So we can restart the game with the updated files
    sys.exit(122)


def get_changelog() -> list:
    with open("myning/changelog.yaml", "r") as f:
        changelog = yaml.load(f, Loader=yaml.FullLoader)

    return changelog
