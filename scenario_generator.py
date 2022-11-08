import random

from src.enum.identifiers.Ride import Ride as RideIdentifier
from src.setup.ScenarioGenerator import ScenarioGenerator
from src.enum.setup.FileSetup import FileSetup
from src.enum.setup.Scenario import Scenario
from src.enum.identifiers.Scenario import Scenario as ScenarioIdentifier
from src.model.Net import Net
from src.enum.types.NetType import NetType
from src.enum.setup.City import City
from src.utils import utils
from src.settings.Settings import Settings
import sumolib

env_settings = Settings()
CITY = City(env_settings.CITY)
SCENARIO = Scenario(env_settings.SCENARIO)


if __name__ == "__main__":
    sumo_net = sumolib.net.readNet(FileSetup.NET_SUMO.value)
    net = Net(utils.read_setup(FileSetup.NET_SIMULATOR.value), sumo_net)
    scenario_setup = utils.read_setup(FileSetup.SCENARIO_CONFIG.value)
    scenario_generator = ScenarioGenerator()

    if SCENARIO == Scenario.NORMAL:
        params = {
            ScenarioIdentifier.CITY.value: CITY
        }
        scenario_generator.generate_scenario(
            Scenario.NORMAL.value,
            params
        )
    elif SCENARIO == Scenario.DRIVER_STRIKE:
        if scenario_setup[ScenarioIdentifier.MOBILITY_TAZS.value] == []:
            mobility_taz_ids_net_boundary = net.get_all_taz_ids(
                NetType.BOUNDARY_NET
            )
        else:
            mobility_taz_ids_net_boundary = scenario_setup[ScenarioIdentifier.MOBILITY_TAZS.value]
        if scenario_setup[ScenarioIdentifier.SIMULATION_TAZS.value] == []:
            simulation_taz_ids_net_boundary = net.get_all_taz_ids(
                NetType.BOUNDARY_NET
            )
        else:
            simulation_taz_ids_net_boundary = scenario_setup[ScenarioIdentifier.SIMULATION_TAZS.value]
        params = {
            ScenarioIdentifier.CITY.value: CITY,
            ScenarioIdentifier.MOBILITY_INTERVALS.value: scenario_setup[ScenarioIdentifier.MOBILITY_INTERVALS.value],
            ScenarioIdentifier.MOBILITY_TAZS.value: [mobility_taz_ids_net_boundary],
            ScenarioIdentifier.SIMULATION_INTERVALS.value: scenario_setup[ScenarioIdentifier.SIMULATION_INTERVALS.value],
            ScenarioIdentifier.SIMULATION_TAZS.value: [simulation_taz_ids_net_boundary],
            ScenarioIdentifier.MOBILITY_DRIVER.value: scenario_setup[ScenarioIdentifier.MOBILITY_DRIVER.value],
            ScenarioIdentifier.SIMULATION_DRIVER.value: scenario_setup[ScenarioIdentifier.SIMULATION_DRIVER.value]
        }
        scenario_generator.generate_scenario(
            Scenario.DRIVER_STRIKE,
            params
        )
    elif SCENARIO == Scenario.PROGRESSIVE_GREEDY:
        if scenario_setup[ScenarioIdentifier.MOBILITY_TAZS.value] == []:
            mobility_taz_ids_net_boundary = net.get_all_taz_ids(
                NetType.BOUNDARY_NET
            )
        else:
            mobility_taz_ids_net_boundary = scenario_setup[ScenarioIdentifier.MOBILITY_TAZS.value]
        params = {
            ScenarioIdentifier.CITY.value: CITY,
            ScenarioIdentifier.MOBILITY_INTERVALS.value: scenario_setup[ScenarioIdentifier.MOBILITY_INTERVALS.value],
            ScenarioIdentifier.MOBILITY_TAZS.value: [mobility_taz_ids_net_boundary],
            ScenarioIdentifier.DRIVER.value: scenario_setup[ScenarioIdentifier.DRIVER.value]
        }
        scenario_generator.generate_scenario(
            Scenario.PROGRESSIVE_GREEDY,
            params
        )
    elif SCENARIO == Scenario.FLASH_MOB:
        params = {
            ScenarioIdentifier.CITY.value: CITY,
            ScenarioIdentifier.SIMULATION_INTERVALS.value: scenario_setup[ScenarioIdentifier.SIMULATION_INTERVALS.value],
            ScenarioIdentifier.SIMULATION_TAZS.value: scenario_setup[ScenarioIdentifier.SIMULATION_TAZS.value]
        }
        scenario_generator.generate_scenario(
            Scenario.FLASH_MOB,
            params
        )
    elif SCENARIO == Scenario.LONG_RIDES:
        if scenario_setup[ScenarioIdentifier.MOBILITY_TAZS.value] == []:
            mobility_taz_ids_net_boundary = []
            for interval in scenario_setup[ScenarioIdentifier.MOBILITY_INTERVALS.value]:
                mobility_taz_ids_net_boundary.append(net.get_all_taz_ids(
                    NetType.BOUNDARY_NET
                ))
        else:
            mobility_taz_ids_net_boundary = scenario_setup[ScenarioIdentifier.MOBILITY_TAZS.value]
        params = {
            ScenarioIdentifier.CITY.value: CITY,
            ScenarioIdentifier.MOBILITY_INTERVALS.value: scenario_setup[ScenarioIdentifier.MOBILITY_INTERVALS.value],
            ScenarioIdentifier.MOBILITY_TAZS.value: mobility_taz_ids_net_boundary,
            ScenarioIdentifier.RIDE.value: {
                RideIdentifier.ROUTE_LENGTH_DISTRIBUTION.value: scenario_setup[RideIdentifier.ROUTE_LENGTH_DISTRIBUTION.value],
                RideIdentifier.INCREMENT.value: scenario_setup[RideIdentifier.INCREMENT.value]
            }
        }
        scenario_generator.generate_scenario(
            Scenario.LONG_RIDES,
            params
        )
    elif SCENARIO == Scenario.UNDERGROUND:
        params = {
            ScenarioIdentifier.CITY.value: CITY,
            ScenarioIdentifier.MOBILITY_INTERVALS.value: scenario_setup[ScenarioIdentifier.MOBILITY_INTERVALS.value],
            ScenarioIdentifier.MOBILITY_TAZS.value: scenario_setup[ScenarioIdentifier.MOBILITY_TAZS.value]
        }
        scenario_generator.generate_scenario(
            Scenario.UNDERGROUND,
            params
        )