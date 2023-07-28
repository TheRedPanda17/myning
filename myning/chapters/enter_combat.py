from blessed.terminal import Terminal

from myning.chapters import enter_fighting
from myning.objects.army import Army
from myning.objects.player import Player
from myning.objects.trip import Trip
from myning.utils.file_manager import FileManager
from myning.utils.generators import generate_enemy_army, generate_reward
from myning.utils.output import print_battle_results
from myning.utils.user_input import slow_print

term = Terminal()


def play():
    player = Player()
    trip = Trip()
    mine = trip.mine
    army = player.army
    print(term.orange("\nOh no! You're under attack"))
    if mine.enemies[1] < 0:
        mine.enemies[1] = len(army) + mine.enemies[1]
    enemy_army = generate_enemy_army(
        mine.character_levels,
        mine.enemies,
        mine.max_enemy_items,
        mine.max_enemy_item_level,
        mine.enemy_item_scale,
    )
    enemy_count = len(enemy_army)

    victory, ticks_passed = enter_fighting.play(army, enemy_army)

    print_battle_results(victory)

    if victory:
        rewards = generate_reward(mine.max_item_level, enemy_count)
        FileManager.multi_save(*rewards)
        [trip.add_item(reward) for reward in rewards]
        [slow_print(reward.get_new_text()) for reward in rewards]

    enemy_survivors = Army(list(filter(lambda x: x.health > 0, enemy_army)))
    trip.add_battle(enemy_count - len(enemy_survivors), victory)
    trip.tick_passed(ticks_passed)
    FileManager.save(trip)
    return False
