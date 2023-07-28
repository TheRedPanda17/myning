from dataclasses import dataclass
from enum import Enum


class StoreType(Enum):
    """
    The current specialty types of stores in the game
    """

    GARDEN = "garden"
    BLACKSMITH = "blacksmith"


@dataclass
class BuyingOption:
    """
    A buying option is a way to buy something unlocked by an upgrade. This Class is used to pass around the
    players buying options from the garden or blacksmith to the store.
    Example:
    buying_options = BuyingOption(
                    name="all Blademaster items",
                    store_type=StoreType.BLACKSMITH,
                    options_string="Buy Full Set",
                    filter="Blademaster's",
                )
    params:
    name: The string to display in the store
    store_type: The type of store chosen (garden or blacksmith)
    options_string: The string to use when displaying the items
    filter: Optional, the filter to use when displaying the items, e.g. A list of all Bladesmith class items
    """

    name: str
    store_type: StoreType
    options_string: str
    filter: str = None
