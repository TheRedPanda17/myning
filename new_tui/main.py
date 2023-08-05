from textual.app import App
from textual.widgets import OptionList
from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility


def main():
    Player.initialize()
    ResearchFacility.initialize()
    ResearchFacility().check_in()
    from new_tui.view.app import MyningApp

    MyningApp().run()
    print("Game saved. Thank you for playing Myning!")


# class TestApp(App):
#     CSS = """
#     OptionList {
#         height: 1fr
#     }
#     """
#
#     def __init__(self):
#         self.option_list = OptionList(*[str(x) for x in range(100)])
#         super().__init__()
#
#     def compose(self):
#         yield self.option_list


if __name__ == "__main__":
    main()
    # TestApp().run()
