import os

import yaml
from blessed import Terminal

term = Terminal()


def check_for_updates():
    if os.popen("git rev-parse --abbrev-ref HEAD").read().rstrip() != "main":
        return

    os.system("git fetch")

    if not os.popen("git diff HEAD origin/main").read():
        return

    print(term.clear)
    print("There is a new version of Myning available. Would you like to update?")
    if input("(y/n): ").lower() == "n":
        print("\nNot updating.")
        input()
        return

    old_changelog = get_changelog()
    os.system("git pull")
    print(term.clear)
    changelog = get_changelog()
    changelog.reverse()

    changed = False
    for change in changelog:
        if change in old_changelog:
            continue
        changed = True
        print(f'{term.bold}New Update "{change["name"]}"{term.normal} on {change["date"]}')
        if change["description"]:
            print(change["description"])

    if not changed:
        print("Changelog empty (probably just a patch!)")

    input("Press ↵")
    # So we can restart the game with the updated files
    exit(122)


def get_changelog() -> list:
    with open("myning/changelog.yaml", "r") as f:
        changelog = yaml.load(f, Loader=yaml.FullLoader)

    return changelog
