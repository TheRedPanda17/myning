from blessed.terminal import Terminal

from myning.chapters import enter_armory, enter_healer, enter_mine, enter_store
from myning.objects.character import Character
from myning.objects.item import Item, ItemType
from myning.objects.player import Player
from myning.utils.file_manager import FileManager
from myning.utils.output import get_character_speech, narrate, print_entity_speech

term = Terminal()


def play():
    player = Player()

    # This ensures new players have the new migrations. Preferably, we'd loop
    # through the MIGRATIONS, but we have a circular dependency if we do,
    # so this is the hack right now.
    player.completed_migrations = [1, 2, 3, 4, 5, 6]
    FileManager.save(player)

    print(term.bold(f"\nWelcome to Myning, {player.name}!\n"))
    narrate(
        "Today is your first day as a minor miner (as opposed to a major electrician). The days are long down in the shafts, and dangers abound. The company that hired you, MMMC (Minor Miners Mining Company), has provided a guide for you.",
    )

    j_rod = Character("J-Rod", "a friendly minor miner")
    FileManager.save(j_rod)

    print_entity_speech(j_rod, j_rod.get_introduction())

    get_character_speech(player)

    print_entity_speech(
        j_rod,
        "I'm not very smart, so I'm just going to ignore what you said and keep talking like a good NPC should.",
    )
    print_entity_speech(
        j_rod,
        "The only way to make a living wage down here is by collecting minerals. Here, take this.",
    )

    copper_nugget = Item(
        "Miniscule Copper Nugget",
        "a clump of coppery metal",
        value=1,
        type=ItemType.MINERAL,
    )
    player.inventory.add_item(copper_nugget)
    print(copper_nugget.get_new_text())
    FileManager.save(copper_nugget)
    print("\n" + str(copper_nugget), end="")
    input()

    print_entity_speech(
        j_rod,
        "Now you know what to look for. You can sell it to the Overlo-- I mean our bosses. You can use that to upgrade your tools and weapons",
    )

    print_entity_speech(player, "Weapons?")

    print_entity_speech(
        j_rod,
        "Oh yeah. You'll figure out why you need those eventually. Here, take this.",
    )
    pickaxe = Item(
        name="Ol' Pickaxe",
        description="good for rocks. Not bad as a weapon, I guess",
        type=ItemType.WEAPON,
        value=2,
        main_affect=2,
    )
    pickaxe.add_affect("mining", 1)
    player.inventory.add_item(pickaxe)
    print(pickaxe.get_new_text())
    FileManager.save(pickaxe)
    print("\n" + str(pickaxe), end="")
    input()

    print_entity_speech(player, "Thanks.")

    print_entity_speech(j_rod, "You'll need to see as well, I suppose.")

    helmet = Item(
        name="Basic Mining Helmet",
        description="a nice helmet for rocks (or battle). Also, it's got a dinky light",
        type=ItemType.HELMET,
        value=2,
        main_affect=1,
    )
    helmet.add_affect("light", 1)
    player.inventory.add_item(helmet)
    print(helmet.get_new_text())
    FileManager.save(helmet)
    print("\n" + str(helmet), end="")
    input()
    print_entity_speech(
        j_rod,
        "Okay! You're ready to go meet the shop keeper! I would suggest selling the mineral I gave you and buying some equipment.",
    )

    carl = Character("Caaaarl", "your not-at-all sketchy shop owner")
    FileManager.save(carl)
    print_entity_speech(carl, carl.get_introduction(), wait=False)
    print()
    print_entity_speech(
        carl,
        "Welcome to the store. Take a look around. Special sale today on absolutely nothing.",
    )
    enter_store.play()

    print_entity_speech(
        j_rod,
        "It's time to get your equipment ready. Here's what you're wearing down into the mines.",
    )
    print(term.bold("\nEquipment"))
    print(player.equipment)
    print(term.bold("\nStats"))
    print(player.stats_str)
    input()
    enter_armory.play()

    print_entity_speech(j_rod, "Now we can go mining!")
    print_entity_speech(
        j_rod,
        "There will be some minigames to help you mine or battle better, "
        "but you can ignore them without penalty if you want to be AFK. "
        "Or you can disable them entirely in the settings after you finish "
        "up this here tutorial",
    )
    enter_mine.play()

    if player.health < player.max_health:
        print_entity_speech(
            j_rod,
            "It looks like you got injured in battle! It's time to go heal.",
        )
    else:
        narrate(
            "As you exit the mine, a large boulder falls and hits your head. You have lost 2 health!"
        )
        player.subtract_health(2)
        FileManager.save(player)
        print_entity_speech(
            j_rod,
            "It looks like you took some damage from the mine! Let's go heal that up.",
        )

    enter_healer.play()
