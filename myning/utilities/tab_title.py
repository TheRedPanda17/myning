import os

IS_IN_TMUX = bool(os.environ.get("TMUX"))


class TabTitle:
    _root_tab_name = "⛏ Myning"
    _tab_status = ""
    _tab_subactivity = ""

    @classmethod
    def change_tab_status(cls, s: str):
        cls._tab_status = s
        cls._update_tab_title()

    @classmethod
    def change_tab_subactivity(cls, s: str):
        cls._tab_subactivity = s
        cls._update_tab_title()

    @classmethod
    def _update_tab_title(cls):
        title = f"{cls._root_tab_name} ({cls._tab_status})"
        if cls._tab_subactivity:
            title += f" - {cls._tab_subactivity}"
        if IS_IN_TMUX:
            os.system(f'printf "\033]0; {title} \007"')
        else:
            os.system(f'printf "\033]1; {title} \007"')

    @classmethod
    def beep(cls):
        os.system("printf '\a'")
