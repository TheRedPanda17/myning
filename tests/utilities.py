from rich.text import Text

from myning.tui.app import MyningApp
from myning.tui.chapter.option_table import OptionTable


def get_option(app: MyningApp, index: int):
    option_table = app.query_one("OptionTable", OptionTable)
    arr = []
    for x in option_table.get_row_at(index):
        if not x:
            continue
        if isinstance(x, Text):
            arr.append(x.plain)
        elif isinstance(x, str):
            arr.append(x)
        else:
            arr.append(str(x))
    return " ".join(arr)
