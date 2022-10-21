from src.utils import utils
from src.enum.state.CustomerState import CustomerState
from src.enum.state.DriverState import DriverState
from src.enum.types.PersonalityType import PersonalityType
from src.enum.identifiers.Human import Human as HumanIdentifier     ###
import random
from typing import Type, Union, Dict


class Human:
    def __init__(
            self,
            timestamp: float,
            id: str,
            state: Union[CustomerState, DriverState],
            personality: Type[PersonalityType]
    ):
        self._id = id
        self._state = state
        self._timestamp = timestamp
        self._personality = personality

    @property
    def id(self) -> str:
        return self._id

    @property
    def state(self) -> Type[PersonalityType]:
        return self._state

    @state.setter
    def state(self, state: Type[PersonalityType]):
        self._state = state

    def get_info(self):
        return {
            HumanIdentifier.HUMAN_ID.value: self._id,
            HumanIdentifier.PERSONALITY.value: self._personality,
            HumanIdentifier.HUMAN_STATE.value: self._state,
            HumanIdentifier.TIMESTAMP.value: self._timestamp
        }

    def accept_ride_conditions(self, surge_multiplier: float, policy: Dict[str,list[[float, float, float]]], bias=0):
        for min_surge, max_surge, probability in policy:
            if min_surge <= surge_multiplier < max_surge:
                return utils.random_choice(probability + bias)
        return utils.random_choice(0.5 + bias)

    def change_personality(self, new_personality: Type[PersonalityType]):
        self._personality = new_personality

