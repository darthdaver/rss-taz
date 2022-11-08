from enum import Enum

class PersonalityType(str, Enum):
    HURRY = "hurry"
    GREEDY = "greedy"
    NORMAL = "normal"