from typing import Type

from src.enum.setup.Scenario import Scenario
from src.scenario.generator.driver_strike_scenario import driver_strike_scenario
from src.scenario.generator.flash_mob_scenario import flash_mob_scenario
from src.scenario.generator.long_rides_scenario import long_rides_scenario
from src.scenario.generator.normal_scenario import normal_scenario
from src.scenario.generator.progressive_greedy_scenario import progressive_greedy_scenario
from src.scenario.generator.underground_scenario import underground_scenario


class ScenarioGenerator():
    def __init__(self):
        self.collection = {
            Scenario.NORMAL.value: normal_scenario,
            Scenario.DRIVER_STRIKE.value: driver_strike_scenario,
            Scenario.PROGRESSIVE_GREEDY.value: progressive_greedy_scenario,
            Scenario.LONG_RIDES.value: long_rides_scenario,
            Scenario.UNDERGROUND.value: underground_scenario,
            Scenario.FLASH_MOB.value: flash_mob_scenario,
        }

    def generate_scenario(self, scenarioType: Type[Scenario], params: dict):
        self.collection[scenarioType](params)