from myning.objects.player import Player
from myning.objects.research_facility import ResearchFacility


def main():
    Player.initialize()
    ResearchFacility.initialize()
    ResearchFacility().check_in()
    from new_tui.view.app import MyningApp

    MyningApp().run()


if __name__ == "__main__":
    main()
