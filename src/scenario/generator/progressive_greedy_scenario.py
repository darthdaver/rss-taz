from src.enum.identifiers.Driver import Driver as DriverIdentifier
from src.enum.identifiers.Scenario import Scenario as ScenarioIdentifier
from src.enum.setup.City import City
from src.enum.setup.FileFormat import FileFormat
from src.enum.setup.FileName import FileName
from src.enum.setup.Paths import Paths
from src.enum.setup.Scenario import Scenario
from src.enum.types.EventType import EventType
from src.enum.types.PersonalityType import PersonalityType
from src.types.Scenario import ScenarioProgressiveGreedyParams
from src.utils import utils

def progressive_greedy_scenario(params: ScenarioProgressiveGreedyParams):
    city = params[ScenarioIdentifier.CITY.value]
    mobility_intervals = params[ScenarioIdentifier.MOBILITY_INTERVALS.value]
    mobility_tazs = params[ScenarioIdentifier.MOBILITY_TAZS.value]
    scenario_dict = {
        ScenarioIdentifier.NAME.value: Scenario.NORMAL.value,
        ScenarioIdentifier.MOBILITY_PLANNER.value: [],
        ScenarioIdentifier.SIMULATION_PLANNER.value: []
    }
    for idx, interval in enumerate(mobility_intervals):
        begin = interval[0]
        end = interval[1]
        progressive_greedy_event = {
            ScenarioIdentifier.BEGIN.value: begin,
            ScenarioIdentifier.END.value: end,
            ScenarioIdentifier.EVENT_TYPE.value: EventType.DRIVER_GENERATION.value,
            ScenarioIdentifier.PARAMS.value: {
                ScenarioIdentifier.TAZ.value: {}
            }
        }
        interval_tazs = mobility_tazs[idx]
        for taz_id in interval_tazs:
            taz_param = progressive_greedy_event[ScenarioIdentifier.PARAMS.value][ScenarioIdentifier.TAZ.value]
            taz_param[taz_id] = {
                ScenarioIdentifier.ID.value: taz_id,
                ScenarioIdentifier.MOBILITY_DRIVER.value: params[ScenarioIdentifier.DRIVER.value]
            }
    scenario_dict[ScenarioIdentifier.MOBILITY_PLANNER.value].append(
        progressive_greedy_event
    )
    output_absolute_path = utils.generate_absolute_path_to_file(
        Paths.SCENARIO,
        FileName.SCENARIO_PLANNER,
        FileFormat.JSON,
        Scenario.PROGRESSIVE_GREEDY,
        city
    )
    utils.export_file_from_absolute_path(
        output_absolute_path,
        FileFormat.JSON,
        scenario_dict
    )