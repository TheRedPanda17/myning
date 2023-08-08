import math
import random
from typing import Callable

from rich.table import Table
from textual import events
from textual.containers import Container, ScrollableContainer
from textual.screen import Screen
from textual.widgets import ProgressBar, Static
from myning.config import CONFIG
from myning.objects.army import Army
from myning.objects.item import Item

from myning.objects.player import Player
from myning.objects.trip import Trip
from myning.utils.file_manager import FileManager
from myning.utils.generators import (
    generate_character,
    generate_enemy_army,
    generate_equipment,
    generate_mineral,
)
from myning.utils.race_rarity import get_recruit_species
from myning.utils.utils import get_random_array_item
from new_tui.actions import (
    Action,
    CombatAction,
    ItemAction,
    LoseAllyAction,
    MineAction,
    RecruitAction,
)
from new_tui.utilities import throttle
from new_tui.view.header import Header

player = Player()
trip = Trip()


def time_str(seconds: int):  # sourcery skip: assign-if-exp, reintroduce-else
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    if minutes > 0:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


class Content(Static):
    def print(self, content):
        table = Table.grid()
        table.add_column(overflow="fold")
        table.add_row(content)
        self.update(table)


class TimeRemaining(Static):
    def on_mount(self):
        self.set_interval(0.1, self.update_time)

    def update_time(self):
        self.update(f"{time_str(trip.seconds_left)} remaining")


class MineScreen(Screen):
    def __init__(self) -> None:
        self.content = Content()
        self.progress = ProgressBar(total=trip.total_seconds, show_eta=False)
        self.actions: dict[str, Callable[..., Action]] = {
            "combat": self.combat,
            "mineral": self.mine,
            "equipment": self.equipment,
            "recruit": self.recruit,
            "lose_ally": self.lose_ally,
        }
        self.action: Action = self.mine()
        super().__init__()

    def compose(self):
        yield Header()
        with ScrollableContainer() as c:
            c.border_title = f"{trip.mine.icon} {trip.mine.name}"
            yield self.content
        with Container() as c:
            c.border_title = "Trip Summary"
            yield Static(trip.tui_summary)
        with Container() as c:
            c.border_title = "Trip Progress"
            yield TimeRemaining()
            yield self.progress

    def on_mount(self):
        self.tick()
        self.set_interval(1, self.tick)

    def on_key(self, key: events.Key):
        if key.name == "q":
            self.exit()
        else:
            self.skip()

    def exit(self):
        self.dismiss()

    def update_progress(self):
        self.progress.progress = trip.total_seconds - trip.seconds_left

    @throttle(1)
    def skip(self):
        print(f"Skipped {self.action.duration} seconds")
        trip.seconds_left -= self.action.duration
        self.action = self.next_action

    def tick(self):
        self.update_progress()
        self.content.print(self.action.content)

        self.action.tick()
        if self.action.duration <= 0:
            self.action = self.next_action

        trip.tick_passed(1)
        if trip.seconds_left < 0:
            self.exit()

    @property
    def next_action(self):
        if isinstance(self.action, MineAction):
            return self.mineral()
        if isinstance(self.action, CombatAction) and self.action.enemy_army:
            return CombatAction(5, self.action.enemy_army)

        odds = trip.mine.odds.copy()
        if not player.allies:
            odds = [o for o in odds if o["action"] != "lose_ally"]
        actions = [o["action"] for o in odds]
        chances = [o["chance"] for o in odds]
        selected_action = random.choices(actions, weights=chances)[0]
        return self.actions[selected_action]()

    def combat(self):
        mine = trip.mine
        army = player.army
        if mine.enemies[1] < 0:
            mine.enemies[1] = len(army) + mine.enemies[1]
        enemy_army = generate_enemy_army(
            mine.character_levels,
            mine.enemies,
            mine.max_enemy_items,
            mine.max_enemy_item_level,
            mine.enemy_item_scale,
        )
        # enemy_count = len(enemy_army)

        # victory, ticks_passed = enter_fighting.play(army, enemy_army)

        # print_battle_results(victory)

        # if victory:
        #     rewards = generate_reward(mine.max_item_level, enemy_count)
        #     FileManager.multi_save(*rewards)
        #     [trip.add_item(reward) for reward in rewards]
        #     [slow_print(reward.get_new_text()) for reward in rewards]

        # enemy_survivors = Army(list(filter(lambda x: x.health > 0, enemy_army)))
        # trip.add_battle(enemy_count - len(enemy_survivors), victory)
        FileManager.save(trip)
        return CombatAction(5, enemy_army)

    def mine(self):
        duration = random.randint(0, int(CONFIG["tick_length"] + trip.seconds_left / 60)) + 5
        return MineAction(duration)

    def mineral(self):
        mineral = generate_mineral(trip.mine.max_item_level, trip.mine.resource)
        return self.item(mineral)

    def equipment(self):
        equipment = generate_equipment(trip.mine.max_item_level)
        return self.item(equipment)

    def item(self, item: Item):
        trip.add_item(item)
        FileManager.multi_save(item, trip)
        return ItemAction(item)

    def recruit(self):
        levels = trip.mine.character_levels
        levels = [max(1, math.ceil(level * 0.75)) for level in levels]
        species = get_recruit_species(trip.mine.companion_rarity)
        ally = generate_character(levels, race=species)
        trip.add_ally(ally)
        FileManager.multi_save(ally, trip)
        return RecruitAction(ally)

    def lose_ally(self):
        ally = get_random_array_item(player.allies)
        player.kill_ally(ally)
        trip.remove_ally(ally)
        FileManager.multi_save(trip, player)
        return LoseAllyAction(ally)

    def unimplemented(self):
        class UnimplementedAction(Action):
            @property
            def content(self):
                return "unimplemented action"

        return UnimplementedAction(1)
