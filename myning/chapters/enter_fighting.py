import random
import sys
import threading
from select import select
from time import sleep
from typing import List

from blessed import Terminal

from myning.config import CONFIG
from myning.objects.army import Army
from myning.objects.character import Character
from myning.objects.combat_game import CombatGame
from myning.objects.settings import Settings
from myning.utils.file_manager import FileManager
from myning.utils.output import bonus_string, damage_string
from myning.utils.tab_title import TabTitle
from myning.utils.ui import columnate
from myning.utils.user_input import timed_input
from myning.utils.utils import get_random_array_item, get_random_int

term = Terminal()
ROUND_TIMEOUT = 5
WAIT_TIME = int(CONFIG["tick_length"] / 5) + 3
DISABLED_INTERVAL = 1 / 2


def play(allies: Army, enemies: Army):
    round = 1
    enemies = Army(list(filter(lambda x: x.health > 0, enemies)))
    allies = Army(list(filter(lambda x: x.health > 0, allies)))

    while True:
        TabTitle.change_tab_subactivity(_get_battle_status(len(allies), len(enemies)))
        static_menu = _armies_str(allies, enemies)
        static_menu += f"\n\n{term.bold}Round {round}{term.normal}"
        print(term.clear, end="")
        print(static_menu)

        battle_order = _get_battle_order(allies, enemies)
        bonus = _mini_game_bonus(static_menu)
        battle_log = []
        damage_taken = damage_done = 0

        for combatant in battle_order:
            if not enemies or not allies:
                break

            is_friendly = combatant in allies
            if is_friendly:
                target = get_random_array_item(enemies)
                damage, dodged, crit = _do_damage(combatant, target, bonus)
            else:
                target = get_random_array_item(allies)
                damage, dodged, crit = _do_damage(combatant, target)
            if not target:
                continue

            if damage > 0:
                battle_log.append(
                    damage_string(combatant, target, damage, is_friendly, dodged, crit)
                )
            if is_friendly:
                damage_done += damage
                FileManager.save(combatant)
            else:
                damage_taken += damage
                FileManager.save(target)

            if target.health == 0:
                battle_order.remove(target)
                if is_friendly:
                    enemies.remove(target)
                else:
                    allies.remove(target)

        print(term.clear, end="")
        print(_armies_str(allies, enemies))
        print(f"\n{term.bold}Round Results{term.normal} ({bonus_string(bonus)})\n")

        print(_round_summary_str(damage_done, damage_taken))
        print("\n".join(columnate(battle_log)))

        victory = _get_victory(allies, enemies)
        if victory is not None:
            TabTitle.change_tab_subactivity("")
            return victory, (WAIT_TIME + ROUND_TIMEOUT) * round

        _, _ = timed_input(timeout=5)
        round += 1


def _do_damage(attacker: Character, defender: Character, bonus=1):
    dodge_chance = int(defender.stats["dodge_chance"])
    dodge = random.choices(
        [True, False],
        weights=[dodge_chance, 100 - dodge_chance],
    )[0]

    critical_chance = int(attacker.stats["critical_chance"])
    crit = random.choices(
        [True, False],
        weights=[critical_chance, 100 - critical_chance],
    )[0]

    damage = attacker.stats["damage"]
    damage = random.randint(0, damage)
    damage = int(bonus * damage)
    if crit:
        damage *= 2

    armor = defender.stats["armor"]
    blocked = random.randint(0, max(armor, 0))

    damage -= blocked
    if damage < 0:
        damage = 0

    if not dodge:
        defender.subtract_health(damage)
    return damage, dodge, crit


def _armies_str(army1: Army, army2: Army) -> str:
    return f"\n{term.bold('Your Army')}\n{army1}\n\n{term.bold('Enemy Army')}\n{army2}"


def _round_summary_str(damage_done: int, health_lost: int):
    return f"{term.bold}Summary: {term.green}{damage_done} damage done. {term.red}{health_lost} damage received.{term.normal}\n"


def _get_victory(army: List[Character], enemies: List[Character]):
    if army and not enemies:
        return True
    if enemies and not army:
        return False
    return None


def _get_battle_order(allies: Army, enemies: Army):
    combined = [ally for ally in list(allies) + list(enemies)]
    random.shuffle(combined)
    return combined


def _get_battle_status(allies: int, enemies: int):
    return f"⚔️ Battling (👨🏾‍🌾{allies} v 👽{enemies})"


class InputThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.done = False

    def stop(self):
        self.done = True

    def add_brother(self, brother):
        self.brother = brother

    def run(self):
        while not self.done:
            rlist, _, _ = select([sys.stdin], [], [], 1)
            if rlist:
                x = sys.stdin.read(1)[0]
                if x == "\n":
                    self.brother.attempt_stop()
                elif x:
                    self.brother.move_block(x)


def _mini_game_bonus(menu: str) -> int:
    print_thread = PrintThread(menu)
    input_thread = InputThread()
    print_thread.brother = input_thread
    input_thread.brother = print_thread
    print_thread.daemon = True
    input_thread.daemon = True
    input_thread.start()
    print_thread.start()
    input_thread.join()
    print_thread.join()

    return print_thread.combat_game.bonus


class PrintThread(threading.Thread):
    def __init__(self, menu: str):
        threading.Thread.__init__(self)

        self.menu = menu
        self.wait = WAIT_TIME
        self.fought = False
        self.settings = Settings()
        spear_count = random.randint(3, 4)
        self.combat_game = CombatGame(spear_count=spear_count)
        self.spf = get_random_int(spear_count * 13, spear_count * 18)
        self.spf /= 680

    def add_brother(self, brother):
        self.brother = brother

    def stop(self):
        self.fought = True

    def move_block(self, block: str):
        self.combat_game.change_block(block)

    def attempt_stop(self):
        # You can't exit mid-game
        if not self.combat_game.started:
            self.stop()
            self.brother.stop()

    def run(self):
        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            last_count = int(self.wait) + 1
            while self.wait > 0 and not self.fought:
                if self.settings.mini_games_disabled:
                    print(term.clear, end="")
                    print(self.menu)
                    print(f'Fighting ("↵" to exit)... ({int(self.wait)} seconds left)\n')
                    print("⚔️   " * (4 - int(self.wait) % 5))

                    sleep(DISABLED_INTERVAL)
                    self.wait -= DISABLED_INTERVAL
                else:
                    if last_count - int(self.wait) >= 1:
                        print(term.clear, end="")
                        print(self.menu)
                        print()
                    print(self.combat_game)
                    print(term.move_up(2))

                    self.combat_game.tick()
                    sleep(self.spf)
                    self.wait -= self.spf

        self.stop()
        self.brother.stop()
