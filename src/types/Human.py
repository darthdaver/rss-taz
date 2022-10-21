from typing import TypedDict, Union
from src.enum.types.PersonalityType import PersonalityType as PersonalityType
from src.enum.state.DriverState import DriverState
from src.enum.state.CustomerState import CustomerState


class HumanInfo(TypedDict):
    id = str
    personality = PersonalityType
    state: Union[CustomerState, DriverState]
    timestamp: float

class PersonalityDistribution(TypedDict):
    customers: list[[float, PersonalityType]]
    drivers: list[[float, PersonalityType]]
