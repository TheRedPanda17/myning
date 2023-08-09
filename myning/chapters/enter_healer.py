import random

from blessed import Terminal

from myning.config import CONFIG, UPGRADES
from myning.objects.army import Army
from myning.objects.player import Player
from myning.utils.file_manager import FileManager
from myning.utils.io import pick
from myning.utils.output import narrate
from myning.utils.user_input import timed_input
from myning.utils.utils import get_random_array_item, get_random_int

term = Terminal()


def play():
    player = Player()
    army = player.army

    while True:
        if not _members_to_heal(army):
            print(term.clear, end="")
            narrate("\nEveryone is healthy.")
            return

        # show menu
        if player.has_upgrade("insta_heal"):
            cost = UPGRADES["insta_heal"].player_value * len(army)
            options = [f"Instant ({str(cost) + 'g' if cost else 'free'})"]

            # hide slow option, if instant is free
            if cost:
                options.append("Slowly (free)")

            options.append("No")
        else:
            options = ["Yes (free)", "No"]
        option, _ = pick(options, "Start Recovery?")

        # perform action
        if "Instant" in option:
            if player.pay(cost, failure_msg="You can't afford it.", failure_option="Darn!"):
                for member in army:
                    member.health = member.max_health
                    FileManager.save(member)
            print(term.clear, end="")
            print(army)
        elif "No" in option:
            return
        else:
            fully_recovered = False
            while not fully_recovered:
                with term.fullscreen(), term.hidden_cursor():
                    print("\nRecovering... (press ↵ to speed up)\n")
                    print(army)
                    wait = random.randint(0, int(CONFIG["tick_length"] / 3))
                    _, _ = timed_input(timeout=wait)
                    fully_recovered = recover(army)


def recover(army: Army):
    heal_amount = get_random_int(1, len(army))
    members_need_healing = _members_to_heal(army)
    if not members_need_healing:
        return True

    member = get_random_array_item(members_need_healing)
    member.health += heal_amount
    if member.health > member.max_health:
        member.health = member.max_health
    FileManager.save(member)

    members_need_healing = _members_to_heal(army)
    if not members_need_healing:
        return True


def _members_to_heal(members: Army):
    return [member for member in members if member.health < member.max_health]
