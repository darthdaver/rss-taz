from enum import Enum

class Human(str, Enum):
    PERSONALITY = "personality"
    CUSTOMERS = "customers"
    DRIVERS = "drivers"
    HUMAN_ID = "id"
    HUMAN_STATE = "state"
    TIMESTAMP = "timestamp"
