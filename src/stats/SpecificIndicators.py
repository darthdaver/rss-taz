from src.enum.setup.FileName import FileName
from src.enum.setup.FileFormat import FileFormat
from src.enum.setup.Scenario import Scenario
from src.enum.setup.Paths import Paths
from src.utils import utils
from src.settings.Settings import Settings
from src.enum.setup.City import City
from src.types.Statistic import SpecificIndicatorsInfo

env_settings = Settings()
CITY = City(env_settings.CITY)
SCENARIO = Scenario(env_settings.SCENARIO)

class SpecificIndicators:
    def __init__(
            self,
            sim_duration: int
    ):
        self.__rides_stats = { k: [] for k in range(0, sim_duration + 1) }

    def get_specific_indicators(self) -> SpecificIndicatorsInfo:
        return {
            **self.__rides_stats
        }

    def add_ride_stats(
            self,
            timestamp: float,
            stats
    ):
        self.__rides_stats[int(timestamp)].append(stats)

    def export_specific_indicators(self):
        output_absolute_path = utils.generate_absolute_path_to_file(
            Paths.SIM_OUTPUT,
            FileName.SPECIFIC_INDICATORS,
            FileFormat.JSON,
            SCENARIO,
            CITY
        )
        utils.export_file_from_absolute_path(
            output_absolute_path,
            FileFormat.JSON,
            self.get_specific_indicators()
        )