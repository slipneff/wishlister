from enum import Enum, auto

class State(Enum):
    CHOOSING = auto()
    ADDING_TITLE = auto()
    ADDING_PRICE = auto()
    ADDING_LINK = auto()
    ADDING_PHOTO = auto()
