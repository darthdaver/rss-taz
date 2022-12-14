from src.enum.identifiers.Statistic import Statistic as StatisticIdentifier
from src.enum.setup.FileName import FileName
from src.enum.setup.FileFormat import FileFormat
from src.enum.setup.Scenario import Scenario
from src.enum.setup.Paths import Paths
from src.utils import utils
from src.settings.Settings import Settings
from src.enum.setup.City import City
from src.types.Statistic import GlobalIndicatorsInfo

env_settings = Settings()
CITY = City(env_settings.CITY)
SCENARIO = Scenario(env_settings.SCENARIO)

class GlobalIndicators:
    def __init__(
            self,
            sim_duration: int,
            taz_ids: list[str]
    ):
        sim_duration = sim_duration + 1
        self.taz_ids = taz_ids
        self.__requested = { k: { t: 0 for t in taz_ids } for k in range(0,sim_duration) }
        self.__canceled = { k: { t: 0 for t in taz_ids } for k in range(0,sim_duration) }
        self.__accepted = { k: { t: 0 for t in taz_ids } for k in range(0,sim_duration) }
        self.__not_served = { k: { t: 0 for t in taz_ids } for k in range(0,sim_duration) }
        self.__rejections = { k: { t: 0 for t in taz_ids } for k in range(0,sim_duration) }
        self.__sim_failure = { k: { t: 0 for t in taz_ids } for k in range(0,sim_duration) }
        self.__sim_failure_rejections = { k: { t: 0 for t in taz_ids } for k in range(0,sim_duration) }
        self.__idle_drivers = { k: { t: 0 for t in taz_ids } for k in range(0,sim_duration) }
        self.__responding_drivers = { k: { t: 0 for t in taz_ids } for k in range(0,sim_duration) }
        self.__pickup_drivers = { k: { t: 0 for t in taz_ids } for k in range(0,sim_duration) }
        self.__on_road_drivers = { k: { t: 0 for t in taz_ids } for k in range(0,sim_duration) }
        self.__moving_drivers = { k: { t: 0 for t in taz_ids } for k in range(0,sim_duration) }
        self.__active_customers = { k: { t: 0 for t in taz_ids } for k in range(0,sim_duration) }
        self.__pending_customers = { k: { t: 0 for t in taz_ids } for k in range(0,sim_duration) }
        self.__pickup_customers = { k: { t: 0 for t in taz_ids } for k in range(0,sim_duration) }
        self.__on_road_customers = { k: { t: 0 for t in taz_ids } for k in range(0,sim_duration) }

    def get_global_indicators_info(self) -> GlobalIndicatorsInfo:
        return {
            StatisticIdentifier.REQUESTED.value: {**self.__requested},
            StatisticIdentifier.CANCELED.value: {**self.__canceled},
            StatisticIdentifier.ACCEPTED.value: {**self.__accepted},
            StatisticIdentifier.NOT_SERVED.value: {**self.__not_served},
            StatisticIdentifier.REJECTIONS.value: {**self.__rejections},
            StatisticIdentifier.SIM_FAILURE.value: {**self.__sim_failure},
            StatisticIdentifier.SIM_FAILURE_REJECTIONS.value: {**self.__sim_failure_rejections},
            StatisticIdentifier.IDLE_DRIVERS.value: {**self.__idle_drivers},
            StatisticIdentifier.RESPONDING_DRIVERS.value: {**self.__responding_drivers},
            StatisticIdentifier.PICKUP_DRIVERS.value: {**self.__pickup_drivers},
            StatisticIdentifier.ON_ROAD_DRIVERS.value: {**self.__on_road_drivers},
            StatisticIdentifier.MOVING_DRIVERS.value: {**self.__moving_drivers},
            StatisticIdentifier.ACTIVE_CUSTOMERS.value: {**self.__active_customers},
            StatisticIdentifier.PENDING_CUSTOMERS.value: {**self.__pending_customers},
            StatisticIdentifier.PICKUP_CUSTOMERS.value: {**self.__pickup_customers},
            StatisticIdentifier.ON_ROAD_CUSTOMERS.value: {**self.__on_road_customers}
        }

    def received_request(
            self,
            timestamp: float,
            taz_id: str
    ):
        self.__requested[int(timestamp)][taz_id] += 1

    def accepted_request(
            self,
            timestamp: float,
            taz_id: str
    ):
        self.__accepted[int(timestamp)][taz_id] += 1

    def canceled_request(
            self,
            timestamp: float,
            taz_id: str
    ):
        self.__canceled[int(timestamp)][taz_id] += 1

    def request_not_served(
            self,
            timestamp: float,
            taz_id: str
    ):
        self.__not_served[int(timestamp)][taz_id] += 1

    def rejected(
            self,
            timestamp: float,
            taz_id: str
    ):
        self.__rejections[int(timestamp)][taz_id] += 1

    def sim_failure(
            self,
            timestamp: float,
            taz_id: str
    ):
        self.__sim_failure[int(timestamp)][taz_id] += 1

    def sim_failure_rejection(
            self,
            timestamp: float,
            taz_id: str
    ):
        self.__sim_failure_rejections[int(timestamp)][taz_id] += 1

    def idle_drivers(
            self,
            timestamp:float,
            taz_id:str,
            num:int
    ):
        self.__idle_drivers[int(timestamp)][taz_id] = num

    def responding_drivers(
            self,
            timestamp:float,
            taz_id:str,
            num:int
    ):
        self.__responding_drivers[int(timestamp)][taz_id] = num

    def pickup_drivers(
            self,
            timestamp:float,
            taz_id:str,
            num:int
    ):
        self.__pickup_drivers[int(timestamp)][taz_id] = num

    def on_road_drivers(
            self,
            timestamp:float,
            taz_id:str,
            num:int
    ):
        self.__on_road_drivers[int(timestamp)][taz_id] = num

    def moving_drivers(
            self,
            timestamp:float,
            taz_id:str,
            num:int
    ):
        self.__moving_drivers[int(timestamp)][taz_id] = num

    def active_customers(
            self,
            timestamp:float,
            taz_id:str,
            num:int
    ):
        self.__active_customers[int(timestamp)][taz_id] = num

    def pending_customers(
            self,
            timestamp:float,
            taz_id:str,
            num:int
    ):
        self.__pending_customers[int(timestamp)][taz_id] = num

    def pickup_customers(
            self,
            timestamp:float,
            taz_id:str,
            num:int
    ):
        self.__pickup_customers[int(timestamp)][taz_id] = num

    def on_road_customers(
            self,
            timestamp:float,
            taz_id:str,
            num:int
    ):
        self.__on_road_customers[int(timestamp)][taz_id] = num

    def export_global_indicators(
            self,
            interval: int = 1
    ):
        output_json_absolute_path = utils.generate_absolute_path_to_file(
            Paths.SIM_OUTPUT,
            FileName.GLOBAL_INDICATORS,
            FileFormat.JSON,
            SCENARIO,
            CITY
        )
        utils.export_file_from_absolute_path(
            output_json_absolute_path,
            FileFormat.JSON,
            self.get_global_indicators_info()
        )
        output_csv_absolute_path = utils.generate_absolute_path_to_file(
            Paths.SIM_OUTPUT,
            FileName.GLOBAL_INDICATORS,
            FileFormat.CSV,
            SCENARIO,
            CITY
        )
        utils.export_file_from_absolute_path(
            output_csv_absolute_path,
            FileFormat.CSV,
            self.convert_json_global_indicators_to_csv(interval)
        )


    def convert_json_global_indicators_to_csv(
            self,
            interval: int = 1
    ):
        g_i_dict = self.get_global_indicators_info()
        header = ""
        content = ""
        indicators_list_dict = {}
        csv_rows = []
        keys = g_i_dict.keys()
        for k_idx, k in enumerate(keys):
            header += f"{k}," if (k_idx < (len(keys) - 1)) else f"{k}"
            g_i_k_dict = g_i_dict[k]
            timestamps = [int(t) for t in g_i_k_dict.keys()]
            indicator_list = []
            for timestamp in range(interval, timestamps[-1]):
                indicator_sum = 0
                for taz_id in self.taz_ids:
                    for i in range(timestamp - interval, timestamp):
                        indicator_sum += g_i_k_dict[i][taz_id]
                indicator_list.append(indicator_sum)
            indicators_list_dict[k] = indicator_list
        csv_rows = list(zip(*indicators_list_dict.values()))
        content += f"{header}\n"
        for row in csv_rows:
            content += f"{','.join(str(x) for x in row)}\n"
        return content
