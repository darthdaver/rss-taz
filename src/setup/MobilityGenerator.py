from src.enum.identifiers.Scenario import Scenario as ScenarioIdentifier
from src.enum.types.EventType import EventType
from src.enum.types.HumanType import HumanType
from src.model.Scenario import Scenario
from src.utils import utils
from src.enum.setup.FileSetup import FileSetup
from src.enum.identifiers.Simulation import Simulation as SimulationEnum
from src.enum.identifiers.Config import Config as ConfigEnum
from src.enum.identifiers.Human import Human as HumanEnum
from src.enum.types.NetType import NetType
from typing import Type, Dict, Union
from src.enum.identifiers.Customer import Customer as CustomerIdentifiers
from src.enum.identifiers.Driver import Driver as DriverIdentifiers
from src.enum.identifiers.Net import Net as NetIdentifiers
from src.enum.types.PersonalityType import PersonalityType
from src.enum.identifiers.Ride import Ride as RideIdentifier
from src.enum.identifiers.Scenario import Scenario as ScenarioIdentifier
from src.enum.xml.MobilityXml import MobilityXML as MobilityXMLEnum
from src.enum.setup.FileFormat import FileFormat
from src.enum.setup.FileName import FileName
from src.enum.setup.Dataset import Dataset
from src.enum.setup.City import City
from src.enum.setup.Paths import Paths
from src.types.Net import TazInfo
from src.types.Vehicle import VehicleType
from src.model.Net import Net
import xml.etree.ElementTree as ET
import random
import sumolib
from sumolib.net.edge import Edge as SumoEdge
from sumolib.net.lane import Lane as SumoLane
import numpy as np
from src.enum.identifiers.Api import Api as ApiIdentifier
from src.enum.api.Api import Api


class MobilityGenerator():
    def __init__(
            self,
            net_path: str,
            city: Type[City],
            dataset_pickups: Type[Dataset],
            dataset_travel_times: Type[Dataset],
            begin,
            end
    ):
        self.__city = city
        self.__dataset_pickups = dataset_pickups
        self.__dataset_travel_times = dataset_travel_times
        self.__customer_counter = 0
        self.__driver_counter = 0
        self.__begin = begin
        self.__end = end
        self.__sumo_net = sumolib.net.readNet(net_path, withInternal=True)
        self.__sim_net = utils.read_file_from_absolute_path_to_file(FileSetup.NET_SIMULATOR.value, FileFormat.JSON)
        self.__generation_dict = {str(i): {HumanEnum.CUSTOMERS.value: [], HumanEnum.DRIVERS.value: []} for i in range(begin, end+1)}
        self.__pickups_file = utils.read_file_from_absolute_path_to_file(FileSetup.PICKUPS.value, FileFormat.JSON)
        self.__xml_root = ET.Element(MobilityXMLEnum.ROUTES.value)
        self.__net = Net(utils.read_file_from_absolute_path_to_file(FileSetup.NET_SIMULATOR.value, FileFormat.JSON), self.__sumo_net)
        self.__vehicle_types: VehicleType = utils.read_file_from_absolute_path_to_file(FileSetup.MOBILITY_VEHICLE_TYPES.value, FileFormat.JSON)
        self.__define_vehicles_type()
        self.__scenario = Scenario(utils.read_setup(FileSetup.SCENARIO.value))
        self.__timeline = self.__generate_timeline()
        self.__generated_customers = 0
        self.__generated_drivers = 0
        self.__discarded_customers = 0
        self.__discarded_drivers = 0

    def export_mobility(self):
        output_xml_absolute_path = utils.generate_absolute_path_to_file(
            Paths.MOBILITY,
            FileName.MOBILITY,
            FileFormat.XML,
            self.__dataset_pickups,
            self.__city
        )
        utils.export_file_from_absolute_path(
            output_xml_absolute_path,
            FileFormat.XML,
            self.__xml_root
        )
        utils.check_path_exists(Paths.MOBILITY_SIMULATOR)
        output_dict_absolute_path = FileSetup.MOBILITY_SIMULATOR
        utils.export_file_from_absolute_path(output_dict_absolute_path, FileFormat.JSON, self.__generation_dict)

    def generate_mobility(self):
        for timestamp, mobility in self.__timeline.items():
            timestamp = float(timestamp)
            for c_event in mobility["customers"]:
                taz_id = c_event[NetIdentifiers.TAZ_ID.value]
                print(f"Generate customer {self.__customer_counter} - taz_id: {taz_id} - timestamp: {timestamp}")
                if self.__net.is_taz_id_in_net(taz_id, NetType.MOBILITY_NET):
                    self.__generate_customer(timestamp, c_event, NetType.MOBILITY_NET, attempts=10)
            for d_event in mobility["drivers"]:
                taz_id = d_event[NetIdentifiers.TAZ_ID.value]
                print(f"Generate driver {self.__driver_counter} - taz_id: {taz_id} - timestamp: {timestamp}")
                if self.__net.is_taz_id_in_net(taz_id, NetType.MOBILITY_NET):
                    self.__generate_driver(timestamp, d_event, NetType.MOBILITY_NET, attempts=10)
        self.export_mobility()
        print(f"Generated {self.__generated_customers} customers.")
        print(f"Generated {self.__generated_drivers} drivers.")
        print(f"Discarded {self.__discarded_customers} customers.")
        print(f"Discarded {self.__discarded_drivers} drivers.")

    def __add_customer_to_dict(self, timestamp: float, customer_id: str, src_edge_id: str, dst_edge_id: str, personality: PersonalityType, src_pos: float, dst_pos: float):
        timestamp = int(timestamp)
        customer = {
            SimulationEnum.TIMESTAMP.value: timestamp,
            CustomerIdentifiers.CUSTOMER_ID.value: customer_id,
            HumanEnum.PERSONALITY.value: personality,
            CustomerIdentifiers.SRC_EDGE_ID.value: src_edge_id,
            CustomerIdentifiers.DST_EDGE_ID.value: dst_edge_id,
            CustomerIdentifiers.SRC_POS.value: src_pos,
            CustomerIdentifiers.DST_POS.value: dst_pos
        }
        self.__generation_dict[str(timestamp)][HumanEnum.CUSTOMERS.value].append(customer)
        self.__generated_customers += 1

    def __add_driver_to_dict(self, timestamp: float, driver_id: str, personality: PersonalityType, edge_id_list: list[str], src_pos: float, dst_pos: float):
        timestamp = int(timestamp)
        driver = {
            DriverIdentifiers.DRIVER_ID.value: driver_id,
            SimulationEnum.TIMESTAMP.value: timestamp,
            HumanEnum.PERSONALITY.value: personality,
            #DriverIdentifiers.EDGE_ID_LIST.value: edge_id_list,
            DriverIdentifiers.SRC_POS.value: src_pos,
            DriverIdentifiers.DST_POS.value: dst_pos
        }
        self.__generation_dict[str(timestamp)][HumanEnum.DRIVERS.value].append(driver)
        self.__generated_drivers += 1

    def __assign_personality(self, personality_distribution: [[float,str]]) -> PersonalityType:
        value = random.random()
        min_treshold = 0
        for max_treshold, personality in personality_distribution:
            if min_treshold <= value <= max_treshold:
                return PersonalityType(personality)
            min_treshold = max_treshold
        assert False, "Human.__assign_personality - personality not found."

    def __check_edge_allows_vehicle_type(self, edge: Type[SumoEdge]):
        for v_type in self.__vehicle_types:
            if edge.allows(v_type["vClass"]):
                return True
        return False

    def __decrease_ride_length(self, ride_length: Type[RideIdentifier]):
        if ride_length == RideIdentifier.SHORT:
            return None
        elif ride_length == RideIdentifier.NORMAL:
            return RideIdentifier.SHORT
        elif ride_length == RideIdentifier.LONG:
            return RideIdentifier.NORMAL
        elif ride_length == RideIdentifier.EXTREME:
            return RideIdentifier.LONG

    def __define_vehicles_type(self):
        for v_type_attr in self.__vehicle_types:
            ET.SubElement(self.__xml_root, MobilityXMLEnum.VEHICLE_TYPE.value, attrib=v_type_attr)

    def __enrich_customer_information(
            self,
            taz_id: str,
            timestamp: float,
            customer_uniform_distribution: list[int]
    ):
        scenario_events = self.__scenario.check_events(
            timestamp,
            ScenarioIdentifier.MOBILITY_PLANNER
        )
        for type, params in scenario_events:
            self.__perform_scenario_event(
                timestamp,
                taz_id,
                customer_uniform_distribution,
                HumanType.CUSTOMER,
                type,
                params,
            )
        taz_info: TazInfo = self.__net.get_taz_info(
            taz_id,
            NetType.MOBILITY_NET
        )
        probability_generation = taz_info[ConfigEnum.CUSTOMER.value][CustomerIdentifiers.PROBABILITY_GENERATION.value]
        personality_distribution: list[[float, PersonalityType]] = taz_info[ConfigEnum.CUSTOMER.value][CustomerIdentifiers.PERSONALITY_DISTRIBUTION.value]
        personality: Type[PersonalityType] = self.__assign_personality(personality_distribution)
        ride_length: Type[RideIdentifier] = RideIdentifier(
            utils.select_from_distribution(
                taz_info[ConfigEnum.RIDE.value][RideIdentifier.ROUTE_LENGTH_DISTRIBUTION.value]
            )
        )
        return {
            CustomerIdentifiers.TIMESTAMP.value: timestamp,
            NetIdentifiers.TAZ_ID.value: taz_id,
            CustomerIdentifiers.PERSONALITY.value: personality,
            RideIdentifier.RIDE_LENGTH.value: ride_length,
            CustomerIdentifiers.PROBABILITY_GENERATION.value: probability_generation
        }

    def __enrich_driver_information(
            self,
            taz_id: str,
            timestamp: float,
            driver_uniform_distribution: list[int]
    ):
        scenario_events = self.__scenario.check_events(
            timestamp,
            ScenarioIdentifier.MOBILITY_PLANNER
        )
        for type, params in scenario_events:
            self.__perform_scenario_event(
                timestamp,
                taz_id,
                driver_uniform_distribution,
                HumanType.DRIVER,
                type,
                params
            )
        taz_info: TazInfo = self.__net.get_taz_info(
            taz_id,
            NetType.MOBILITY_NET
        )
        probability_generation = taz_info[ConfigEnum.DRIVER.value][DriverIdentifiers.PROBABILITY_GENERATION.value]
        personality_distribution: list[[float, PersonalityType]] = taz_info[ConfigEnum.DRIVER.value][DriverIdentifiers.PERSONALITY_DISTRIBUTION.value]
        personality: Type[PersonalityType] = self.__assign_personality(personality_distribution)
        return {
            DriverIdentifiers.TIMESTAMP.value: timestamp,
            NetIdentifiers.TAZ_ID.value: taz_id,
            DriverIdentifiers.PERSONALITY.value: personality,
            DriverIdentifiers.PROBABILITY_GENERATION.value: probability_generation
        }

    def __generate_customer(self, timestamp: float, customer_information, net_type: Type[NetType], src_edge_id: str = None, ride_length: Type[RideIdentifier] = None, attempts: int = 0, allow_ride_decrease: bool = True):
        taz_id = customer_information[NetIdentifiers.TAZ_ID.value]
        taz_info: TazInfo = self.__net.get_taz_info(taz_id, net_type)
        if src_edge_id is None:
            src_edge_id = self.__net.get_random_edge_id_from_taz_id(taz_id, net_type=net_type)
            if src_edge_id is None:
                self.__discarded_customers += 1
                return
        src_edge = self.__sumo_net.getEdge(src_edge_id)
        if self.__check_edge_allows_vehicle_type(src_edge):
            src_edge_lane_id = src_edge.getLanes()[0].getID()
            src_edge_length = src_edge.getLength()
            src_pos: float = round(src_edge_length/2, 2) #round(random.uniform(0.01, src_edge_length), 2)
            src_taz_id = self.__net.get_taz_id_from_edge_id(src_edge_id, NetType.ANALYTICS_NET)
            if ride_length is None:
                ride_length = customer_information[RideIdentifier.RIDE_LENGTH.value]
            dst_edge_id: str = self.__net.generate_destination_edge(taz_id, ride_length, net_type)
            if dst_edge_id is None and allow_ride_decrease:
                if attempts > 0:
                    ride_length = self.__decrease_ride_length(ride_length)
                    self.__generate_customer(timestamp, customer_information, net_type, ride_length=ride_length, attempts=(attempts - 1))
                    return
                else:
                    self.__discarded_customers += 1
                    return
            dst_edge = self.__sumo_net.getEdge(dst_edge_id)
            dst_edge_length = dst_edge.getLength()
            dst_pos = dst_edge_length # round(random.uniform(0.01, dst_edge_length), 2)
            dst_taz_id = self.__net.get_taz_id_from_edge_id(dst_edge_id, NetType.ANALYTICS_NET)
            if src_pos > 1 and dst_pos > 1:
                if self.__check_edge_allows_vehicle_type(dst_edge) and self.__net.check_connection_travel_time(src_taz_id, dst_taz_id):
                    if self.__net.check_route(src_edge, dst_edge, src_pos, dst_pos):
                        personality: Type[PersonalityType] = customer_information[CustomerIdentifiers.PERSONALITY.value]
                        customer_id = f"customer_{self.__customer_counter}"
                        self.__customer_counter += 1
                        customer_attr = {
                            MobilityXMLEnum.ID.value: customer_id,
                            MobilityXMLEnum.DEPART.value: str(timestamp),
                            MobilityXMLEnum.DEPART_POS.value: str(src_pos)
                        }
                        stop_attr = {
                            MobilityXMLEnum.LANE.value: src_edge_lane_id,
                            MobilityXMLEnum.DEPART_POS.value: str(src_pos),
                            MobilityXMLEnum.DEPART_POS.value: str(dst_pos),
                            MobilityXMLEnum.DURATION.value: str(1000)  # set to huge number by default. When the ride will start the stop will be removed
                        }
                        self.__add_customer_to_dict(timestamp, customer_id, src_edge_id, dst_edge_id, personality, src_pos, dst_pos)
                        person_xml: Type[ET.Element] = ET.SubElement(self.__xml_root, MobilityXMLEnum.PERSON, attrib=customer_attr)
                        ET.SubElement(person_xml, MobilityXMLEnum.STOP.value, attrib=stop_attr)
                        return
        if attempts > 0:
            self.__generate_customer(timestamp, customer_information, net_type, attempts=(attempts - 1))
        else:
            self.__discarded_customers += 1

    def __generate_driver(self, timestamp: float, driver_information,net_type: Type[NetType], src_edge_id: str = None, attempts=0):
        taz_id = driver_information[NetIdentifiers.TAZ_ID.value]
        taz_info: TazInfo = self.__net.get_taz_info(taz_id, net_type)
        personality = driver_information[DriverIdentifiers.PERSONALITY.value]
        if src_edge_id is None:
            src_edge_id = self.__net.get_random_edge_id_from_taz_id(taz_id, net_type=net_type)
            if src_edge_id is None:
                self.__discarded_drivers += 1
                return
        src_edge = self.__sumo_net.getEdge(src_edge_id)
        src_edge_length = src_edge.getLength()
        src_pos: float = round(src_edge_length/2, 2) # round(random.uniform(0.01, src_edge_length), 2)
        if self.__check_edge_allows_vehicle_type(src_edge):
            route_edge_list, cost = self.__net.generate_random_sumolib_route_in_taz(
                taz_id,
                src_edge_id,
                src_pos,
                net_type
            )
            if route_edge_list is not None:
                route_edge_id_list = self.__net.convert_route_to_edge_id_list(route_edge_list)
                dst_edge = route_edge_list[-1]
                dst_edge_length = dst_edge.getLength()
                route_str: str = self.__net.convert_route_to_str(route_edge_list)
                dst_pos: float = round(dst_edge_length/2, 2) # round(random.uniform(0.01, dst_edge_length), 2)
                if src_pos > 1 and dst_pos > 1:
                    driver_id = f"driver_{self.__driver_counter}"
                    self.__driver_counter += 1
                    driver_attr = {
                        MobilityXMLEnum.ID.value: driver_id,
                        MobilityXMLEnum.DEPART.value: str(timestamp),
                        MobilityXMLEnum.DEPART_POS.value: str(src_pos)
                    }
                    route_attr = {
                        MobilityXMLEnum.EDGES.value: route_str
                    }
                    vehicle_xml: Type[ET.Element] = ET.SubElement(self.__xml_root, MobilityXMLEnum.VEHICLE, attrib=driver_attr)
                    route_xml: Type[ET.Element] = ET.SubElement(vehicle_xml, MobilityXMLEnum.ROUTE, attrib=route_attr)
                    self.__add_driver_to_dict(timestamp, driver_id, personality, route_edge_id_list, src_pos, dst_pos)
                    return
        if attempts > 0:
            self.__generate_driver(timestamp, driver_information, net_type, attempts=attempts - 1)
        else:
            self.__discarded_drivers += 1

    def __generate_timeline(self):
        np.random.seed(123)
        data_generator = {}
        timeline_events = {k: {"customers": [], "drivers": []} for k in range(self.__begin, self.__end + 1)}
        for taz_id, taz_dict in self.__pickups_file.items():
            if self.__net.is_taz_id_in_net(taz_id, NetType.MOBILITY_NET):
                pickups_mean = round(taz_dict['mean'])
                pickups_std = round(taz_dict['std'])
                proportional_pickups_mean = int(self.__end - self.__begin) * pickups_mean / 3600   # pickups_mean : 1 hour = x : (end_sim - begin_sim)
                customer_uniform_dist = np.random.uniform(self.__begin, self.__end, round(proportional_pickups_mean)).astype(int).tolist()
                driver_uniform_dist = np.random.uniform(self.__begin, self.__end, round(proportional_pickups_mean/2)).astype(int).tolist()
                if random.random() <= 0.7:
                    driver_uniform_dist.insert(0, random.randint(1, 11))
                    driver_uniform_dist.pop()
                #print(len(customer_uniform_dist))
                enriched_customer_uniform_dist = []
                enriched_driver_uniform_dist = []
                for timestamp in range(int(self.__begin), int(self.__end)):
                    scenario_events = self.__scenario.check_events(
                        timestamp,
                        ScenarioIdentifier.MOBILITY_PLANNER
                    )
                    for type, params in scenario_events:
                        self.__perform_scenario_event(
                            timestamp,
                            taz_id,
                            customer_uniform_dist,
                            driver_uniform_dist,
                            type,
                            params,
                        )
                    for occurrence in range(customer_uniform_dist.count(timestamp)):
                        enriched_customer_uniform_dist.append(
                            self.__enrich_customer_information(
                                taz_id,
                                timestamp,
                                customer_uniform_dist
                            )
                        )
                    for occurrence in range(driver_uniform_dist.count(timestamp)):
                        enriched_driver_uniform_dist.append(
                            self.__enrich_driver_information(
                                taz_id,
                                timestamp,
                                driver_uniform_dist
                            )
                        )

                data_generator[taz_id] = {
                    "taz_id": taz_id,
                    "pickups_mean": pickups_mean,
                    "pickups_std": pickups_std,
                    "customer_dist": enriched_customer_uniform_dist,
                    "driver_dist": enriched_driver_uniform_dist
                }
                for c_event in enriched_customer_uniform_dist:
                    probability_generation = c_event[CustomerIdentifiers.PROBABILITY_GENERATION.value]
                    if utils.random_choice(probability_generation):
                        timeline_events[int(c_event[CustomerIdentifiers.TIMESTAMP.value])]["customers"].append(c_event)
                for d_event in enriched_driver_uniform_dist:
                    probability_generation = d_event[DriverIdentifiers.PROBABILITY_GENERATION.value]
                    if utils.random_choice(probability_generation):
                        timeline_events[int(d_event[DriverIdentifiers.TIMESTAMP.value])]["drivers"].append(d_event)
        output_path_data_generator = utils.generate_absolute_path_to_file(
            Paths.MOBILITY,
            FileName.TAZ_TIMELINE_DICT,
            FileFormat.JSON,
            self.__dataset_pickups,
            self.__city
        )
        utils.export_file_from_absolute_path(output_path_data_generator, FileFormat.JSON, data_generator)
        output_path_timeline_events = utils.generate_absolute_path_to_file(
            Paths.MOBILITY,
            FileName.TIMELINE_DICT,
            FileFormat.JSON,
            self.__dataset_pickups,
            self.__city
        )
        utils.export_file_from_absolute_path(output_path_timeline_events, FileFormat.JSON, timeline_events)
        return timeline_events

    def __perform_scenario_event(
            self,
            timestamp: float,
            taz_id: str,
            customer_uniform_dist: list[int],
            driver_uniform_dist: list[int],
            type: Type[EventType],
            params: dict         ###
    ):
        if type == EventType.DRIVER_GENERATION:
            tazs = params[ScenarioIdentifier.TAZ.value]
            if taz_id in tazs:
                taz_param = tazs[taz_id]
                begin = params[ScenarioIdentifier.BEGIN.value]
                driver_param = taz_param[ScenarioIdentifier.DRIVER.value]
                probability_generation = driver_param[DriverIdentifiers.PROBABILITY_GENERATION.value]
                personality_increment = taz_param[ScenarioIdentifier.INCREMENT.value]
                initial_personality_distribution = driver_param[DriverIdentifiers.PERSONALITY_DISTRIBUTION.value]
                new_personality_distribution = []
                for incremental_probability, personality in initial_personality_distribution:
                    increment = personality_increment[personality]
                    new_incremental_probability = incremental_probability + (increment * (timestamp - begin))
                    new_personality_distribution.append([
                        new_incremental_probability,
                        personality
                    ])

                self.__net.update_personality_distribution_in_taz(
                    taz_id,
                    new_personality_distribution,
                    HumanType.DRIVER,
                    NetType.MOBILITY_NET
                )
                self.__net.update_probability_generation_in_taz(
                    taz_id,
                    probability_generation,
                    HumanType.DRIVER,
                    NetType.MOBILITY_NET
                )
        if type == EventType.RIDE_LENGTH:
            begin = params[ScenarioIdentifier.BEGIN.value]
            tazs = params[ScenarioIdentifier.TAZ.value]
            if taz_id in tazs:
                taz_param = tazs[taz_id]
                taz_info = self.__net.get_taz_info(taz_id)
                ride_param = taz_param[ScenarioIdentifier.RIDE.value]
                initial_route_length_distribution = ride_param[RideIdentifier.ROUTE_LENGTH_DISTRIBUTION.value]
                length_increment = ride_param[ScenarioIdentifier.INCREMENT.value]
                new_route_length_distribution = []
                for incremental_probability, route_length in initial_route_length_distribution:
                    increment = length_increment[route_length]
                    new_incremental_probability = incremental_probability + (increment * (timestamp - begin))
                    new_route_length_distribution.append([
                        new_incremental_probability,
                        route_length
                    ])
                self.__net.update_route_length_distribution_in_taz(
                    taz_id,
                    new_route_length_distribution,
                    NetType.MOBILITY_NET
                )
        if type == EventType.SUDDEN_REQUESTS:
            begin = params[ScenarioIdentifier.BEGIN.value]
            tazs = params[ScenarioIdentifier.TAZ.value]
            if taz_id in tazs:
                taz_param = tazs[taz_id]
                interval = taz_param[ScenarioIdentifier.INTERVAL.value]
                requests = taz_param[ScenarioIdentifier.REQUESTS.value]
                end = begin + interval
                customer_uniform_dist.extend(
                    np.random.uniform(int(begin), int(end), requests).astype(int).tolist()
                )
