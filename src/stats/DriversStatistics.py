from src.enum.identifiers.Driver import Driver as DriverIdentifier
from src.enum.identifiers.DriverRemotion import DriverRemotion as DriverRemotionIdentifier
from src.enum.identifiers.Statistic import Statistic as StatisticIdentifier
from src.types.Statistic import DriverStatsInfo
from src.types.Driver import DriverInfo
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

class DriversStatistics:
    def __init__(self):
        self.__drivers_stats = {}

    def added_driver(
            self,
            timestamp: float,
            driver_id
    ):
        self.__drivers_stats[driver_id] = {
            StatisticIdentifier.ID.value: driver_id,
            StatisticIdentifier.START_TIMESTAMP.value: timestamp,
            StatisticIdentifier.RIDES_IDS_LIST: [],
            StatisticIdentifier.MOVING_TO_TAZS_LIST: []
        }

    def export_drivers_stats_info(self):
        output_absolute_path = utils.generate_sim_out_absolute_path_to_file(
            Paths.SIM_OUTPUT,
            FileName.DRIVERS_STATS,
            FileFormat.JSON,
            SCENARIO,
            CITY
        )
        utils.export_file_from_absolute_path(
            output_absolute_path,
            FileFormat.JSON,
            self.get_drivers_stats()
        )

    def get_drivers_stats(self) -> Dict[str, DriverStatsInfo]:
        return {
            **self.__drivers_stats
        }
    
    def moving_to_taz(
            self,
            timestamp: float,
            driver_id: str,
            from_taz_id: str,
            to_taz_id: str
    ):
        self.__drivers_stats[driver_id][StatisticIdentifier.MOVING_TO_TAZS_LIST.value].append((
            timestamp,
            from_taz_id,
            to_taz_id
        ))

    def removed_driver(
            self,
            timestamp: float,
            reason: Type[DriverRemotionIdentifier],
            driver_info: Type[DriverInfo]
    ):
        driver_id = driver_info[DriverIdentifier.DRIVER_ID.value]
        self.__drivers_stats[driver_id] = {
            **self.__drivers_stats[driver_id],
            StatisticIdentifier.REMOTION_TIMESTAMP.value: timestamp,
            StatisticIdentifier.REMOTION_REASON.value: reason.value
        }

    def ride_completed(
            self,
            driver_id,
            ride_id
    ):
        self.__drivers_stats[driver_id][StatisticIdentifier.RIDES_IDS_LIST.value].append(ride_id)