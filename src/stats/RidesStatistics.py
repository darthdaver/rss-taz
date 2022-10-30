from src.enum.identifiers.Ride import Ride as RideIdentifier
from src.types.Ride import RideInfo
from src.types.Statistic import DriverStatsInfo
from typing import Type, Dict
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


class RidesStatistics:
    def __init__(self):
        self.__rides_stats = {}

    def get_rides_stats(self) -> Dict[str, DriverStatsInfo]:
        return {
            **self.__rides_stats
        }

    def export_rides_stats_info(self):
        output_absolute_path = utils.generate_sim_out_absolute_path_to_file(
            Paths.SIM_OUTPUT,
            FileName.RIDES_STATS,
            FileFormat.JSON,
            SCENARIO,
            CITY
        )
        utils.export_file_from_absolute_path(
            output_absolute_path,
            FileFormat.JSON,
            self.get_rides_stats()
        )

    def save_rides_stats(
            self,
            rides_info: list[RideInfo]
    ):
        for ride_info in rides_info:
            ride_id = ride_info[RideIdentifier.RIDE_ID.value]
            self.__rides_stats[ride_id] = ride_info

