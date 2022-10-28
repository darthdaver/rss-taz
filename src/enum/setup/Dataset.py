from enum import Enum

class Dataset(str, Enum):
    SFCTA = "sfcta"
    STANFORD = "stanford"
    UBER = "uber"
    TEST = "test"
