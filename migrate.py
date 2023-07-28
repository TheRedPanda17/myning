import sys

from myning.migrations import race_pokedex


def migrate(id: int):
    if id == "1":
        race_pokedex.run()
    else:
        sys.exit(f"{id} is not a valid migration id")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Please pass a migration id")

    migrate(sys.argv[1])
