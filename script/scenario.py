from src.enum.identifiers.Driver import Driver as DriverIdentifier
from src.enum.identifiers.Scenario import Scenario as ScenarioIdentifier
from src.enum.setup.City import City
from src.enum.setup.FileFormat import FileFormat
from src.enum.setup.FileName import FileName
from src.enum.setup.Paths import Paths
from src.enum.setup.Scenario import Scenario
from src.enum.types.EventType import EventType
from src.enum.types.PersonalityType import PersonalityType
from src.utils import utils


def normal_scenario(city: City):
    scenario_dict = {
        ScenarioIdentifier.NAME.value: Scenario.NORMAL.value,
        ScenarioIdentifier.MOBILITY_PLANNER.value: [],
        ScenarioIdentifier.SIMULATION_PLANNER.value: []
    }
    output_absolute_path = utils.generate_absolute_path_to_file(
        Paths.SCENARIO,
        FileName.SCENARIO,
        FileFormat.JSON,
        Scenario.NORMAL,
        city
    )
    utils.export_file_from_absolute_path(
        output_absolute_path,
        FileFormat.JSON,
        scenario_dict
    )

def driver_strike_scenario(
        city: City,
        mobility_intervals: list[[float,float]],
        mobility_tazs: list[list[str]],
        simulation_intervals: list[[float,float]],
        simulation_tazs: list[list[str]]
):
    scenario_dict = {
        ScenarioIdentifier.NAME.value: Scenario.NORMAL.value,
        ScenarioIdentifier.MOBILITY_PLANNER.value: [],
        ScenarioIdentifier.SIMULATION_PLANNER.value: []
    }

    for idx, begin, end in enumerate(mobility_intervals):
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
                ScenarioIdentifier.DRIVER.value: {
                    DriverIdentifier.PROBABILITY_GENERATION.value: 0.2,
                    DriverIdentifier.PERSONALITY_DISTRIBUTION.value: [
                        [
                            1,
                            PersonalityType.HURRY.value
                        ],
                        [
                            1,
                            PersonalityType.GREEDY.value
                        ],
                        [
                            1,
                            PersonalityType.NORMAL.value
                        ],
                    ]
                },
                ScenarioIdentifier.INCREMENT.value: {
                    PersonalityType.HURRY.value: 0.0,
                    PersonalityType.GREEDY.value: 0.0,
                    PersonalityType.NORMAL.value: 0.0,
                }
            }

    for idx, begin, end in enumerate(simulation_intervals):
        strike_event = {
            ScenarioIdentifier.BEGIN.value: begin,
            ScenarioIdentifier.END.value: end,
            ScenarioIdentifier.EVENT_TYPE.value: EventType.DRIVER_STOP_WORK.value,
            ScenarioIdentifier.PARAMS.value: {
                ScenarioIdentifier.TAZ.value: {}
            }
        }
        interval_tazs = simulation_tazs[idx]
        for taz_id in interval_tazs:
            taz_param = strike_event[ScenarioIdentifier.PARAMS.value][ScenarioIdentifier.TAZ.value]
            taz_param[taz_id] = {
                ScenarioIdentifier.ID.value: taz_id,
                ScenarioIdentifier.DRIVER.value: {
                    DriverIdentifier.STOP_WORK_DISTRIBUTION.value: {
                        PersonalityType.HURRY.value: 0.00002,
                        PersonalityType.NORMAL.value: 0.0001,
                        PersonalityType.GREEDY.value: 0.0002
                    }
                }
            }
    output_absolute_path = utils.generate_absolute_path_to_file(
        Paths.SCENARIO,
        FileName.SCENARIO,
        FileFormat.JSON,
        Scenario.DRIVER_STRIKE,
        city
    )
    utils.export_file_from_absolute_path(
        output_absolute_path,
        FileFormat.JSON,
        scenario_dict
    )


def progressive_greedy_scenario (
        city: City,
        mobility_intervals: list[[float,float]],
        mobility_tazs: list[list[str]]
):
    scenario_dict = {
        ScenarioIdentifier.NAME.value: Scenario.NORMAL.value,
        ScenarioIdentifier.MOBILITY_PLANNER.value: [],
        ScenarioIdentifier.SIMULATION_PLANNER.value: []
    }

    for idx, begin, end in enumerate(mobility_intervals):
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
                ScenarioIdentifier.DRIVER.value: {
                    DriverIdentifier.PROBABILITY_GENERATION.value: 1,
                    DriverIdentifier.PERSONALITY_DISTRIBUTION.value: [
                        [
                            0.35,
                            PersonalityType.HURRY.value
                        ],
                        [
                            0.35,
                            PersonalityType.GREEDY.value
                        ],
                        [
                            0.35,
                            PersonalityType.NORMAL.value
                        ],
                    ]
                },
                ScenarioIdentifier.INCREMENT.value: {
                    PersonalityType.HURRY.value: -0.0002,
                    PersonalityType.GREEDY.value: 0.0003,
                    PersonalityType.NORMAL.value: -0.0002,
                }
            }
    output_absolute_path = utils.generate_absolute_path_to_file(
        Paths.SCENARIO,
        FileName.SCENARIO,
        FileFormat.JSON,
        Scenario.PROGRESSIVE_GREEDY,
        city
    )
    utils.export_file_from_absolute_path(
        output_absolute_path,
        FileFormat.JSON,
        scenario_dict
    )


def flash_mob_city(
        city: City,
        simulation_intervals: list[[float,float]],
        simulation_tazs: list[list[str,[[float,float,float],[float,float,float]]]],

):
    for idx, begin, end in enumerate(simulation_intervals):
        slow_down_event = {
            ScenarioIdentifier.BEGIN.value: begin,
            ScenarioIdentifier.END.value: end,
            ScenarioIdentifier.EVENT_TYPE.value: EventType.SLOW_DOWN_SPEED.value,
            ScenarioIdentifier.PARAMS.value: {
                ScenarioIdentifier.TAZ.value: {}
            }
        }
        speed_up_event = {
            ScenarioIdentifier.BEGIN.value: begin,
            ScenarioIdentifier.END.value: end,
            ScenarioIdentifier.EVENT_TYPE.value: EventType.SPEED_UP.value,
            ScenarioIdentifier.PARAMS.value: {
                ScenarioIdentifier.TAZ.value: {}
            }
        }
        interval_tazs = simulation_tazs[idx]
        for taz_id, slow_down_interval, speed_up_interval in interval_tazs:
            slow_down_taz_param = slow_down_event[ScenarioIdentifier.PARAMS.value][ScenarioIdentifier.TAZ.value]
            speed_up_taz_param = slow_down_event[ScenarioIdentifier.PARAMS.value][ScenarioIdentifier.TAZ.value]
            slow_down_taz_param[taz_id] = {
                ScenarioIdentifier.ID.value: taz_id,
                ScenarioIdentifier.SLOW_DOWN.value: {
                    ScenarioIdentifier.BEGIN.value: slow_down_interval[0],
                    ScenarioIdentifier.END.value: slow_down_interval[1],
                    ScenarioIdentifier.RATE.value: slow_down_interval[2]
                }
            }
            speed_up_taz_param[taz_id] = {
                ScenarioIdentifier.ID.value: taz_id,
                ScenarioIdentifier.SPEED_UP.value: {
                    ScenarioIdentifier.BEGIN.value: speed_up_interval[0],
                    ScenarioIdentifier.END.value: speed_up_interval[1],
                    ScenarioIdentifier.RATE.value: slow_down_interval[2]
                }
            }
    output_absolute_path = utils.generate_absolute_path_to_file(
        Paths.SCENARIO,
        FileName.SCENARIO,
        FileFormat.JSON,
        Scenario.DRIVER_STRIKE,
        city
    )
    utils.export_file_from_absolute_path(
        output_absolute_path,
        FileFormat.JSON,
        scenario_dict
    )