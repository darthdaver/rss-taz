from enum import Enum

class Human(str, Enum):
    PERSONALITY = "personality"
    CUSTOMERS = "customers"
    DRIVERS = "drivers"
    HUMAN_ID = "id"
    HUMAN_STATE = "state"
    TIMESTAMP = "timestamp"
    PERSONALITY_DISTRIBUTION = "personality_distribution"
    PROBABILITY_GENERATION = "probability_generation"
