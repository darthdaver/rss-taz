import os
from src.enum.state.RideState import RideState
from src.enum.identifiers.Ride import Ride as RideIdentifier
from src.enum.identifiers.Route import Route as RouteIdentifier
from src.enum.identifiers.Customer import Customer as CustomerIdentifier
from src.enum.identifiers.Driver import Driver as DriverIdentifier
from src.enum.identifiers.Provider import Provider as ProviderIdentifier
from src.enum.identifiers.EnergyIndexes import EnergyIndexes as EnergyIndexesIdentifier
from src.enum.identifiers.Net import Net as NetIdentifier
from src.enum.identifiers.Config import Config as ConfigIdentifier
from functools import reduce
from src.utils import utils
from src.enum.setup.Scenario import Scenario
from src.enum.setup.FileName import FileName
from src.enum.setup.FileFormat import FileFormat
from src.enum.setup.City import City
from src.enum.setup.Paths import Paths

class Printer:

    def __init__(
            self,
            city,
            scenario
    ):
        self.__global_indicators_content = ""
        self.__global_indicators_content_v2 = ""
        self.__specific_indicators_content = ""
        self.__surge_multipliers_content = ""
        self.__rides_assignations_content = ""
        self.__tazs_info_agents_content = ""
        self.__simulator_performances_content = ""
        self.__city = city
        self.__scenario = scenario

    def export_global_indicators(self):
        path = f"{os.getcwd()}/output/global-indicators.csv"
        with open(path, 'w') as outfile:
            outfile.write(self.__global_indicators_content)

    def export_global_indicators_v2(self):
        path = f"{os.getcwd()}/output/global-indicators_v2.csv"
        with open(path, 'w') as outfile:
            outfile.write(self.__global_indicators_content_v2)

    def export_specific_indicators(self):
        path = f"{os.getcwd()}/output/specific-indicators.csv"
        with open(path, 'w') as outfile:
            outfile.write(self.__specific_indicators_content)

    def export_surge_multipliers(self):
        path = f"{os.getcwd()}/output/surge_multipliers.txt"
        with open(path, 'w') as outfile:
            outfile.write(self.__surge_multipliers_content)

    def export_rides_assignations(self):
        path = f"{os.getcwd()}/output/ride_assignations.txt"
        with open(path, 'w') as outfile:
            outfile.write(self.__rides_assignations_content)

    def export_tazs_info_agents_statistics(self):
        path = f"{os.getcwd()}/output/tazs_info_drivers.txt"
        with open(path, 'w') as outfile:
            outfile.write(self.__tazs_info_agents_content)

    @staticmethod
    def export_tazs_info(timestamp, tazs_info):
        content = "*" * 20 + "\n"
        content += f"TIMESTAMP: {timestamp}\n"
        content += "-" * 20 + "\n"
        content += "TAZS:\n"
        for id_taz, taz_info in tazs_info.items():
            content += f"ID TAZ: {id_taz}\n"
            content += f"RIDES ACCOMPLISHED: {taz_info[RideIdentifier.ENDED.value]}\n"
            content += f"RIDES NOT SERVED: {taz_info[RideIdentifier.NOT_SERVED.value]}\n"
            content += f"RIDES REJECTED: {taz_info[RideIdentifier.REJECTED.value]}\n"
            content += f"RIDES CANCELED: ${taz_info[RideIdentifier.CANCELED.value]}\n"
            content += f"SURGE MULTIPLIER: ${round(taz_info[ProviderIdentifier.SURGE_MULTIPLIERS.value][0], 2)}\n"
            content += f"BALANCE: ${round(taz_info[ProviderIdentifier.BALANCES.value][0], 2)}\n"
        content += "*" * 20 + "\n\n"
        path = f"{os.getcwd()}/output/tazs.txt"
        with open(path, 'a') as outfile:
            outfile.write(content)

    @staticmethod
    def export_customers_info(timestamp, customers_info):
        content = "*" * 20 + "\n"
        content += f"TIMESTAMP: {timestamp}\n"
        content += "-" * 20 + "\n"
        content += "INFO:\n"
        for id_customer, customer_info in customers_info.items():
            content += f"ID CUSTOMER: {id_customer}\n"
            content += f"STATE: {customer_info[CustomerIdentifier.CUSTOMER_STATE.value]}\n"
            content += f"PERSONALITY: {customer_info[CustomerIdentifier.PERSONALITY.value]}\n"
            content += "*" * 20 + "\n"
        path = f"{os.getcwd()}/output/{id_customer}.txt"
        with open(path, 'a') as outfile:
            outfile.write(content)

    @staticmethod
    def export_drivers_info(timestamp, drivers_info):
        content = "*" * 20 + "\n"
        content += f"TIMESTAMP: {timestamp}\n"
        content += "-" * 20 + "\n"
        content += "INFO:\n"
        for id_driver, driver_info in drivers_info.items():
            content += f"ID CUSTOMER: {id_driver}\n"
            content += f"STATE: {driver_info[DriverIdentifier.DRIVER_STATE.value]}\n"
            content += f"PERSONALITY: {driver_info[DriverIdentifier.PERSONALITY.value]}\n"
            content += "*" * 20 + "\n"
        path = f"{os.getcwd()}/output/{id_driver}.txt"
        with open(path, 'a') as outfile:
            outfile.write(content)

    @staticmethod
    def export_driver_movements(timestamp, driver_info, origin, destination):
        content = "*" * 20 + "\n"
        content += f"TIMESTAMP: {timestamp}\n";
        content += f"-" * 20 + "\n"
        content += f"MOVEMENT:\n"
        content += f"ID DRIVER: {driver_info[DriverIdentifier.DRIVER_ID.value]}\n"
        content += f"ORIGIN TAZ {origin}\n"
        content += f"DESTINATION TAZ {destination}\n"
        content += "*" * 20 + '\n'
        path = f"{os.getcwd()}/output/driver_movements.txt"
        with open(path, 'a') as outfile:
            outfile.write(content)


    def export_energy_indexes(self, timestamp, energy_indexes, num_timestamps):
        timestamp_start = int(timestamp) - num_timestamps + 1
        content = ""
        content_values = ""
        if timestamp == 0.0:
            content += "timestamp,unserved_request,unserved_requests_accepted,avg_overhead,avg_price_fluctuation\n"
            content_values += "timestamp,canceled,not_served,requested,ended\n"
        else:
            accepted = 0
            not_served = 0
            canceled = 0
            requested = 0
            sum_overhead = 0
            num_events_overhead = 0
            sum_price_fluctuation = 0
            num_events_price_fluctuation = 0

            for i in range(int(timestamp_start), int(timestamp) + 1):
                accepted += energy_indexes[EnergyIndexesIdentifier.ACCEPTED.value][i]
                requested += energy_indexes[EnergyIndexesIdentifier.REQUESTED.value][i]
                not_served += energy_indexes[EnergyIndexesIdentifier.NOT_SERVED.value][i]
                canceled += energy_indexes[EnergyIndexesIdentifier.CANCELED.value][i]
                sum_overhead += reduce(lambda sum, o: sum + o, energy_indexes[EnergyIndexesIdentifier.OVERHEAD.value][i], 0)
                num_events_overhead += len(energy_indexes[EnergyIndexesIdentifier.OVERHEAD.value][i])
                sum_price_fluctuation += reduce(lambda sum, o: sum + o, energy_indexes[EnergyIndexesIdentifier.PRICE_FLUCTUATION.value][i], 0)
                num_events_price_fluctuation += len(energy_indexes[EnergyIndexesIdentifier.PRICE_FLUCTUATION.value][i])
            unserved_requests = (canceled + not_served) / requested if requested else 0
            unserved_requests_accepted = (canceled + not_served) / (canceled + not_served + accepted) if (canceled + not_served + accepted) else 0
            avg_overhead = sum_overhead / num_events_overhead if num_events_overhead > 0 else 0.0
            avg_price_fluctuation = sum_price_fluctuation / num_events_price_fluctuation if num_events_price_fluctuation > 0 else 0.0

            content += f"{timestamp},"
            content += f"{round(unserved_requests, 3)},"
            content += f"{round(unserved_requests_accepted, 3)},"
            content += f"{round(avg_overhead, 3)},"
            content += f"{round(avg_price_fluctuation, 3)}\n"
            content_values += f"{timestamp},{canceled},{not_served},{requested},{num_events_overhead}\n"

        if num_timestamps == 100:
            file_name = FileName.ENERGY_INDEXES_100
            file_name_values = FileName.ENERGY_INDEXES_100_VALUES
        elif num_timestamps == 200:
            file_name = FileName.ENERGY_INDEXES_200
            file_name_values = FileName.ENERGY_INDEXES_200_VALUES
        elif num_timestamps == 500:
            file_name = FileName.ENERGY_INDEXES_500
            file_name_values = FileName.ENERGY_INDEXES_500_VALUES

        output_absolute_path_to_file = utils.generate_sim_out_absolute_path_to_file(
            Paths.SIM_OUTPUT,
            file_name,
            FileFormat.CSV,
            self.__scenario,
            self.__city
        )
        output_absolute_path_to_file_values = utils.generate_sim_out_absolute_path_to_file(
            Paths.SIM_OUTPUT,
            file_name_values,
            FileFormat.CSV,
            self.__scenario,
            self.__city
        )
        utils.export_file_from_absolute_path(
            output_absolute_path_to_file,
            FileFormat.CSV,
            content,
            mode="a"
        )
        utils.export_file_from_absolute_path(
            output_absolute_path_to_file_values,
            FileFormat.CSV,
            content,
            mode="a"
        )

    def export_energy_indexes_obj(
            self,
            energy_indexes
    ):
        output_absolute_path = utils.generate_sim_out_absolute_path_to_file(
            Paths.SIM_OUTPUT,
            FileName.ENERGY_INDEXES,
            FileFormat.JSON,
            self.__scenario,
            self.__city
        )
        utils.export_file_from_absolute_path(
            output_absolute_path,
            FileFormat.JSON,
            energy_indexes.get_energy_indexes()
        )

    def export_global_indicators_obj(
            self,
            global_indicators
    ):
        output_absolute_path = utils.generate_sim_out_absolute_path_to_file(
            Paths.SIM_OUTPUT,
            FileName.GLOBAL_INDICATORS,
            FileFormat.JSON,
            self.__scenario,
            self.__city
        )
        utils.export_file_from_absolute_path(
            output_absolute_path,
            FileFormat.JSON,
            global_indicators.get_global_indicators()
        )

    def export_specific_indicators_obj(
            self,
            specific_indicators
    ):
        output_absolute_path = utils.generate_sim_out_absolute_path_to_file(
            Paths.SIM_OUTPUT,
            FileName.SPECIFIC_INDICATORS,
            FileFormat.JSON,
            self.__scenario,
            self.__city
        )
        utils.export_file_from_absolute_path(
            output_absolute_path,
            FileFormat.JSON,
            specific_indicators.get_specific_indicators()
        )

    def export_simulator_performances(self):
        path = f"{os.getcwd()}/output/simulator_performances.csv"
        with open(path, 'w') as outfile:
            outfile.write(self.__simulator_performances_content)

    def save_tazs_info_agents(self, timestamp, statistics):
        content = "*" * 20 + "\n"
        content += f"TIMESTAMP: {timestamp}\n"
        content += "-" * 20 + "\n"
        content += f"ID TAZ: {statistics['taz_id']}\n"
        content += f"IDLE DRIVERS: {statistics['idle_drivers']}\n"
        content += f"RESPONDING DRIVERS: {statistics['responding_drivers']}\n"
        content += f"PICKUP DRIVERS: {statistics['pickup_drivers']}\n"
        content += f"ON ROAD DRIVERS: {statistics['on_road_drivers']}\n"
        content += f"MOVING DRIVERS: {statistics['moving_drivers']}\n"
        content += f"ACTIVE CUSTOMERS: {statistics['active_customers']}\n"
        content += f"PENDING CUSTOMERS: {statistics['pending_customers']}\n"
        content += f"PICKUP CUSTOMERS: {statistics['pickup_customers']}\n"
        content += f"ON ROAD CUSTOMERS: {statistics['on_road_customers']}\n"
        content += f"BALANCE: {statistics['balance']}\n"
        self.__tazs_info_agents_content += content

    def save_global_indicators(self, timestamp, rides_info):
        content = ""
        if timestamp == 1:
            content += "timestamp,"
            content += "rides_canceled,"
            content += "rides_not_served,"
            content += "rides_completed,"
            content += "rides_in_progress,"
            content += "rides_accepted,"
            content += "rides_pending,"
            content += "total_rides,"
            content += "percentage_in_progress,"
            content += "percentage_rides_completed,"
            content += "average_driver_rejections,"
            content += "average_expected_waiting_time,"
            content += "average_expected_ride_time,"
            content += "average_expected_total_time,"
            content += "average_waiting_time,"
            content += "average_ride_time,"
            content += "average_total_time,"
            content += "average_meeting_length,"
            content += "average_length,"
            content += "average_total_length,"
            content += "average_expected_meeting_length,"
            content += "average_expected_ride_length,"
            content += "average_expected_total_length,"
            content += "average_expected_price,"
            content += "average_price,"
            content += "average_error_price,"
            content += "average_error_waiting_time,"
            content += "average_error_ride_time,"
            content += "average_error_total_time,"
            content += "average_error_meeting_length,"
            content += "average_error_ride_length,"
            content += "average_error_total_length,"
            content += "average_surge_multiplier"
            content += "\n"
        rides_canceled = list(filter(lambda r: r["state"] in [RideState.CANCELED], rides_info))
        rides_not_served = list(filter(lambda r: r["state"] in [RideState.NOT_SERVED], rides_info))
        rides_accepted = list(filter(lambda r: r["state"] in [RideState.PICKUP, RideState.ON_ROAD, RideState.END], rides_info))
        rides_pending = list(filter(lambda r: r["state"] == RideState.PENDING, rides_info))
        rides_in_progress = list(filter(lambda r: r["state"] in [RideState.PICKUP, RideState.ON_ROAD], rides_info))
        rides_completed = list(filter(lambda r: r["state"] == RideState.END, rides_info))
        rides_requested = list(filter(lambda r: r["state"] == RideState.REQUESTED, rides_info))
        rides_simulation_error = list(filter(lambda r: r["state"] == RideState.SIMULATION_ERROR, rides_info))
        rides_set = list(filter(lambda r: r["state"] in [RideState.PENDING, RideState.END, RideState.ON_ROAD, RideState.PICKUP, RideState.NOT_SERVED, RideState.CANCELED], rides_info))
        rides_confirmed = list(filter(lambda r: r["state"] in [RideState.PICKUP, RideState.ON_ROAD, RideState.END], rides_info))
        rides_waiting_completed = list(filter(lambda r: r["state"] in [RideState.ON_ROAD, RideState.END], rides_info))
        percentage_not_served = len(rides_not_served) / (len(rides_not_served) + len(rides_confirmed)) if (len(rides_confirmed) + len(rides_not_served)) > 0 else 0
        percentage_canceled = len(rides_canceled) / (len(rides_canceled) + len(rides_confirmed)) if (len(rides_confirmed) + len(rides_confirmed)) > 0 else 0
        percentage_completed = len(rides_completed) / (len(rides_completed) + len(rides_not_served) + len(rides_canceled)) if (len(rides_completed) + len(rides_not_served) + len(rides_canceled)) > 0 else 0
        percentage_in_progress = len(rides_accepted) / (len(rides_accepted) + len(rides_not_served) + len(rides_canceled)) if (len(rides_accepted) + len(rides_not_served) + len(rides_canceled)) > 0 else 0
        average_driver_rejections = reduce(lambda sum, r: sum + len(r["request"]["rejections"]), rides_info, 0) / len(rides_set) if len(rides_set) > 0 else 0
        average_expected_waiting_time = reduce(lambda sum, r: sum + r["stats"]["expected_meeting_duration"], rides_confirmed, 0) / len(rides_confirmed) if len(rides_confirmed) > 0 else 0
        average_expected_ride_time = reduce(lambda sum, r: sum + r["stats"]["expected_ride_duration"], rides_confirmed, 0) / len(rides_confirmed) if len(rides_confirmed) > 0 else 0
        average_expected_total_time = reduce(lambda sum, r: sum + r["stats"]["expected_meeting_duration"] + r["stats"]["expected_ride_duration"], rides_confirmed, 0) / len(rides_confirmed) if len(rides_confirmed) > 0 else 0
        average_waiting_time = reduce(lambda sum, r: sum + r["stats"]["meeting_duration"], rides_waiting_completed, 0) / len(rides_waiting_completed) if len(rides_waiting_completed) > 0 else 0
        average_ride_time = reduce(lambda sum, r: sum + r["stats"]["ride_duration"], rides_completed, 0) / len(rides_completed) if len(rides_completed) > 0 else 0
        average_total_time = reduce(lambda sum, r: sum + r["stats"]["meeting_duration"] + r["stats"]["ride_duration"], rides_completed, 0) / len(rides_completed) if len(rides_completed) > 0 else 0
        average_meeting_length = reduce(lambda sum, r: sum + r["stats"]["meeting_length"], rides_waiting_completed, 0) / len(rides_waiting_completed) if len(rides_waiting_completed) > 0 else 0
        average_ride_length = reduce(lambda sum, r: sum + r["stats"]["ride_length"], rides_completed, 0) / len(rides_completed) if len(rides_completed) > 0 else 0
        average_total_length = reduce(lambda sum, r: sum + r["stats"]["meeting_length"] + r["stats"]["ride_length"], rides_completed, 0) / len(rides_completed) if len(rides_completed) > 0 else 0
        average_expected_meeting_length = reduce(lambda sum, r: sum + r["stats"]["expected_meeting_length"], rides_confirmed, 0) / len(rides_confirmed) if len(rides_confirmed) > 0 else 0
        average_expected_ride_length = reduce(lambda sum, r: sum + r["stats"]["expected_ride_length"], rides_confirmed, 0) / len(rides_confirmed) if len(rides_confirmed) > 0 else 0
        average_expected_total_length = reduce(lambda sum, r: sum + r["stats"]["expected_meeting_length"] + r["stats"]["expected_ride_length"], rides_confirmed, 0) / len(rides_confirmed) if len(rides_confirmed) > 0 else 0
        average_expected_price = reduce(lambda sum, r: sum + r["stats"]["expected_price"], rides_confirmed, 0) / len(rides_confirmed) if len(rides_confirmed) > 0 else 0
        average_price = reduce(lambda sum, r: sum + r["stats"]["price"], rides_completed, 0) / len(rides_completed) if len(rides_completed) > 0 else 0
        average_error_price = reduce(lambda sum, r: sum + (r["stats"]["price"] - r["stats"]["expected_price"])**2, rides_completed, 0) / len(rides_completed) if len(rides_completed) > 0 else 0
        average_error_waiting_time = reduce(lambda sum, r: sum + (r["stats"]["meeting_duration"] - r["stats"]["expected_meeting_duration"])**2, rides_completed, 0) / len(rides_completed) if len(rides_completed) > 0 else 0
        average_error_ride_time = reduce(lambda sum, r: sum + (r["stats"]["ride_duration"] - r["stats"]["expected_ride_duration"])**2, rides_completed, 0) / len(rides_completed) if len(rides_completed) > 0 else 0
        average_error_total_time = reduce(lambda sum, r: sum + ((r["stats"]["meeting_duration"] + r["stats"]["ride_duration"]) - (r["stats"]["expected_meeting_duration"] + r["stats"]["expected_ride_duration"]))**2, rides_completed, 0) / len(rides_completed) if len(rides_completed) > 0 else 0
        average_error_meeting_length = reduce(lambda sum, r: sum + (r["stats"]["meeting_length"] - r["stats"]["expected_meeting_length"]) ** 2, rides_completed, 0) / len(rides_completed) if len(rides_completed) > 0 else 0
        average_error_ride_length = reduce(lambda sum, r: sum + (r["stats"]["ride_length"] - r["stats"]["expected_ride_length"]) ** 2, rides_completed, 0) / len(rides_completed) if len(rides_completed) > 0 else 0
        average_error_total_length = reduce(lambda sum, r: sum + ((r["stats"]["meeting_length"] + r["stats"]["ride_length"]) - (r["stats"]["expected_meeting_length"] + r["stats"]["expected_ride_length"])) ** 2, rides_completed, 0) / len(rides_completed) if len(rides_completed) > 0 else 0
        average_surge_multipliers = reduce(lambda sum, r: sum + r["stats"]["surge_multiplier"], rides_confirmed, 0) / len(rides_confirmed) if len(rides_confirmed) > 0 else 0

        content += f"{timestamp},"
        content += f"{len(rides_canceled)},"
        content += f"{len(rides_not_served)},"
        content += f"{len(rides_completed)},"
        content += f"{len(rides_in_progress)},"
        content += f"{len(rides_accepted)},"
        content += f"{len(rides_pending)},"
        content += f"{len(rides_canceled) + len(rides_not_served) + len(rides_completed) + len(rides_pending)},"
        content += f"{round(percentage_in_progress, 2)},"
        content += f"{round(percentage_completed, 2)},"
        content += f"{round(average_driver_rejections, 2)},"
        content += f"{round(average_expected_waiting_time, 2)},"
        content += f"{round(average_expected_ride_time, 2)},"
        content += f"{round(average_expected_total_time, 2)},"
        content += f"{round(average_waiting_time, 2)},"
        content += f"{round(average_ride_time, 2)},"
        content += f"{round(average_total_time, 2)},"
        content += f"{round(average_meeting_length, 2)},"
        content += f"{round(average_ride_length, 2)},"
        content += f"{round(average_total_length, 2)},"
        content += f"{round(average_expected_meeting_length, 2)},"
        content += f"{round(average_expected_ride_length, 2)},"
        content += f"{round(average_expected_total_length, 2)},"
        content += f"{round(average_expected_price, 2)},"
        content += f"{round(average_price, 2)},"
        content += f"{round(average_error_price, 2)},"
        content += f"{round(average_error_waiting_time, 2)},"
        content += f"{round(average_error_ride_time, 2)},"
        content += f"{round(average_error_total_time, 2)},"
        content += f"{round(average_error_meeting_length, 2)},"
        content += f"{round(average_error_ride_length, 2)},"
        content += f"{round(average_error_total_length, 2)},"
        content += f"{round(average_surge_multipliers, 2)}"
        content += "\n"
        self.__global_indicators_content += content

    def save_global_indicators_v2(self, timestamp, rides_info):
        content = ""
        if timestamp == 1:
            content += "timestamp,"
            content += "percentage_rides_canceled,"
            content += "percentage_rides_not_served,"
            content += "percentage_accepted,"
            content += "percentage_pending,"
            content += "average_driver_rejections,"
            content += "average_expected_waiting_time,"
            content += "average_expected_waiting_time_vs_meeting_length,"
            content += "average_expected_ride_time_vs_length,"
            content += "average_expected_waiting_time_vs_average_waiting_time,"
            content += "average_waiting_time,"
            content += "average_waiting_time_vs_meeting_length,"
            content += "average_ride_time_vs_length,"
            content += "average_expected_meeting_length_vs_meeting_length,"
            content += "average_expected_ride_length_vs_ride_length,"
            content += "average_expected_price_vs_average_price,"
            content += "average_surge_multiplier"
            content += "\n"

        rides_canceled = list(filter(lambda r: r["state"] in [RideState.CANCELED], rides_info))
        rides_not_served = list(filter(lambda r: r["state"] in [RideState.NOT_SERVED], rides_info))
        rides_accepted = list(filter(lambda r: r["state"] in [RideState.PICKUP, RideState.ON_ROAD, RideState.END], rides_info))
        rides_pending = list(filter(lambda r: r["state"] == RideState.PENDING, rides_info))
        rides_completed = list(filter(lambda r: r["state"] == RideState.END, rides_info))
        rides_set = list(filter(lambda r: r["state"] in [RideState.PENDING, RideState.END, RideState.ON_ROAD, RideState.PICKUP, RideState.NOT_SERVED, RideState.CANCELED], rides_info))
        rides_waiting_completed = list(filter(lambda r: r["state"] in [RideState.ON_ROAD, RideState.END], rides_info))

        percentage_canceled = len(rides_canceled) / (len(rides_set)) if (len(rides_set)) > 0 else 0
        percentage_not_accomplished = len(rides_not_served) / (len(rides_set)) if (len(rides_set)) > 0 else 0
        percentage_accepted = len(rides_accepted) / (len(rides_set)) if (len(rides_set)) > 0 else 0
        percentage_pending = len(rides_pending) / (len(rides_set)) if (len(rides_set)) > 0 else 0
        average_driver_rejections = reduce(lambda sum, r: sum + len(r["request"]["rejections"]), rides_info, 0) / (len(rides_set)) if (len(rides_set)) > 0 else 0
        average_expected_waiting_time = reduce(lambda sum, r: sum + r["stats"]["expected_meeting_duration"], rides_accepted, 0) / len(rides_accepted) if len(rides_accepted) > 0 else 0
        average_expected_waiting_time_vs_meeting_length = reduce(lambda sum, r: sum + (r["stats"]["expected_meeting_duration"]/r["stats"]["expected_meeting_length"]), rides_accepted, 0) / len(rides_accepted) if len(rides_accepted) > 0 else 0
        average_expected_ride_time_vs_length = reduce(lambda sum, r: sum + (r["stats"]["expected_ride_duration"]/r["stats"]["expected_ride_length"]), rides_accepted, 0) / len(rides_accepted) if len(rides_accepted) > 0 else 0
        average_expected_waiting_time_vs_average_waiting_time = reduce(lambda sum, r: sum + (r["stats"]["expected_meeting_duration"]/r["stats"]["meeting_duration"]), rides_waiting_completed, 0) / len(rides_waiting_completed) if len(rides_waiting_completed) > 0 else 0
        average_waiting_time = reduce(lambda sum, r: sum + r["stats"]["meeting_duration"], rides_waiting_completed, 0) / len(rides_waiting_completed) if len(rides_waiting_completed) > 0 else 0
        average_waiting_time_vs_meeting_length = reduce(lambda sum, r: sum + (r["stats"]["meeting_duration"]/r["stats"]["meeting_length"]), rides_waiting_completed, 0) / len(rides_waiting_completed) if len(rides_waiting_completed) > 0 else 0
        average_ride_time_vs_length = reduce(lambda sum, r: sum + (r["stats"]["ride_duration"]/r["stats"]["ride_length"]), rides_completed, 0) / len(rides_completed) if len(rides_completed) > 0 else 0
        average_expected_meeting_length_vs_meeting_length = reduce(lambda sum, r: sum + (r["stats"]["expected_meeting_length"]/r["stats"]["meeting_length"]), rides_waiting_completed, 0) / len(rides_waiting_completed) if len(rides_waiting_completed) > 0 else 0
        average_expected_ride_length_vs_ride_length = reduce(lambda sum, r: sum + (r["stats"]["expected_ride_length"]/r["stats"]["ride_length"]), rides_completed, 0) / len(rides_completed) if len(rides_completed) > 0 else 0
        average_expected_price_vs_average_price = reduce(lambda sum, r: sum + (r["stats"]["expected_price"]/r["stats"]["expected_price"]), rides_completed, 0) / len(rides_completed) if len(rides_completed) > 0 else 0
        average_surge_multipliers = reduce(lambda sum, r: sum + r["stats"]["surge_multiplier"], rides_accepted, 0) / len(rides_accepted) if len(rides_accepted) > 0 else 0

        content += f"{int(timestamp)},"
        content += f"{round(percentage_canceled,4)},"
        content += f"{round(percentage_not_accomplished,4)},"
        content += f"{round(percentage_accepted,4)},"
        content += f"{round(percentage_pending,4)},"
        content += f"{round(average_driver_rejections,4)},"
        content += f"{round(average_expected_waiting_time,4)},"
        content += f"{round(average_expected_waiting_time_vs_meeting_length,4)},"
        content += f"{round(average_expected_ride_time_vs_length,4)},"
        content += f"{round(average_expected_waiting_time_vs_average_waiting_time,4)},"
        content += f"{round(average_waiting_time,4)},"
        content += f"{round(average_waiting_time_vs_meeting_length,4)},"
        content += f"{round(average_ride_time_vs_length,4)},"
        content += f"{round(average_expected_meeting_length_vs_meeting_length,4)},"
        content += f"{round(average_expected_ride_length_vs_ride_length,4)},"
        content += f"{round(average_expected_price_vs_average_price,4)},"
        content += f"{round(average_surge_multipliers,4)},"
        content += "\n"
        self.__global_indicators_content_v2 += content

    def save_global_indicators_v3(self, timestamp, rides_info):
        content = ""
        if timestamp == 1:
            content += "timestamp,"
            content += "rides_canceled,"
            content += "rides_not_served,"
            content += "accepted,"
            content += "pending,"
            content += "average_driver_rejections,"
            content += "average_expected_waiting_time,"
            content += "average_expected_waiting_time_vs_meeting_length,"
            content += "average_expected_ride_time_vs_length,"
            content += "average_expected_waiting_time_vs_average_waiting_time,"
            content += "average_waiting_time,"
            content += "average_waiting_time_vs_meeting_length,"
            content += "average_ride_time_vs_length,"
            content += "average_expected_meeting_length_vs_meeting_length,"
            content += "average_expected_ride_length_vs_ride_length,"
            content += "average_expected_price_vs_average_price,"
            content += "average_surge_multiplier"
            content += "\n"

        rides_canceled = list(filter(lambda r: r["state"] in [RideState.CANCELED], rides_info))
        rides_not_served = list(filter(lambda r: r["state"] in [RideState.NOT_SERVED], rides_info))
        rides_accepted = list(filter(lambda r: r["state"] in [RideState.PICKUP, RideState.ON_ROAD, RideState.END], rides_info))
        rides_pending = list(filter(lambda r: r["state"] == RideState.PENDING, rides_info))
        rides_completed = list(filter(lambda r: r["state"] == RideState.END, rides_info))
        rides_set = list(filter(lambda r: r["state"] in [RideState.PENDING, RideState.END, RideState.ON_ROAD, RideState.PICKUP, RideState.NOT_SERVED, RideState.CANCELED], rides_info))
        rides_waiting_completed = list(filter(lambda r: r["state"] in [RideState.ON_ROAD, RideState.END], rides_info))

        percentage_canceled = len(rides_canceled) / (len(rides_set)) if (len(rides_set)) > 0 else 0
        percentage_not_accomplished = len(rides_not_served) / (len(rides_set)) if (len(rides_set)) > 0 else 0
        percentage_accepted = len(rides_accepted) / (len(rides_set)) if (len(rides_set)) > 0 else 0
        percentage_pending = len(rides_pending) / (len(rides_set)) if (len(rides_set)) > 0 else 0
        average_driver_rejections = reduce(lambda sum, r: sum + len(r["request"]["rejections"]), rides_info, 0) / (len(rides_set)) if (len(rides_set)) > 0 else 0
        average_expected_waiting_time = reduce(lambda sum, r: sum + r["stats"]["expected_meeting_duration"], rides_accepted, 0) / len(rides_accepted) if len(rides_accepted) > 0 else 0
        average_expected_waiting_time_vs_meeting_length = reduce(lambda sum, r: sum + (r["stats"]["expected_meeting_duration"]/r["stats"]["expected_meeting_length"]), rides_accepted, 0) / len(rides_accepted) if len(rides_accepted) > 0 else 0
        average_expected_ride_time_vs_length = reduce(lambda sum, r: sum + (r["stats"]["expected_ride_duration"]/r["stats"]["expected_ride_length"]), rides_accepted, 0) / len(rides_accepted) if len(rides_accepted) > 0 else 0
        average_expected_waiting_time_vs_average_waiting_time = reduce(lambda sum, r: sum + (r["stats"]["expected_meeting_duration"]/r["stats"]["meeting_duration"]), rides_waiting_completed, 0) / len(rides_waiting_completed) if len(rides_waiting_completed) > 0 else 0
        average_waiting_time = reduce(lambda sum, r: sum + r["stats"]["meeting_duration"], rides_waiting_completed, 0) / len(rides_waiting_completed) if len(rides_waiting_completed) > 0 else 0
        average_waiting_time_vs_meeting_length = reduce(lambda sum, r: sum + (r["stats"]["meeting_duration"]/r["stats"]["meeting_length"]), rides_waiting_completed, 0) / len(rides_waiting_completed) if len(rides_waiting_completed) > 0 else 0
        average_ride_time_vs_length = reduce(lambda sum, r: sum + (r["stats"]["ride_duration"]/r["stats"]["ride_length"]), rides_completed, 0) / len(rides_completed) if len(rides_completed) > 0 else 0
        average_expected_meeting_length_vs_meeting_length = reduce(lambda sum, r: sum + (r["stats"]["expected_meeting_length"]/r["stats"]["meeting_length"]), rides_waiting_completed, 0) / len(rides_waiting_completed) if len(rides_waiting_completed) > 0 else 0
        average_expected_ride_length_vs_ride_length = reduce(lambda sum, r: sum + (r["stats"]["expected_ride_length"]/r["stats"]["ride_length"]), rides_completed, 0) / len(rides_completed) if len(rides_completed) > 0 else 0
        average_expected_price_vs_average_price = reduce(lambda sum, r: sum + (r["stats"]["expected_price"]/r["stats"]["expected_price"]), rides_completed, 0) / len(rides_completed) if len(rides_completed) > 0 else 0
        average_surge_multipliers = reduce(lambda sum, r: sum + r["stats"]["surge_multiplier"], rides_accepted, 0) / len(rides_accepted) if len(rides_accepted) > 0 else 0

        content += f"{int(timestamp)},"
        content += f"{round(percentage_canceled,4)},"
        content += f"{round(percentage_not_accomplished,4)},"
        content += f"{round(percentage_accepted,4)},"
        content += f"{round(percentage_pending,4)},"
        content += f"{round(average_driver_rejections,4)},"
        content += f"{round(average_expected_waiting_time,4)},"
        content += f"{round(average_expected_waiting_time_vs_meeting_length,4)},"
        content += f"{round(average_expected_ride_time_vs_length,4)},"
        content += f"{round(average_expected_waiting_time_vs_average_waiting_time,4)},"
        content += f"{round(average_waiting_time,4)},"
        content += f"{round(average_waiting_time_vs_meeting_length,4)},"
        content += f"{round(average_ride_time_vs_length,4)},"
        content += f"{round(average_expected_meeting_length_vs_meeting_length,4)},"
        content += f"{round(average_expected_ride_length_vs_ride_length,4)},"
        content += f"{round(average_expected_price_vs_average_price,4)},"
        content += f"{round(average_surge_multipliers,4)},"
        content += "\n"
        self.__global_indicators_content_v2 += content

    def save_ride_assignation(self, timestamp, ride_id, customer_id, driver_id):
        content = "*" * 20 + "\n"
        content += f"TIMESTAMP: {timestamp}\n";
        content += f"-" * 20 + "\n"
        content += f"RIDE ID: {ride_id}\n"
        content += f"DRIVER ID: {driver_id}\n"
        content += f"CUSTOMER ID: {customer_id}\n"
        content += "*" * 20 + '\n'
        self.__rides_assignations_content += content

    def save_simulator_performances(self, timestamp, performances_dict):
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



    def save_specific_indicators(self, timestamp, ride_info = None):
        content = ""
        if ride_info is None:
            content += f"timestamp,"
            content += f"timestamp_request,"
            content += f"timestamp_accepted,"
            content += f"timestamp_on_road,"
            content += f"source_taz_id,"
            content += f"destination_taz_id,"
            content += f"ride_length,"
            content += f"meeting_length,"
            content += f"total_length,"
            content += f"expected_waiting_time,"
            content += f"expected_ride_time,"
            content += f"expected_total_time,"
            content += f"waiting_time,"
            content += f"ride_time,"
            content += f"total_time,"
            content += f"expected_ride_price,"
            content += f"ride_price,"
            content += f"surge_multiplier,"
            content += f"rejections,"
            content += f"error_price,"
            content += f"error_meeting_duration,"
            content += f"error_ride_duration,"
            content += f"error_total_duration,"
            content += f"error_meeting_length,"
            content += f"error_meeting_length,"
            content += f"error_ride_length,"
            content += f"error_total_length"
            content += f"\n"
            content += f"\n"
        else:
            content += f"{timestamp},"
            content += f"{ride_info['stats']['timestamp_request']},"
            content += f"{ride_info['stats']['timestamp_pickup']},"
            content += f"{ride_info['stats']['timestamp_on_road']},"
            content += f"{ride_info['stats']['source_taz_id']},"
            content += f"{ride_info['stats']['destination_taz_id']},"
            content += f"{round(ride_info['stats']['ride_length'], 2)},"
            content += f"{round(ride_info['stats']['meeting_length'], 2)},"
            content += f"{round(ride_info['stats']['meeting_length'] + ride_info['stats']['ride_length'], 2)},"
            content += f"{round(ride_info['stats']['expected_meeting_duration'], 2)},"
            content += f"{round(ride_info['stats']['expected_ride_duration'], 2)},"
            content += f"{round(ride_info['stats']['expected_meeting_duration'] + ride_info['stats']['expected_ride_duration'], 2)},"
            content += f"{round(ride_info['stats']['meeting_duration'], 2)},"
            content += f"{round(ride_info['stats']['ride_duration'], 2)},"
            content += f"{round(ride_info['stats']['meeting_duration'] + ride_info['stats']['ride_duration'], 2)},"
            content += f"{round(ride_info['stats']['expected_price'], 2)},"
            content += f"{round(ride_info['stats']['price'], 2)},"
            content += f"{round(ride_info['stats']['surge_multiplier'], 2)},"
            content += f"{len(ride_info['request']['rejections'])},"
            content += f"{round(ride_info['stats']['price'] - ride_info['stats']['expected_price'], 2)},"
            content += f"{round(ride_info['stats']['meeting_duration'] - ride_info['stats']['expected_meeting_duration'], 2)},"
            content += f"{round(ride_info['stats']['ride_duration'] - ride_info['stats']['expected_ride_duration'], 2)},"
            content += f"{round((ride_info['stats']['meeting_duration'] + ride_info['stats']['ride_duration']) - (ride_info['stats']['expected_meeting_duration'] + ride_info['stats']['expected_ride_duration']), 2)},"
            content += f"{round(ride_info['stats']['meeting_length'] - ride_info['stats']['expected_meeting_length'], 2)},"
            content += f"{round(ride_info['stats']['ride_length'] - ride_info['stats']['expected_ride_length'], 2)},"
            content += f"{round((ride_info['stats']['meeting_length'] + ride_info['stats']['ride_length']) - (ride_info['stats']['expected_meeting_length'] + ride_info['stats']['expected_ride_length']), 2)}"
            content += f"\n"
        self.__specific_indicators_content += content

    def save_surge_multipliers(self, timestamp, tazs_info):
        content = "*" * 20 + "\n"
        content += f"TIMESTAMP: {timestamp}\n"
        content += "-" * 20 + "\n"
        content += "TAZS:\n"
        for id_taz, taz_info in tazs_info.items():
            content += f"ID TAZ: {id_taz}\n"
            content += f"SURGE MULTIPLIER: {round(taz_info['surge_multipliers'][0], 2)}\n"
            content += f"BALANCE: {round(taz_info['balances'][0], 2)}\n"
        content += "*" * 20 + "\n"
        self.__surge_multipliers_content += content
