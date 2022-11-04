from typing import Type

from src.enum.types.EventType import EventType
from src.enum.setup.Scenario import Scenario as ScenarioType
from src.enum.identifiers.Scenario import Scenario as ScenarioIdentifier

class Scenario:
    def __init__(self, planner):
        print(planner)
        self.__name = planner[ScenarioIdentifier.NAME.value]
        self.__mobility_planner = planner[ScenarioIdentifier.MOBILITY_PLANNER.value]
        self.__simulation_planner = planner[ScenarioIdentifier.SIMULATION_PLANNER.value]

    def check_events(self, timestamp, planner_type: Type[ScenarioIdentifier]):
        timestamp = int(timestamp)
        events = []
        planner = self.__simulation_planner if planner_type == ScenarioIdentifier.SIMULATION_PLANNER else self.__mobility_planner

        for ev in planner:
            begin = ev[ScenarioIdentifier.BEGIN.value]
            end = ev[ScenarioIdentifier.END.value]
            type = EventType(ev[ScenarioIdentifier.EVENT_TYPE.value])
            params = ev[ScenarioIdentifier.PARAMS.value]
            if begin <= timestamp <= end:
                if timestamp == begin:
                    print(f"TRIGGER {type.value}: START")
                events.append((type, {
                    ScenarioIdentifier.BEGIN.value: begin,
                    **params
                }))
            if timestamp == end:
                print(f"TRIGGER {type.value}: END")
        return events

    def get_scenario_type(self):
        return self.__type