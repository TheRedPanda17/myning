from dataclasses import dataclass
from typing import Callable

from myning.objects.item import Item


@dataclass
class BuyingOption:
    """
    A buying option is a convenience option unlocked by an upgrade which can be used to buy a set of
    items.

    Parameters:
    name: The string to display in the store
    filter: The function to use to filter the items

    Example:
    ```python
    buying_option = BuyingOption(
        name="all Blademaster items",
        filter=lambda item: "Blademaster" in item.name,
    )
    ```
    """

    name: str
    filter: Callable[[Item], bool]
