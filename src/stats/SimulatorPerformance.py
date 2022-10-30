from src.types.Statistic import SimulatorPerformanceRow
from typing import Type
from src.enum.setup.FileName import FileName
from src.enum.setup.FileFormat import FileFormat
from src.enum.setup.Scenario import Scenario
from src.enum.setup.Paths import Paths
from src.utils import utils
from src.settings.Settings import Settings
from src.enum.setup.City import City

env_settings = Settings()
CITY = City(env_settings.CITY)
SCENARIO = Scenario(env_settings.SCENARIO)


class SimulatorPerformance:
    def __init__(self):
        self.__simulator_performances_content = ""

    def save_simulator_performances(
            self,
            timestamp: str,
            performances_dict: Type[SimulatorPerformanceRow]
    ):
        content = ""
        if timestamp == 0.0:
            content += "timestamp,"
            for idx, k in enumerate(performances_dict.keys()):
                content += f"{k}"
                if idx != (len(performances_dict) - 1):
                    content += ","
            content += "\n"
        content += f"{timestamp},"
        for idx, performance_value in enumerate(performances_dict.values()):
            content += f"{performance_value}"
            if idx != (len(performances_dict) - 1):
                content += ","
        content += "\n"
        self.__simulator_performances_content += content

    def export_simulator_performances(self):
        output_absolute_path = utils.generate_sim_out_absolute_path_to_file(
            Paths.SIM_OUTPUT,
            FileName.SIMULATOR_PERFORMANCES,
            FileFormat.CSV,
            SCENARIO,
            CITY
        )
        utils.export_file_from_absolute_path(
            output_absolute_path,
            FileFormat.CSV,
            self.__simulator_performances_content
        )