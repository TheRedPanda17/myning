# pylint: disable=line-too-long

from myning.chapters import (
    Option,
    PickArgs,
    PickHandler,
    StoryArgs,
    armory,
    healer,
    main_menu,
    mine,
    store,
)
from myning.objects.character import Character
from myning.objects.game import Game, GameState
from myning.objects.inventory import Inventory
from myning.objects.item import Item, ItemType
from myning.objects.player import Player
from myning.utilities.file_manager import FileManager
from myning.utilities.formatter import Formatter
from myning.utilities.pick import story_builder

game = Game()
player = Player()
inventory = Inventory()
jrod = Character("J-Rod", "a friendly minor miner")


def is_complete():
    return game._state != GameState.TUTORIAL  # pylint: disable=protected-access


def narrate(messages: list[str], handler: PickHandler):
    return story_builder(
        [
            StoryArgs(
                message=m,
                response=f"Press {Formatter.keybind('Enter ↩')} to continue...",
                border_title="Tutorial",
            )
            for m in messages
        ],
        handler,
    )


def enter():
    return narrate(
        [
            f"Welcome to Myning, {player.name}!",
            "Today is your first day as a minor miner (as opposed to a major electrician). The days are long down in the shafts, and dangers abound. The company that hired you, MMMC (Minor Miners Mining Company), has provided a guide for you.",
            f"{jrod.name}: {jrod.introduction}",
            f"{player.name}: ...",
            f"{jrod.name}: I'm not very smart, so I'm just going to ignore what you said and keep talking like a good NPC should.",
            f"{jrod.name}: The only way to make a living wage down here is by collecting minerals. Here, take this.",
        ],
        get_mineral,
    )


def get_mineral():
    nugget = Item(
        name="Miniscule Copper Nugget",
        description="a clump of coppery metal",
        value=1,
        type=ItemType.MINERAL,
    )
    inventory.add_item(nugget)
    return narrate(
        [
            nugget.tutorial_new_str,
            "You inspect the item:\n\n" + str(nugget),
            f"{jrod.name} Now you know what to look for. You can sell it to the Overlo-- I mean our bosses. You can use that to upgrade your tools and weapons.",
            f"{player.name}: Weapons?",
            f"{jrod.name}: Oh yeah. You'll figure out why you need those eventually. Here, take this.",
        ],
        get_pickaxe,
    )


def get_pickaxe():
    pickaxe = Item(
        name="Ol' Pickaxe",
        description="good for rocks. Not bad as a weapon, I guess",
        type=ItemType.WEAPON,
        value=2,
        main_affect=2,
    )
    pickaxe.add_affect("mining", 1)
    inventory.add_item(pickaxe)
    return narrate(
        [
            pickaxe.tutorial_new_str,
            "You inspect the item:\n\n" + str(pickaxe),
            f"{player.name}: Thanks.",
            f"{jrod.name}: You'll need to see as well, I suppose.",
        ],
        get_helmet,
    )


def get_helmet():
    carl = Character("Caaaarl", "your not-at-all sketchy shop owner")
    helmet = Item(
        name="Basic Mining Helmet",
        description="a nice helmet for rocks (or battle). Also, it's got a dinky light",
        type=ItemType.HELMET,
        value=2,
        main_affect=1,
    )
    helmet.add_affect("light", 1)
    inventory.add_item(helmet)
    return narrate(
        [
            helmet.tutorial_new_str,
            "You inspect the item:\n\n" + str(helmet),
            f"{jrod.name}: Okay! You're ready to go meet the shop keeper! I would suggest selling the mineral I gave you and buying some equipment.",
            f"{carl.name}: {carl.introduction}",
            f"{carl.name}: Welcome to the store. Take a look around. Special sale today on absolutely nothing.",
        ],
        store.enter,
    )


def learn_armory():
    return PickArgs(
        message=f"{jrod.name}: It's time to get your equipment ready. Here's what you're wearing down into the mines.\n",
        options=[
            Option(f"Press {Formatter.keybind('Enter ↩')} to continue...", armory.pick_member)
        ],
        subtitle=player.equipment_table,
    )


def learn_mine():
    return narrate(
        [
            f"{jrod.name}: Now we can go mining!",
            # f"{jrod.name}: There will be some minigames to help you mine or battle better, but you can ignore them without penalty if you want to be AFK. Or you can disable them entirely in the settings after you finish up this here tutorial",
        ],
        mine.pick_mine,
    )


def learn_healer():
    if player.health < player.max_health:
        messages = [f"{jrod.name}: It looks like you got injured in battle! It's time to go heal."]
    else:
        player.subtract_health(2)
        messages = [
            "As you exit the mine, a large boulder falls and hits your head. You have lost 2 health!",
            f"{jrod.name}: It looks like you took some damage from the mine! Let's go heal that up.",
        ]
    return narrate(messages, healer.enter)


def learn_bindings():
    return PickArgs(
        message=f"{jrod.name}: Alright! Before I let you go, note that there are key bindings at the bottom of the screen, depending on what you're doing. You can press {Formatter.keybind('F1')} to see more. Also, many of the elements on the screen can be interacted with using the {Formatter.keybind('mouse')}.\n\nYou should have everything you need now. Good luck!",
        options=[Option("Thanks!", exit_tutorial)],
    )


def exit_tutorial():
    game._state = GameState.READY  # pylint: disable=protected-access
    FileManager.multi_save(game, player, *inventory.items)
    return main_menu.enter()
