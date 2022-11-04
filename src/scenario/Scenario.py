from src.enum.identifiers.Scenario import Scenario as ScenarioIdentifier

class Scenario:
    def __init__(self, scenario_setup):
        self.__name = scenario_setup[ScenarioIdentifier.NAME.value]
        self.__mobility_planner = scenario_setup[ScenarioIdentifier.MOBILITY_PLANNER.value]
        self.__simulation_planner = scenario_setup[ScenarioIdentifier.SIMULATION_PLANNER.value]

    def exec_mobility_planner(self):
        pass

    def exec_simulation_planner(self):
        pass