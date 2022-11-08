from src.enum.identifiers.Scenario import Scenario as ScenarioIdentifier
from src.enum.setup.City import City
from src.enum.setup.FileFormat import FileFormat
from src.enum.setup.FileName import FileName
from src.enum.setup.Paths import Paths
from src.enum.setup.Scenario import Scenario
from src.enum.types.EventType import EventType
from src.types.Scenario import ScenarioUndergroundParams
from src.utils import utils


def underground_scenario(params: ScenarioUndergroundParams):
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
        sudden_requests_event = {
            ScenarioIdentifier.BEGIN.value: begin,
            ScenarioIdentifier.END.value: end,
            ScenarioIdentifier.EVENT_TYPE.value: EventType.SUDDEN_REQUESTS.value,
            ScenarioIdentifier.PARAMS.value: {
                ScenarioIdentifier.TAZ.value: {}
            }
        }
        interval_tazs = mobility_tazs[idx]
        for requests_param in interval_tazs:
            taz_id = requests_param[0]
            sudden_requests = requests_param[1]
            taz_param = sudden_requests_event[ScenarioIdentifier.PARAMS.value][ScenarioIdentifier.TAZ.value]
            taz_param[taz_id] = {
                ScenarioIdentifier.ID.value: taz_id,
                ScenarioIdentifier.REQUESTS.value: sudden_requests[0],
                ScenarioIdentifier.INTERVAL.value: sudden_requests[1]
            }
    scenario_dict[ScenarioIdentifier.MOBILITY_PLANNER.value].append(
        sudden_requests_event
    )
    output_absolute_path = utils.generate_absolute_path_to_file(
        Paths.SCENARIO,
        FileName.SCENARIO_PLANNER,
        FileFormat.JSON,
        Scenario.UNDERGROUND,
        city
    )
    utils.export_file_from_absolute_path(
        output_absolute_path,
        FileFormat.JSON,
        scenario_dict
    )