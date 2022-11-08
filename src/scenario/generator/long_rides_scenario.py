from src.enum.identifiers.Ride import Ride as RideIdentifier
from src.enum.identifiers.Scenario import Scenario as ScenarioIdentifier
from src.enum.setup.City import City
from src.enum.setup.FileFormat import FileFormat
from src.enum.setup.FileName import FileName
from src.enum.setup.Paths import Paths
from src.enum.setup.Scenario import Scenario
from src.enum.types.EventType import EventType
from src.types.Scenario import ScenarioLongRidesParams
from src.utils import utils


def long_rides_scenario(params: ScenarioLongRidesParams):
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
        long_rides_event = {
            ScenarioIdentifier.BEGIN.value: begin,
            ScenarioIdentifier.END.value: end,
            ScenarioIdentifier.EVENT_TYPE.value: EventType.RIDE_LENGTH.value,
            ScenarioIdentifier.PARAMS.value: {
                ScenarioIdentifier.TAZ.value: {}
            }
        }
        interval_tazs = mobility_tazs[idx]
        for taz_id in interval_tazs:
            taz_param = long_rides_event[ScenarioIdentifier.PARAMS.value][ScenarioIdentifier.TAZ.value]
            taz_param[taz_id] = {
                ScenarioIdentifier.ID.value: taz_id,
                ScenarioIdentifier.RIDE.value: params[ScenarioIdentifier.RIDE.value]
            }
        scenario_dict[ScenarioIdentifier.MOBILITY_PLANNER.value].append(
            long_rides_event
        )
        output_absolute_path = utils.generate_absolute_path_to_file(
            Paths.SCENARIO,
            FileName.SCENARIO_PLANNER,
            FileFormat.JSON,
            Scenario.LONG_RIDES,
            city
        )
        utils.export_file_from_absolute_path(
            output_absolute_path,
            FileFormat.JSON,
            scenario_dict
        )
