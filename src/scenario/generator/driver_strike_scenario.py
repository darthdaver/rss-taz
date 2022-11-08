from src.enum.identifiers.Driver import Driver as DriverIdentifier
from src.enum.identifiers.Scenario import Scenario as ScenarioIdentifier
from src.enum.setup.City import City
from src.enum.setup.FileFormat import FileFormat
from src.enum.setup.FileName import FileName
from src.enum.setup.Paths import Paths
from src.enum.setup.Scenario import Scenario
from src.enum.types.EventType import EventType
from src.enum.types.PersonalityType import PersonalityType
from src.types.Scenario import ScenarioDriverStrikeParams
from src.utils import utils


def driver_strike_scenario(params: ScenarioDriverStrikeParams):
    city = params[ScenarioIdentifier.CITY.value]
    mobility_intervals = params[ScenarioIdentifier.MOBILITY_INTERVALS.value]
    mobility_tazs = params[ScenarioIdentifier.MOBILITY_TAZS.value]
    simulation_intervals = params[ScenarioIdentifier.SIMULATION_INTERVALS.value]
    simulation_tazs = params[ScenarioIdentifier.SIMULATION_TAZS.value]

    scenario_dict = {
        ScenarioIdentifier.NAME.value: Scenario.NORMAL.value,
        ScenarioIdentifier.MOBILITY_PLANNER.value: [],
        ScenarioIdentifier.SIMULATION_PLANNER.value: []
    }

    for idx, interval in enumerate(mobility_intervals):
        begin = interval[0]
        end = interval[1]
        strike_event = {
            ScenarioIdentifier.BEGIN.value: begin,
            ScenarioIdentifier.END.value: end,
            ScenarioIdentifier.EVENT_TYPE.value: EventType.DRIVER_GENERATION.value,
            ScenarioIdentifier.PARAMS.value: {
                ScenarioIdentifier.TAZ.value: {}
            }
        }
        interval_tazs = mobility_tazs[idx]
        for taz_id in interval_tazs:
            taz_param = strike_event[ScenarioIdentifier.PARAMS.value][ScenarioIdentifier.TAZ.value]
            taz_param[taz_id] = {
                ScenarioIdentifier.ID.value: taz_id,
                ScenarioIdentifier.MOBILITY_DRIVER.value: params[ScenarioIdentifier.MOBILITY_DRIVER.value]
            }

    for idx, interval in enumerate(simulation_intervals):
        begin = interval[0]
        end = interval[1]
        stop_event = {
            ScenarioIdentifier.BEGIN.value: begin,
            ScenarioIdentifier.END.value: end,
            ScenarioIdentifier.EVENT_TYPE.value: EventType.DRIVER_STOP_WORK.value,
            ScenarioIdentifier.PARAMS.value: {
                ScenarioIdentifier.TAZ.value: {}
            }
        }
        interval_tazs = simulation_tazs[idx]
        for taz_id in interval_tazs:
            taz_param = stop_event[ScenarioIdentifier.PARAMS.value][ScenarioIdentifier.TAZ.value]
            taz_param[taz_id] = {
                ScenarioIdentifier.ID.value: taz_id,
                ScenarioIdentifier.DRIVER.value: params[ScenarioIdentifier.SIMULATION_DRIVER.value]
            }
    scenario_dict[ScenarioIdentifier.MOBILITY_PLANNER.value].append(
        strike_event
    )
    scenario_dict[ScenarioIdentifier.SIMULATION_PLANNER.value].append(
        stop_event
    )
    output_absolute_path = utils.generate_absolute_path_to_file(
        Paths.SCENARIO,
        FileName.SCENARIO_PLANNER,
        FileFormat.JSON,
        Scenario.DRIVER_STRIKE,
        city
    )
    utils.export_file_from_absolute_path(
        output_absolute_path,
        FileFormat.JSON,
        scenario_dict
    )