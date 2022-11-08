from src.enum.identifiers.Scenario import Scenario as ScenarioIdentifier
from src.enum.setup.FileFormat import FileFormat
from src.enum.setup.FileName import FileName
from src.enum.setup.Paths import Paths
from src.enum.setup.Scenario import Scenario
from src.enum.types.EventType import EventType
from src.types.Scenario import ScenarioFlashMobParams
from src.utils import utils


def flash_mob_scenario(params: ScenarioFlashMobParams):
    city = params[ScenarioIdentifier.CITY.value]
    simulation_intervals = params[ScenarioIdentifier.SIMULATION_INTERVALS.value]
    simulation_tazs = params[ScenarioIdentifier.SIMULATION_TAZS]
    scenario_dict = {
        ScenarioIdentifier.NAME.value: Scenario.NORMAL.value,
        ScenarioIdentifier.MOBILITY_PLANNER.value: [],
        ScenarioIdentifier.SIMULATION_PLANNER.value: []
    }
    for idx, interval in enumerate(simulation_intervals):
        begin = interval[0]
        end = interval[1]
        tazs_speed_event = simulation_tazs[idx]
        speed_type = tazs_speed_event[0]
        speed_tazs = tazs_speed_event[1]
        speed_event = {
            ScenarioIdentifier.BEGIN.value: begin,
            ScenarioIdentifier.END.value: end,
            ScenarioIdentifier.EVENT_TYPE.value: EventType.SLOW_DOWN_SPEED.value if speed_type == ScenarioIdentifier.SLOW_DOWN.value else EventType.SPEED_UP.value,
            ScenarioIdentifier.PARAMS.value: {
                ScenarioIdentifier.TAZ.value: {}
            }
        }
        for taz_speed_interval in speed_tazs:
            taz_id = taz_speed_interval[0]
            speed_interval = taz_speed_interval[1]
            speed_taz_param = speed_event[ScenarioIdentifier.PARAMS.value][ScenarioIdentifier.TAZ.value]
            speed_taz_param[taz_id] = {
                ScenarioIdentifier.ID.value: taz_id,
                speed_type: {
                    ScenarioIdentifier.BEGIN.value: speed_interval[0],
                    ScenarioIdentifier.END.value: speed_interval[1],
                    ScenarioIdentifier.RATE.value: speed_interval[2]
                }
            }
        scenario_dict[ScenarioIdentifier.SIMULATION_PLANNER].append(
            speed_event
        )
    output_absolute_path = utils.generate_absolute_path_to_file(
        Paths.SCENARIO,
        FileName.SCENARIO_PLANNER,
        FileFormat.JSON,
        Scenario.FLASH_MOB,
        city
    )
    utils.export_file_from_absolute_path(
        output_absolute_path,
        FileFormat.JSON,
        scenario_dict
    )