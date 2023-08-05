from rich.table import Table
from textual.app import App
from textual.containers import ScrollableContainer
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import OptionList, Static
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility


def main():
    Player.initialize()
    ResearchFacility.initialize()
    ResearchFacility().check_in()
    from new_tui.view.app import MyningApp

    MyningApp().run()
    # print("Game saved. Thank you for playing Myning!")
    print("Game was not saved because we are still in dev. Thank you for playing Myning!")


# items = ["a"]


# class Content(Widget):
#     def render(self):
#         table = Table.grid()
#         for i in items:
#             table.add_row(i)
#         # self.update(table)
#         return table
#
#
# class TestApp(App):
#     def compose(self):
#         yield Content()
#
#     def on_key(self):
#         items.append("a")
#         table = self.query_one("Content")
#         table.refresh()


if __name__ == "__main__":
    main()
    # TestApp().run()
