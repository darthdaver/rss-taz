import time
import multiprocessing

from src.enum.identifiers.Statistic import Statistic as StatisticIdentifier
from src.enum.setup.FileSetup import FileSetup
from src.enum.state.CustomerState import CustomerState
from src.enum.state.DriverState import DriverState
from src.enum.state.RideState import RideState
from src.enum.state.RideRequestState import RideRequestState
from src.enum.types.PersonalityType import PersonalityType
from src.enum.types.EventType import EventType
from src.enum.types.HumanType import HumanType
from src.enum.types.RouteType import RouteType
from src.enum.types.NetType import NetType
from src.enum.identifiers.Net import Net as NetIdentifier
from src.enum.identifiers.Provider import Provider as ProviderIdentifier        ###
from src.enum.identifiers.Route import Route as RouteIdentifier
from src.enum.identifiers.EnergyIndexes import EnergyIndexes as EnergyIndexesIdentifier     ###
from src.enum.identifiers.Config import Config as ConfigEnum        ###
from src.enum.identifiers.Human import Human as HumanEnum       ###
from src.enum.identifiers.Customer import Customer as CustomerIdentifier        ###
from src.enum.identifiers.Ride import Ride as RideIdentifier        ###
from src.enum.identifiers.Request import Request as RequestIdentifier        ###
from src.enum.identifiers.Driver import Driver as DriverIdentifiers     ###
from src.enum.identifiers.DriverRemotion import DriverRemotion as DriverRemotionIdentifier     ###
from src.stats.Statistics import Statistics
from src.types.Ride import RideInfo
from src.types.Driver import DriverInfo
from src.types.Customer import CustomerInfo
from src.types.Route import RouteInfo
from src.utils import utils
from src.model.Scenario import Scenario
from src.model.Provider import Provider
from src.model.Net import Net
from src.model.Ride import Ride
from src.model.Route import Route
from src.model.Customer import Customer
from src.model.Driver import Driver
from src.enum.setup.City import City
from typing import Type, Dict, Union
import traci
import sumolib
import sys


class Simulator:
    def __init__(
            self,
            city: Type[City]
    ):
        self.__sumo_net = sumolib.net.readNet(FileSetup.NET_SUMO.value, withInternal=True)
        self.__customer_setup = utils.read_setup(FileSetup.CUSTOMER.value)
        self.__driver_setup = utils.read_setup(FileSetup.DRIVER.value)
        self.__simulator_setup = utils.read_setup(FileSetup.SIMULATOR.value)
        self.__scenario = Scenario(utils.read_setup(FileSetup.SCENARIO.value))
        self.__provider = Provider(utils.read_setup(FileSetup.PROVIDER.value), self.__sumo_net)
        self.__net = Net(utils.read_setup(FileSetup.NET_SIMULATOR.value), self.__sumo_net)
        self.__generation_dict = utils.read_setup(FileSetup.MOBILITY_SIMULATOR.value)
        self.__city = city
        self.__driver_id_counter = 0
        self.__customer_id_counter = 0
        self.__ride_id_counter = 0
        self.__traffic_counter = 0
        self.__sim_drivers_ids = []
        self.__sim_customers_ids = []
        self.__drivers = {}
        self.__customers = {}
        self.__drivers_by_state = {k.value: [] for k in DriverState}
        self.__customers_by_state = {k.value: [] for k in CustomerState}
        self.__temp_drivers_gen = 0
        self.__temp_customers_gen = 0
        self.__timeline_generation = utils.read_setup(FileSetup.MOBILITY_SIMULATOR.value)
        self.__scenario = Scenario(utils.read_setup(FileSetup.SCENARIO.value))
        self.__cpu_cores = multiprocessing.cpu_count()
        self.__statistics = Statistics(
            self.__simulator_setup[ConfigEnum.CHECKPOINTS.value][ConfigEnum.SIMULATION_DURATION.value],
            self.__net.get_all_taz_ids(NetType.BOUNDARY_NET)
        )

    def __check_customers_list(
            self,
            timestamp: float
    ):
        # Solve disalignments
        def __solve_customers_inconsistencies(customer_id: str):
            if not customer_id in current_customers_list:
                # print(f"Sumo forced {customer_id} remotion.")
                self.__remove_customer_by_state(
                    timestamp,
                    customer_id
                )
            elif not customer_id in self.__sim_customers_ids:
                # print(f"{customer_id} not removed by the sumo simulator.")
                traci.person.remove(customer_id)
        current_customers_list = traci.person.getIDList()
        if not set(current_customers_list) == set(self.__sim_customers_ids):
            customers_diff = list(set(self.__sim_customers_ids).symmetric_difference(set(current_customers_list)))
            for customer_id in customers_diff:
                __solve_customers_inconsistencies(customer_id)


    def __check_drivers_list(
            self,
            timestamp
    ):
        current_drivers_list = traci.vehicle.getIDList()
        if not set(current_drivers_list) == set(self.__sim_drivers_ids):
            drivers_diff = list(set(self.__sim_drivers_ids).symmetric_difference(set(current_drivers_list)))
            for driver_id in drivers_diff:
                if not driver_id in current_drivers_list:
                    # print(f"Sumo forced {driver_id} remotion.")
                    driver_info = self.__drivers[driver_id].get_info()
                    self.__remove_driver_by_state(
                        timestamp,
                        driver_id,
                        DriverRemotionIdentifier.TRACI_FORCED_REMOTION
                    )
                elif not driver_id in self.__sim_drivers_ids:
                    # print(f"{driver_id} not removed by the sumo simulator.")
                    traci.vehicle.remove(driver_id)

    def __generate_agent_id(
            self,
            agent_type: Type[HumanType]
    ) -> str:
        assert agent_type in [HumanType.DRIVER, HumanType.CUSTOMER], "Simulator.generateAgentId - unknown agentType"
        counter = 0
        if agent_type == HumanType.CUSTOMER:
            counter = self.__customer_id_counter
            self.__customer_id_counter += 1
        else:
            counter = self.__driver_id_counter
            self.__driver_id_counter += 1
        return f"{agent_type.value.lower()}_{counter}"

    def __generate_sim_customer(
            self,
            timestamp: float,
            customer_id: str,
            personality: Type[PersonalityType],
            src_edge_id: str,
            dst_edge_id: str,
            src_pos: float,
            dst_pos: float,
            state: Type[CustomerState] = CustomerState.ACTIVE
    ):
        if customer_id in traci.person.getIDList():
            customer = Customer(
                float(timestamp),
                customer_id,
                personality,
                state,
                src_edge_id,
                dst_edge_id,
                src_pos,
                dst_pos
            )
            self.__customers[customer_id] = customer
            self.__customers_by_state[state.value].append(customer_id)
            self.__sim_customers_ids.append(customer_id)

    def __generate_customer_requests(
            self,
            timestamp: float
    ):
        active_customers = self.__customers_by_state[CustomerState.ACTIVE.value]
        for customer_id in active_customers:
            ride_id = f"ride_{self.__ride_id_counter}"
            self.__ride_id_counter += 1
            customer_info = self.__customers[customer_id].get_info()
            src_edge_id = customer_info[CustomerIdentifier.SRC_EDGE_ID.value]
            src_taz_id = self.__net.get_taz_id_from_edge_id(src_edge_id)
            dst_edge_id = customer_info[CustomerIdentifier.DST_EDGE_ID.value]
            src_pos = customer_info[CustomerIdentifier.SRC_POS.value]
            dst_pos = customer_info[CustomerIdentifier.DST_POS.value]
            stats = {
                RideIdentifier.STAT_SRC_TAZ_ID.value: src_edge_id,
                RideIdentifier.STAT_DST_TAZ_ID.value: dst_edge_id
            }
            ride = Ride(ride_id, customer_id, src_edge_id, dst_edge_id, src_pos, dst_pos, stats)
            self.__provider.receive_request(ride)
            self.__statistics.global_indicators.received_request(
                timestamp,
                src_taz_id
            )

    def __generate_driver_random_route(
            self,
            timestamp,
            driver_id,
            dst_taz_id
    ) -> Union[Type[Route], None]:
        driver = self.__drivers[driver_id]
        driver_edge_id = traci.vehicle.getRoute(driver_id)[traci.vehicle.getRouteIndex(driver_id)]
        driver_pos = traci.vehicle.getLanePosition(driver_id)
        random_route = self.__net.generate_random_sim_route_in_taz(
            timestamp,
            dst_taz_id,
            driver_edge_id,
            driver_pos
        )
        if random_route is not None:
            try:
                self.__start_sumo_route(
                    timestamp,
                    driver_id,
                    random_route
                )
            except:
                raise Exception(f"Simulator.__generate_driver_random_route - Impossible to generate route for {driver_id}")
        return random_route

    def __generate_sim_driver(
            self,
            timestamp: float,
            driver_id: str,
            personality: Type[PersonalityType],
            src_pos: float,
            dst_pos: float,
            state: Type[DriverState] = DriverState.IDLE
    ):
        if driver_id in traci.vehicle.getIDList():
            route_edge_id_list = list(traci.vehicle.getRoute(driver_id))
            route = self.__net.generate_sim_route_from_edge_id_list(
                timestamp,
                route_edge_id_list,
                src_pos,
                dst_pos
            )
            driver = Driver(timestamp, driver_id, personality, route, state)
            self.__drivers[driver_id] = driver
            self.__drivers_by_state[DriverState.IDLE.value].append(driver_id)
            self.__sim_drivers_ids.append(driver_id)
            self.__statistics.drivers_stats.added_driver(
                timestamp,
                driver_id
            )

    def __get_available_drivers(
            self,
            taz_id: str
    ) -> Dict[str, Type[DriverInfo]]:
        idle_drivers = self.__get_drivers_info_by_states([DriverState.IDLE])
        drivers_moving_in_taz = self.__get_drivers_info_moving_in_taz(taz_id)
        available_drivers = {
            **idle_drivers,
            **drivers_moving_in_taz
        }
        return available_drivers

    def __get_customers_in_taz(
            self,
            taz_id: str
    ) -> Dict[str, CustomerInfo]:
        customers_in_taz = {}
        customer_ids_snapshot = [*self.__customers.keys()]
        for customer_id in customer_ids_snapshot:
            customer_info = self.__customers[customer_id].get_info()
            if not customer_info[CustomerIdentifier.CUSTOMER_STATE.value] == CustomerState.INACTIVE:
                customer_edge_id = traci.person.getRoadID(customer_id)
                customer_taz_id = self.__net.get_taz_id_from_edge_id(
                    customer_edge_id,
                    NetType.BOUNDARY_NET
                )
                if taz_id == customer_taz_id:
                    customers_in_taz[customer_info[CustomerIdentifier.CUSTOMER_ID.value]] = customer_info
        return customers_in_taz

    def __get_drivers_in_taz(
            self,
            taz_id: str
    ):
        drivers_in_taz = {}
        driver_ids_snapshot = [*self.__drivers.keys()]
        for driver_id in driver_ids_snapshot:
            if self.__is_driver_still_active(driver_id):
                driver_info = self.__drivers[driver_id].get_info()
                driver_edge_id = traci.vehicle.getRoute(driver_id)[traci.vehicle.getRouteIndex(driver_id)]
                driver_taz_id = self.__net.get_taz_id_from_edge_id(driver_edge_id, NetType.BOUNDARY_NET)
                if not driver_info[CustomerIdentifier.CUSTOMER_STATE.value] == CustomerState.INACTIVE:
                    if taz_id == driver_taz_id:
                        drivers_in_taz[driver_id] = driver_info
        return drivers_in_taz

    def __get_drivers_info_moving_in_taz(
            self,
            taz_id: str
    ):
        drivers_moving_in_taz = {}
        driver_ids_snapshot = [*self.__drivers.keys()]
        for driver_id in driver_ids_snapshot:
            driver_info = self.__drivers[driver_id].get_info()
            assert driver_info[DriverIdentifiers.ROUTE.value] is not None, "Simulator.__get_drivers_info_moving_in_taz - driver route not found"
            driver_route = driver_info[DriverIdentifiers.ROUTE.value]
            dst_taz_id = driver_route[RouteIdentifier.DST_EDGE_ID.value]
            if taz_id == dst_taz_id:
                drivers_moving_in_taz[driver_info[DriverIdentifiers.DRIVER_ID.value]] = driver_info
        return drivers_moving_in_taz

    def __get_drivers_info_in_neighbour_tazs(
            self,
            taz_ids,
            net_type: NetType = NetType.BOUNDARY_NET
    ):
        available_drivers = {}
        driver_ids = []
        for taz_id in taz_ids:
            driver_ids.extend(
                self.__net.get_driver_ids_in_taz(
                    taz_id,
                    net_type
                )
            )
        for driver_id in driver_ids:
            driver = self.__drivers[driver_id]
            driver_info = driver.get_info()
            if driver_info[DriverIdentifiers.DRIVER_STATE.value] == DriverState.IDLE:
                available_drivers[driver_id] = driver_info
        return available_drivers

    def __get_drivers_info(self):
        drivers_info = {}
        for driver_id, driver in self.__drivers.items():
            drivers_info[driver_id] = driver.get_info()
        return drivers_info

    def __get_drivers_by_states(
            self,
            states: list[Type[DriverState]]
    ) -> list[Type[Driver]]:
        states = list(map(lambda s: s.value, states))
        drivers = []
        for state, drivers_ids_by_state in self.__drivers_by_state.items():
            if state in states:
                for driver_id in drivers_ids_by_state:
                    driver = self.__drivers[driver_id]
                    drivers.append(driver)
        return drivers

    def __get_drivers_info_by_states(
            self,
            states: list[Type[DriverState]]
    ) -> Dict[str, Type[DriverInfo]]:
        states = list(map(lambda s: s.value, states))
        drivers_info = {}
        for state, drivers_ids_by_state in self.__drivers_by_state.items():
            if state in states:
                for driver_id in drivers_ids_by_state:
                    driver = self.__drivers[driver_id]
                    driver_info = driver.get_info()
                    drivers_info[driver_id] = driver_info
        return drivers_info

    def __get_human_distribution(
            self,
            policy: Dict[str,list[[float, float, float]]],
            personality: Type[PersonalityType]
    ):
        assert personality in [PersonalityType.HURRY.value, PersonalityType.NORMAL.value, PersonalityType.GREEDY.value], f"Simulator.__get_human_distribution - Unknown personality: {personality}"
        return policy[personality.lower()]

    def __is_driver_still_active(
            self,
            driver_id: str
    ):
        driver = self.__drivers[driver_id]
        driver_info = driver.get_info()
        return not driver_info[HumanEnum.HUMAN_STATE.value] == DriverState.INACTIVE

    def __manage_pending_request(
            self,
            timestamp: float
    ):
        def __route_failure_repair(
                ride_info: Type[RideInfo],
                customer_id: str,
                driver_id: str
        ):
            driver = self.__drivers[driver_id]
            customer = self.__customers[customer_id]
            driver_info = driver.reject_request()
            assert driver_id in self.__drivers_by_state[DriverState.RESPONDING.value], f"Simulator.__manage_pending_request - unexpected driver state for {driver_id}"
            self.__drivers_by_state[DriverState.RESPONDING.value].remove(driver_id)
            self.__drivers_by_state[DriverState.IDLE.value].append(driver_id)
            ride_info = self.__provider.ride_request_rejected(
                timestamp,
                ride_info[RideIdentifier.RIDE_ID.value],
                driver_id
            )
            ride_info = self.__provider.set_ride_request_state(
                ride_info[RideIdentifier.RIDE_ID.value],
                RideRequestState.REJECTED
            )

        def __process_pending_request(ride_info: RideInfo):
            driver_acceptance_distribution = self.__driver_setup[DriverIdentifiers.DRIVER_ACCEPTANCE_DISTRIBUTION.value]
            customer_info = self.__customers[ride_info[RideIdentifier.CUSTOMER_ID.value]].get_info()
            customer_id = customer_info[CustomerIdentifier.CUSTOMER_ID.value]
            customer_edge_id = traci.person.getRoadID(customer_id)
            customer_taz_id = self.__net.get_taz_id_from_edge_id(customer_edge_id, NetType.BOUNDARY_NET)
            taz_info = self.__net.get_taz_info(customer_taz_id)
            surge_multiplier = taz_info[ProviderIdentifier.SURGE_MULTIPLIERS.value][0]
            available_drivers_info = self.__get_available_drivers(customer_taz_id)      ### consider to use centroids to widen the tazs to find available drivers
            ride_info, ride_request_state, driver_id = self.__provider.manage_pending_request(
                timestamp,
                ride_info,
                available_drivers_info
            )
            customer_id = ride_info[RideIdentifier.CUSTOMER_ID.value]
            if ride_request_state == RideRequestState.SENT:
                assert not driver_id == None, "Simulator.__manage_pending_request - Unexpected driver id None."
                drivers_info = self.__send_request_to_driver(driver_id)
                self.__provider.set_ride_request_state(ride_info[RideIdentifier.RIDE_ID.value], RideRequestState.SENT)
            elif ride_request_state == RideRequestState.WAITING:
                assert driver_id is not None, "Simulator.__manage_pending_request - Unexpected undefined driver id when request state has been sent. [1]"
                if not self.__is_driver_still_active(driver_id):
                    assert driver_id in self.__drivers_by_state[DriverState.INACTIVE.value], f"Simulator.__manage_pending_request - unexpected driver state for {driver_id}"
                    ride_info = self.__provider.ride_request_rejected(
                        timestamp,
                        ride_info[RideIdentifier.RIDE_ID.value],
                        driver_id
                    )
                    ride_info = self.__provider.set_ride_request_state(
                        ride_info[RideIdentifier.RIDE_ID.value],
                        RideRequestState.REJECTED
                    )
                    self.__statistics.global_indicators.rejected(
                        timestamp,
                        customer_taz_id
                    )
            elif ride_request_state in [RideRequestState.NONE, RideRequestState.ROUTE_NOT_FOUND]:
                assert customer_id is not None, "Simulator.managePendingRequest - id customer undefined on ride request not accomplished."
                self.__remove_customer(customer_id)
                if ride_request_state == RideRequestState.NONE:
                    self.__statistics.global_indicators.request_not_served(
                        timestamp,
                        customer_taz_id
                    )
                    self.__update_surge_multiplier_not_served(timestamp, customer_taz_id)
            elif ride_request_state == RideRequestState.RESPONSE:
                assert driver_id is not None, "Simulator.__manage_pending_request - Unexpected undefined driver id when request state has been sent. [2]"
                if not self.__is_driver_still_active(driver_id):
                    assert driver_id in self.__drivers_by_state[DriverState.INACTIVE.value], f"Simulator.__manage_pending_request - unexpected driver state for {driver_id}"
                    ride_info = self.__provider.ride_request_rejected(
                        timestamp,
                        ride_info[RideIdentifier.RIDE_ID.value],
                        driver_id
                    )
                    ride_info = self.__provider.set_ride_request_state(ride_info[RideIdentifier.RIDE_ID.value], RideRequestState.REJECTED)
                    self.__statistics.global_indicators.rejected(
                        timestamp,
                        customer_taz_id
                    )
                    return
                driver = self.__drivers[driver_id]
                driver_info = driver.get_info()
                personality = driver_info[DriverIdentifiers.PERSONALITY.value]
                driver_policy = self.__get_human_distribution(driver_acceptance_distribution, personality)
                accept = driver.accept_ride_conditions(surge_multiplier, driver_policy)
                if accept:
                    customer_dst_edge_id = customer_info[CustomerIdentifier.DST_EDGE_ID.value]
                    customer_src_pos = customer_info[CustomerIdentifier.SRC_POS.value]
                    customer_dst_pos = customer_info[CustomerIdentifier.DST_POS.value]
                    driver_edge_id = traci.vehicle.getRoute(driver_id)[traci.vehicle.getRouteIndex(driver_id)]
                    driver_src_pos = traci.vehicle.getLanePosition(driver_id)
                    meeting_route = self.__net.generate_sim_route_from_src_dst_edge_ids(
                        timestamp,
                        driver_edge_id,
                        customer_edge_id,
                        driver_src_pos,
                        customer_src_pos
                    )
                    if meeting_route is not None:
                        assert ride_info[RideIdentifier.REQUEST.value][RequestIdentifier.CURRENT_CANDIDATE.value] is not None, "Simulator.__manage_pending_request - candidate undefined on ride request response"
                        customer = self.__customers[customer_id]
                        expected_meeting_travel_time = meeting_route.get_expected_travel_time()
                        expected_meeting_length = meeting_route.get_expected_length()
                        stats = {
                            RideIdentifier.STAT_TIMESTAMP_PICKUP.value: timestamp,
                            RideIdentifier.STAT_EXPECTED_MEETING_LENGTH.value: expected_meeting_length,
                            RideIdentifier.STAT_EXPECTED_MEETING_TRAVEL_TIME.value: expected_meeting_travel_time,
                            RideIdentifier.STAT_SURGE_MULTIPLIER.value: surge_multiplier
                        }
                        try:
                            self.__start_sumo_route(
                                timestamp,
                                driver_id,
                                meeting_route,
                                customer_id
                            )
                        except:
                            driver.reject_request()
                            self.__drivers_by_state[DriverState.RESPONDING.value].remove(driver_id)
                            self.__drivers_by_state[DriverState.IDLE.value].append(driver_id)
                            ride_info = self.__provider.ride_request_rejected(
                                timestamp,
                                ride_info[RideIdentifier.RIDE_ID.value],
                                driver_id
                            )
                            ride_info = self.__provider.set_ride_request_state(ride_info[RideIdentifier.RIDE_ID.value], RideRequestState.REJECTED)
                            self.__statistics.global_indicators.sim_failure_rejection(
                                timestamp,
                                customer_taz_id
                            )
                            return
                        customer_info = customer.update_pickup()
                        driver_info = driver.update_pickup(meeting_route)
                        self.__drivers_by_state[DriverState.RESPONDING.value].remove(driver_id)
                        self.__drivers_by_state[DriverState.PICKUP.value].append(driver_id)
                        self.__customers_by_state[CustomerState.PENDING.value].remove(customer_id)
                        self.__customers_by_state[CustomerState.PICKUP.value].append(customer_id)
                        ride_info = self.__provider.update_ride_accepted(
                            ride_info[RideIdentifier.RIDE_ID.value],
                            driver_id,
                            meeting_route,
                            stats
                        )
                        self.__provider.update_ride_pickup(ride_info[RideIdentifier.RIDE_ID.value])
                        self.__statistics.global_indicators.accepted_request(
                            timestamp,
                            customer_taz_id
                        )
                    else:
                        #print("Simulator.__manage_pending_request - meeting route not found.")
                        self.__statistics.global_indicators.sim_failure_rejection(
                            timestamp,
                            customer_taz_id
                        )
                        __route_failure_repair(
                            ride_info,
                            customer_id,
                            driver_id
                        )
                else:
                    driver_info = driver.reject_request()
                    self.__drivers_by_state[DriverState.RESPONDING.value].remove(driver_id)
                    self.__drivers_by_state[DriverState.IDLE.value].append(driver_id)
                    ride_info = self.__provider.ride_request_rejected(
                        timestamp,
                        ride_info[RideIdentifier.RIDE_ID.value],
                        driver_id
                    )
                    ride_info = self.__provider.set_ride_request_state(ride_info[RideIdentifier.RIDE_ID.value], RideRequestState.REJECTED)
                    self.__statistics.global_indicators.rejected(
                        timestamp,
                        customer_taz_id
                    )
        pending_requests = self.__provider.get_rides_info_by_state(RideState.PENDING.value)
        for request in pending_requests:
            __process_pending_request(request)

    def __move_driver_to_taz(
            self,
            timestamp: float,
            driver_id: str,
            dst_taz_id: str
    ):
        driver = self.__drivers[driver_id]
        driver_edge_id = traci.vehicle.getRoute(driver_id)[traci.vehicle.getRouteIndex(driver_id)]
        driver_pos = traci.vehicle.getLanePosition(driver_id)
        try:
            random_route = self.__generate_driver_random_route(
                timestamp,
                driver_id,
                dst_taz_id
            )
            driver_edge_id = traci.vehicle.getRoute(driver_id)[traci.vehicle.getRouteIndex(driver_id)]
            src_taz_id = self.__net.get_taz_id_from_edge_id(driver_edge_id, NetType.BOUNDARY_NET)
            if random_route is not None:
                driver.set_route(random_route)
                driver.set_state(DriverState.MOVING)
                self.__drivers_by_state[DriverState.IDLE.value].remove(driver_id)
                self.__drivers_by_state[DriverState.MOVING.value].append(driver_id)
                self.__statistics.drivers_stats.moving_to_taz(
                    timestamp,
                    driver_id,
                    src_taz_id,
                    dst_taz_id
                )
                # print(f"Move driver {driver_id} to area {dst_taz_id}")
            else:
                self.__remove_driver(
                    timestamp,
                    driver_id,
                    DriverRemotionIdentifier.ROUTE_NOT_FOUND
                )
        except:
            self.__remove_driver(
                timestamp,
                driver_id,
                DriverRemotionIdentifier.SET_ROUTE_FAILED
            )
            return

    def __perform_scenario_event(
            self,
            timestamp: float,
            event_type: Type[EventType],
            params: dict          ###
    ):
        if event_type == EventType.HUMAN_PERSONALITY_POLICY:
            pass
        if event_type == EventType.DRIVERS_STRIKE:
            pass
        if event_type == EventType.BEHAVIOR_CHANGE:
            pass
        if event_type == EventType.FLASH_MOB:
            pass
        if event_type == EventType.SUDDEN_REQUESTS:
            pass

    def __process_rides(
            self,
            timestamp:str
    ):
        unprocessed_requests = self.__provider.get_unprocessed_requests()
        for ride_id in unprocessed_requests:
            ride_info = self.__provider.get_ride_info(ride_id)
            customer = self.__customers[ride_info[RideIdentifier.CUSTOMER_ID.value]]
            customer_info = customer.get_info()
            customer_id = customer_info[CustomerIdentifier.CUSTOMER_ID.value]
            customer_acceptance_policy = self.__customer_setup[CustomerIdentifier.CUSTOMER_ACCEPTANCE_DISTRIBUTION.value]
            personality = customer.get_info()[HumanEnum.PERSONALITY.value]
            customer_edge_id = traci.person.getRoadID(customer_id)
            customer_taz_id = self.__net.get_taz_id_from_edge_id(customer_edge_id, NetType.BOUNDARY_NET)
            taz_info = self.__net.get_taz_info(customer_taz_id)
            surge_multiplier = taz_info[ProviderIdentifier.SURGE_MULTIPLIERS.value][0]
            customer_policy = self.__get_human_distribution(customer_acceptance_policy, personality)
            accept = customer.accept_ride_conditions(surge_multiplier, customer_policy)
            if accept:
                customer_info = customer.update_pending()
                available_drivers_info = self.__get_available_drivers(customer_taz_id)
                self.__provider.process_customer_request(
                    timestamp,
                    ride_info,
                    customer_edge_id,
                    available_drivers_info
                )
                self.__customers_by_state[CustomerState.ACTIVE.value].remove(customer_info["id"])
                self.__customers_by_state[CustomerState.PENDING.value].append(customer_info["id"])
            else:
                self.__remove_customer(customer_info[CustomerIdentifier.CUSTOMER_ID.value])
                ride_info = self.__provider.ride_request_canceled(ride_id)
                self.__statistics.global_indicators.canceled_request(
                    timestamp,
                    customer_taz_id
                )

    def __refine_ride_route(
            self,
            timestamp: float,
            driver_id: str,
            ride_id: str,
            route: RouteInfo,
            route_type: Type[RouteType] = RouteType.SUMO
    ):
        driver_edge_id = traci.vehicle.getRoute(driver_id)[traci.vehicle.getRouteIndex(driver_id)]
        driver_edge = self.__sumo_net.getEdge(driver_edge_id)
        driver_edge_ids_outgoings = list(map(lambda e: e.getID(), driver_edge.getOutgoing()))
        driver_pos = traci.vehicle.getLanePosition(driver_id)
        route_src_edge_id = route[RouteIdentifier.SRC_EDGE_ID.value]
        route_dst_edge_id = route[RouteIdentifier.DST_EDGE_ID.value]
        route_dst_pos = route[RouteIdentifier.DST_POS.value]
        assert route_src_edge_id in driver_edge_ids_outgoings, f"Simulator.__refine_ride_route - unexpected {driver_id} position with respect to destination route."
        refined_route = self.__net.generate_sim_route_from_src_dst_edge_ids(
            timestamp,
            driver_edge_id,
            route_dst_edge_id,
            driver_pos,
            route_dst_pos
        )
        if refined_route is not None:
            ride_info = self.__provider.refine_ride_route(
                ride_id,
                refined_route,
                route_type
            )
            return (ride_info, refined_route)
        else:
            #print(f"Simulator.__refine_route - cannot find route for {driver_id} from {driver_edge_id} to {route_dst_edge_id}")
            ride_info = self.__provider.get_ride_info(ride_id)
            return (ride_info, None)

    def __remove_customer(
            self,
            customer_id:str
    ):
        #print(f"Remove {customer_id}")
        customer = self.__customers[customer_id]
        customer_info = customer.get_info()
        if customer_id not in self.__customers_by_state[customer_info[HumanEnum.HUMAN_STATE.value].value]:
            #f"{customer_id} with state {customer_info[HumanEnum.HUMAN_STATE.value]}")
            pass
        self.__customers_by_state[customer_info[HumanEnum.HUMAN_STATE.value].value].remove(customer_id)
        self.__customers_by_state[CustomerState.INACTIVE.value].append(customer_id)
        customer.set_state(CustomerState.INACTIVE)
        self.__sim_customers_ids.remove(customer_id)
        traci_customers_list = traci.person.getIDList()
        if customer_id in traci_customers_list:
            traci.person.remove(customer_id)
        else:
            #print(f"Person {customer_id} already removed..."
            pass

    def __remove_customer_by_state(
            self,
            timestamp,
            customer_id:str
    ):
        customer = self.__customers[customer_id]
        customer_info = customer.get_info()
        if customer_info[HumanEnum.HUMAN_STATE.value] in [CustomerState.ACTIVE, CustomerState.PENDING]:
            ride_info = self.__provider.find_ride_by_agent_id(customer_info, HumanType.CUSTOMER)
            if ride_info is not None:
                ride_info = self.__provider.remove_ride_simulation_error(ride_info[RideIdentifier.RIDE_ID.value])
            self.__remove_customer(customer_id)
        elif customer_info[HumanEnum.HUMAN_STATE.value] in [CustomerState.PICKUP, CustomerState.ON_ROAD]:
            ride_info = self.__provider.find_ride_by_agent_id(customer_info, HumanType.CUSTOMER)
            self.__safe_remotion(
                timestamp,
                ride_info[RideIdentifier.DRIVER_ID.value],
                customer_id,
                ride_info[RideIdentifier.RIDE_ID.value],
                DriverRemotionIdentifier.TRACI_FORCED_CUSTOMER_REMOTION_DURING_RIDE
            )

    def __remove_driver(
            self,
            timestamp: float,
            driver_id: str,
            reason: Type[DriverRemotionIdentifier]
    ):
        #print(f"Remove {driver_id}")
        driver = self.__drivers[driver_id]
        driver_info = driver.get_info()
        self.__drivers_by_state[driver_info[DriverIdentifiers.DRIVER_STATE.value].value].remove(driver_id)
        self.__drivers_by_state[DriverState.INACTIVE.value].append(driver_id)
        driver_info = driver.set_state(DriverState.INACTIVE)
        self.__sim_drivers_ids.remove(driver_id)
        traci_drivers_list = traci.vehicle.getIDList()
        self.__statistics.drivers_stats.removed_driver(
            timestamp,
            reason,
            driver_info
        )
        if driver_id in  traci_drivers_list:
            traci.vehicle.remove(driver_id)
        else:
            #print(f"Driver {driver_id} already removed...")
            pass

    def __remove_driver_by_state(
            self,
            timestamp,
            driver_id: str,
            reason: Type[DriverRemotionIdentifier]
    ):
        driver = self.__drivers[driver_id]
        driver_info = driver.get_info()
        driver_edge_id = driver_info[DriverIdentifiers.CURRENT_EDGE_ID.value]
        driver_taz_id = self.__net.get_taz_id_from_edge_id(driver_edge_id)
        if driver_info[DriverIdentifiers.DRIVER_STATE.value] in [DriverState.IDLE, DriverState.MOVING]:
            self.__remove_driver(
                timestamp,
                driver_id,
                reason
            )
        elif driver_info[DriverIdentifiers.DRIVER_STATE.value] in [DriverState.RESPONDING]:
            ride_info = self.__provider.find_ride_by_agent_id(driver_info, HumanType.DRIVER)
            if ride_info is None:
                print(traci.vehicle.getIDList())
                print(traci.vehicle.getRoute(driver_id))
                print(traci.vehicle.getRouteIndex(driver_id))
                print(driver_info)
            ride_info = self.__provider.ride_request_rejected(
                timestamp,
                ride_info[RideIdentifier.RIDE_ID.value],
                driver_id
            )
            ride_info = self.__provider.set_ride_request_state(
                ride_info[RideIdentifier.RIDE_ID.value],
                RideRequestState.REJECTED
            )
            self.__statistics.global_indicators.sim_failure(
                timestamp,
                driver_taz_id
            )
            self.__remove_driver(
                timestamp,
                driver_id,
                reason
            )
        elif driver_info[DriverIdentifiers.DRIVER_STATE.value] in [DriverState.PICKUP, DriverState.ON_ROAD]:
            ride_info = self.__provider.find_ride_by_agent_id(driver_info, HumanType.DRIVER)
            self.__safe_remotion(
                timestamp,
                driver_info[DriverIdentifiers.DRIVER_ID.value],
                ride_info[RideIdentifier.CUSTOMER_ID.value],
                ride_info[RideIdentifier.RIDE_ID.value],
                reason
            )

    def __update_tazs(
            self,
            timestamp: str
    ):
        taz_ids = self.__net.get_all_taz_ids(NetType.BOUNDARY_NET)
        for taz_id in taz_ids:
            drivers_in_taz = self.__get_drivers_in_taz(taz_id)
            drivers_in_taz_array = drivers_in_taz.values()
            customers_in_taz = self.__get_customers_in_taz(taz_id)
            idle_drivers = []
            responding_drivers = []
            pickup_drivers = []
            on_road_drivers = []
            moving_drivers = []
            active_customers = []
            pending_customers = []
            pickup_customers = []
            on_road_customers = []

            for driver in drivers_in_taz_array:
                if driver[DriverIdentifiers.DRIVER_STATE.value] == DriverState.IDLE:
                    idle_drivers.append(driver)
                elif driver[DriverIdentifiers.DRIVER_STATE.value] == DriverState.RESPONDING:
                    responding_drivers.append(driver)
                if driver[DriverIdentifiers.DRIVER_STATE.value] == DriverState.PICKUP:
                    pickup_drivers.append(driver)
                if driver[DriverIdentifiers.DRIVER_STATE.value] == DriverState.ON_ROAD:
                    on_road_drivers.append(driver)
                if driver[DriverIdentifiers.DRIVER_STATE.value] == DriverState.MOVING:
                    moving_drivers.append(driver)

            for customer in customers_in_taz.values():
                if customer[CustomerIdentifier.CUSTOMER_STATE.value] == CustomerState.ACTIVE:
                    active_customers.append(customer)
                if customer[CustomerIdentifier.CUSTOMER_STATE.value] == CustomerState.PENDING:
                    pending_customers.append(customer)
                if customer[CustomerIdentifier.CUSTOMER_STATE.value] == CustomerState.PICKUP:
                    pickup_customers.append(customer)
                if customer[CustomerIdentifier.CUSTOMER_STATE.value] == CustomerState.ON_ROAD:
                    on_road_customers.append(customer)

            self.__statistics.global_indicators.idle_drivers(
                timestamp,
                taz_id,
                len(idle_drivers)
            )
            self.__statistics.global_indicators.responding_drivers(
                timestamp,
                taz_id,
                len(responding_drivers)
            )
            self.__statistics.global_indicators.pickup_drivers(
                timestamp,
                taz_id,
                len(pickup_drivers)
            )
            self.__statistics.global_indicators.on_road_drivers(
                timestamp,
                taz_id,
                len(on_road_drivers)
            )
            self.__statistics.global_indicators.moving_drivers(
                timestamp,
                taz_id,
                len(moving_drivers)
            )
            self.__statistics.global_indicators.active_customers(
                timestamp,
                taz_id,
                len(active_customers)
            )
            self.__statistics.global_indicators.pending_customers(
                timestamp,
                taz_id,
                len(pending_customers)
            )
            self.__statistics.global_indicators.pickup_customers(
                timestamp,
                taz_id,
                len(pickup_customers)
            )
            self.__statistics.global_indicators.on_road_customers(
                timestamp,
                taz_id,
                len(on_road_customers)
            )

            checkpoint_surge_multiplier = self.__simulator_setup[ConfigEnum.CHECKPOINTS.value][ConfigEnum.TIME_UPDATE_SURGE_MULTIPLIER.value]
            if timestamp % self.__simulator_setup[ConfigEnum.CHECKPOINTS.value][ConfigEnum.TIME_UPDATE_SURGE_MULTIPLIER.value] == 0.0:
                num_not_served = 0
                taz_info = self.__net.get_taz_info(taz_id)
                surge_multiplier = taz_info[ProviderIdentifier.SURGE_MULTIPLIERS.value][0]
                global_indicators_info = self.__statistics.global_indicators.get_global_indicators_info()
                start_timestamp = int(timestamp) - checkpoint_surge_multiplier if timestamp >= checkpoint_surge_multiplier else 0
                for i in range(int(start_timestamp) + 1, int(timestamp)):
                    num_not_served += global_indicators_info[StatisticIdentifier.NOT_SERVED][i][taz_id]
                balance = self.__provider.compute_balance(
                    len(pending_customers),
                    len(idle_drivers) + len(responding_drivers),
                    num_not_served
                )
                self.__net.update_taz_balance(
                    taz_id,
                    balance,
                    NetType.BOUNDARY_NET
                )
                surge_multiplier_increment = self.__provider.compute_surge_multiplier_increment(balance)
                new_surge_multiplier = max(0.7, min(surge_multiplier + surge_multiplier_increment, 3.5))
                self.__net.update_taz_surge_multiplier(
                    taz_id,
                    new_surge_multiplier,
                    NetType.BOUNDARY_NET
                )


    def __safe_remotion(
            self,
            timestamp,
            driver_id: str,
            customer_id: str,
            ride_id: str,
            reason: Type[DriverRemotionIdentifier]
    ):
        self.__remove_driver(
            timestamp,
            driver_id,
            reason
        )
        self.__remove_customer(customer_id)
        self.__provider.remove_ride_simulation_error(ride_id)

    def __send_request_to_driver(
            self,
            driver_id: str
    ):
        driver = self.__drivers[driver_id]
        self.__drivers_by_state[DriverState.IDLE.value].remove(driver_id)
        self.__drivers_by_state[DriverState.RESPONDING.value].append(driver_id)
        return driver.receive_request()

    def __set_driver_route(
            self,
            driver_id: str,
            route: Type[Route],
            stop_pos: float = -1,
            flags: int = 0,
            duration: int = 1
    ):
        driver = self.__drivers[driver_id]
        dst_edge_id = route.get_destination_edge_id()
        dst_edge = self.__sumo_net.getEdge(dst_edge_id)
        if stop_pos == -1:
            dst_edge_length = dst_edge.getLength()
            stop_pos = round(dst_edge_length/2,2) # random.random() * dst_edge_length
        if stop_pos < 1.0:
            raise Exception(f"Simulation.__set_driver_route - Raised exception to avoid sumo bug on stop pos < 1 {stop_pos}")
        if len(route.get_route_edge_id_list()) == 1:
            raise Exception(f"Simulation.__set_driver_route - Raised exception to avoid sumo bug when customer and driver are on the same edge, but customer pos < driver pos")
        try:
            route_id = route.get_route_id()
            traci.vehicle.setRouteID(driver_id, route_id)
            traci.vehicle.setStop(driver_id, dst_edge_id, stop_pos, duration=duration, flags=flags)
        except:
            driver_info = driver.get_info()
            driver_route = driver_info[DriverIdentifiers.ROUTE.value]
            route_index = traci.vehicle.getRouteIndex()
            driver_road = traci.vehicle.getRoadID(driver_id)
            driver_edge = traci.vehicle.getRoute(driver_id)[route_index]
            print(driver_id)
            print(driver_route)
            print(driver_road)
            print(driver_edge)
            print(route)
            raise Exception(f"Simulation.__set_driver_route - Impossible to set driver route for {driver_id}")
        driver.set_route_destination_position(stop_pos)

    def __start_sumo_route(
            self,
            timestamp: float,
            driver_id: str,
            route: Type[Route],
            customer_id: str = None
    ):
        driver = self.__drivers[driver_id]
        driver_info = driver.get_info()
        if driver_info[DriverIdentifiers.DRIVER_STATE.value] == DriverState.RESPONDING:
            assert customer_id is not None, "Simulator.__start_sumo_route - customer id is None."
            dst_pos = route.get_destination_position()
            #print(f"Pickup route for driver {driver_info['id']} and customer {customer_id}.")
            try:
                self.__set_driver_route(
                    driver_id,
                    route,
                    dst_pos,
                    flags = 2,
                    duration = 2
                )
            except:
                raise Exception(f"Simulator.__start_sumo_route - impossible to start route for {driver_id}")
        elif driver_info[DriverIdentifiers.DRIVER_STATE.value] == DriverState.PICKUP:
            dst_edge_id = route.get_destination_edge_id()
            traci.person.appendDrivingStage(
                customer_id,
                dst_edge_id,
                driver_id
            )
            traci.person.appendWaitingStage(
                customer_id,
                duration=5
            )
            traci.person.removeStage(
                customer_id,
                0
            )
            # Take into account the limitation of traci in defining the destination position of the customer
            # refinement of the route destination position accordingly
            # update driver_info with the new arrival position
            arrival_dst_pos = traci.person.getStage(customer_id).arrivalPos
            route.set_destination_position(arrival_dst_pos)
            driver_info = driver.get_info()
            print(route.get_destination_position())
            try:
                self.__set_driver_route(
                    driver_id,
                    route,
                    stop_pos=arrival_dst_pos
                )
            except:
                raise Exception(f"Simulator.__start_sumo_route - impossible to start route for {driver_id}")
        elif driver_info[DriverIdentifiers.DRIVER_STATE.value] in [DriverState.ON_ROAD, DriverState.IDLE, DriverState.MOVING]:
            try:
                self.__set_driver_route(
                    driver_id,
                    route
                )
            except:
                raise Exception(f"Simulator.__start_sumo_route - impossible to start route for {driver_id}")
        else:
            raise Exception(f"Simulator.__start_sumo_route - unexpected driver state {driver_info[DriverIdentifiers.DRIVER_STATE.value]}")

    def __update_drivers(
            self,
            timestamp: float
    ):
        def __start_new_random_route(driver_info):
            driver_id = driver_info[DriverIdentifiers.DRIVER_ID.value]
            driver_edge_id = traci.vehicle.getRoute(driver_id)[traci.vehicle.getRouteIndex(driver_id)]
            driver_pos = traci.vehicle.getLanePosition(driver_id)
            driver_taz_id = self.__net.get_taz_id_from_edge_id(driver_edge_id, NetType.BOUNDARY_NET)
            try:
                random_route = self.__generate_driver_random_route(
                    timestamp,
                    driver_id,
                    driver_taz_id
                )
            except:
                raise Exception(f"Simulator_new.__update_drivers.__start_new_random_route - impossible to start new sumo route for {driver_id}.")
            return (random_route, driver_info)

        def __remove_driver_responding(
                timestamp: float,
                driver_info: Type[DriverInfo],
                reason: Type[DriverRemotionIdentifier]
        ):
            driver_id = driver_info[DriverIdentifiers.DRIVER_ID.value]
            if driver_info[DriverIdentifiers.DRIVER_STATE.value] in [DriverState.RESPONDING]:
                ride_info = self.__provider.find_ride_by_agent_id(
                    driver_info,
                    HumanType.DRIVER
                )
                ride_info = self.__provider.ride_request_rejected(
                    timestamp,
                    ride_info[RideIdentifier.RIDE_ID.value],
                    driver_id
                )
                ride_info = self.__provider.set_ride_request_state(
                    ride_info[RideIdentifier.RIDE_ID.value],
                    RideRequestState.REJECTED
                )
            self.__remove_driver(
                timestamp,
                driver_id,
                reason
            )

        active_drivers = [
            *self.__drivers_by_state[DriverState.MOVING],
            *self.__drivers_by_state[DriverState.IDLE],
            *self.__drivers_by_state[DriverState.RESPONDING],
            *self.__drivers_by_state[DriverState.PICKUP],
            *self.__drivers_by_state[DriverState.ON_ROAD]
        ]
        for driver_id in active_drivers:
            driver = self.__drivers[driver_id]
            driver_info = driver.get_info()
            driver_state = driver_info[DriverIdentifiers.DRIVER_STATE.value]
            driver_edge_id = traci.vehicle.getRoute(driver_id)[traci.vehicle.getRouteIndex(driver_id)]
            driver_taz_id = self.__net.get_taz_id_from_edge_id(driver_edge_id, NetType.BOUNDARY_NET)
            driver_taz_info = self.__net.get_taz_info(driver_taz_id)
            driver.update_current_edge(driver_edge_id)
            if driver_state == DriverState.MOVING:
                assert not driver_info[DriverIdentifiers.ROUTE.value] == None, "Simulator.updateDrivers - unexpected moving driver without route"
                if self.__net.is_arrived(driver_info):
                    try:
                        random_route, driver_info = __start_new_random_route(driver_info)
                        if random_route is not None:
                            driver_info = driver.update_end_moving(random_route)
                            self.__drivers_by_state[DriverState.MOVING.value].remove(
                                driver_info[DriverIdentifiers.DRIVER_ID.value])
                            self.__drivers_by_state[DriverState.IDLE.value].append(
                                driver_info[DriverIdentifiers.DRIVER_ID.value])
                        else:
                            self.__remove_driver(
                                timestamp,
                                driver_id,
                                DriverRemotionIdentifier.ROUTE_NOT_FOUND
                            )
                    except:  ### generate new driver
                        self.__remove_driver(
                            timestamp,
                            driver_id,
                            DriverRemotionIdentifier.SET_ROUTE_FAILED
                        )
                        return
            elif driver_state in [DriverState.IDLE, DriverState.RESPONDING]:
                surge_multiplier = driver_taz_info[ProviderIdentifier.SURGE_MULTIPLIERS.value][0]
                last_ride_timestamp = driver_info[DriverIdentifiers.LAST_RIDE_TIMESTAMP.value]
                idle_time_over = (timestamp - last_ride_timestamp) > self.__simulator_setup[ConfigEnum.TIMER_REMOVE_IDLE_DRIVER.value]
                if idle_time_over and driver_state == DriverState.IDLE:
                    # print(f"Driver {driver_id} stop to work [1]")
                    self.__remove_driver(
                        timestamp,
                        driver_id,
                        DriverRemotionIdentifier.STOP_WORK
                    )
                    return
                elif surge_multiplier <= 1 and driver_state == DriverState.IDLE:
                    stop_distribution = self.__driver_setup[ConfigEnum.STOP_WORK_DISTRIBUTION.value]
                    stop_probability = (timestamp - last_ride_timestamp) * self.__get_human_distribution(
                        stop_distribution, driver_info[HumanEnum.PERSONALITY.value])
                    if utils.random_choice(stop_probability):
                        # print(f"Driver {driver_id} stop to work with probability {round(stop_probability, 4)} [2]")
                        self.__remove_driver(
                            timestamp,
                            driver_id,
                            DriverRemotionIdentifier.UNPROFITABLE_SURGE_MULTIPLIER
                        )
                        return
                if self.__net.is_arrived(driver_info):
                    try:
                        random_route, driver_info = __start_new_random_route(driver_info)
                        if random_route is not None:
                            driver.set_route(random_route)
                        else:
                            if driver_state == DriverState.RESPONDING:
                                __remove_driver_responding(
                                    timestamp,
                                    driver_info,
                                    DriverRemotionIdentifier.ROUTE_NOT_FOUND
                                )
                                self.__statistics.global_indicators.sim_failure(
                                    timestamp,
                                    driver_taz_id
                                )
                            else:
                                self.__remove_driver(
                                    timestamp,
                                    driver_id,
                                    DriverRemotionIdentifier.ROUTE_NOT_FOUND
                                )
                            return
                    except:  ### generate new driver
                        if driver_state == DriverState.RESPONDING:
                            __remove_driver_responding(
                                timestamp,
                                driver_info,
                                DriverRemotionIdentifier.SET_ROUTE_FAILED
                            )
                            self.__statistics.global_indicators.sim_failure_rejection(
                                timestamp,
                                driver_taz_id
                            )
                        else:
                            self.__remove_driver(
                                timestamp,
                                driver_id,
                                DriverRemotionIdentifier.SET_ROUTE_FAILED
                            )
                        return


    def __update_driver_movements(
            self,
            timestamp: float
    ):
        active_drivers = self.__get_drivers_by_states([DriverState.IDLE])
        if len(active_drivers) > 0:
            for taz_id in self.__net.get_all_taz_ids(NetType.BOUNDARY_NET):
                for other_taz_id in self.__net.get_all_taz_ids(NetType.BOUNDARY_NET):
                    taz_info = self.__net.get_taz_info(taz_id, NetType.BOUNDARY_NET)
                    move_probability = 0
                    if not taz_id == other_taz_id:
                        other_area_info = self.__net.get_taz_info(other_taz_id)
                        for min_diff, max_diff, probability in self.__driver_setup[ConfigEnum.MOVE_DISTRIBUTION][
                            ConfigEnum.MOVE_DIFF_PROBABILITIES]:
                            surge_multiplier_area = taz_info[ProviderIdentifier.SURGE_MULTIPLIERS][0]
                            surge_multiplier_other_area = other_area_info[ProviderIdentifier.SURGE_MULTIPLIERS][0]
                            diff_surge_multiplier = surge_multiplier_area - surge_multiplier_other_area
                            if min_diff < diff_surge_multiplier < max_diff:
                                move_probability = probability
                                break
                        for driver_id in self.__get_drivers_in_taz(
                                other_taz_id):  ### check if nested parallellization works
                            driver_info = self.__drivers[driver_id].get_info()
                            if driver_info[DriverIdentifiers.DRIVER_STATE.value] == DriverState.IDLE:
                                if utils.random_choice(move_probability):
                                    self.__move_driver_to_taz(timestamp, driver_id, taz_id)


    def __update_rides_state(self, timestamp):
        def __update_pickup_ride(ride_info: Type[RideInfo]):
            ride_id = ride_info[RideIdentifier.RIDE_ID.value]
            assert not ride_info[RideIdentifier.DRIVER_ID.value] == None, "Simulator.__update_rides_state - unexpected id driver undefined [1]"
            driver = self.__drivers[ride_info[RideIdentifier.DRIVER_ID.value]]
            driver_info = driver.get_info()
            driver_id = driver_info[DriverIdentifiers.DRIVER_ID.value]
            if self.__net.is_arrived(driver_info):
                customer = self.__customers[ride_info[RideIdentifier.CUSTOMER_ID.value]]
                customer_info = customer.get_info()
                customer_id = customer_info[CustomerIdentifier.CUSTOMER_ID.value]
                driver_current_edge_id = traci.vehicle.getRoute(driver_id)[traci.vehicle.getRouteIndex(driver_id)]
                driver_current_pos = traci.vehicle.getLanePosition(driver_id)
                dst_route = self.__net.generate_sim_route_from_src_dst_edge_ids(
                    timestamp,
                    driver_current_edge_id,
                    ride_info[RideIdentifier.DST_EDGE_ID.value],
                    driver_current_pos,
                    ride_info[RideIdentifier.DST_POS.value]
                )
                if dst_route is not None:
                    try:
                        self.__start_sumo_route(
                            timestamp,
                            driver_id,
                            dst_route,
                            customer_id
                        )
                    except:
                        self.__safe_remotion(
                            timestamp,
                            driver_id,
                            customer_id,
                            ride_id,
                            DriverRemotionIdentifier.SET_ROUTE_FAILED
                        )
                        return
                    customer_info = customer.update_on_road()
                    driver_info = driver.update_on_road(dst_route)

                    surge_multiplier = ride_info[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_SURGE_MULTIPLIER.value]
                    expected_ride_travel_time = dst_route.get_expected_travel_time()
                    expected_ride_length = dst_route.get_expected_length()
                    expected_price = self.__provider.compute_price(
                        expected_ride_travel_time,
                        expected_ride_length,
                        surge_multiplier
                    )

                    self.__drivers_by_state[DriverState.PICKUP.value].remove(driver_id)
                    self.__drivers_by_state[DriverState.ON_ROAD.value].append(driver_id)
                    self.__customers_by_state[CustomerState.PICKUP.value].remove(customer_id)
                    self.__customers_by_state[CustomerState.ON_ROAD.value].append(customer_id)
                    assert (not ride_info[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_TIMESTAMP_PICKUP.value] == None), "Simulator.__update_rides_state - statistic [timestampPickup] not found or wrong type"
                    meeting_travel_time = timestamp - ride_info[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_TIMESTAMP_PICKUP.value]
                    assert not ride_info[RideIdentifier.ROUTES.value][RouteIdentifier.MEETING_ROUTE.value] == None, "Simulator.__update_rides_state - meeting route not found on pickup."
                    # this should be change according to an algorithm that compute the actual distance covered
                    meeting_route_info = self.__provider.get_ride_meeting_route_info(ride_id)
                    meeting_length = meeting_route_info[RouteIdentifier.EXPECTED_LENGTH.value]
                    stats = {
                        RideIdentifier.STAT_TIMESTAMP_ON_ROAD.value: timestamp,
                        RideIdentifier.STAT_MEETING_TRAVEL_TIME: meeting_travel_time,
                        RideIdentifier.STAT_MEETING_LENGTH: meeting_length,
                        RideIdentifier.STAT_EXPECTED_PRICE.value: expected_price,
                        RideIdentifier.STAT_EXPECTED_RIDE_TRAVEL_TIME.value: expected_ride_travel_time,
                        RideIdentifier.STAT_EXPECTED_RIDE_LENGTH.value: expected_ride_length,
                    }
                    ride_info = self.__provider.update_ride_on_road(ride_id, dst_route, stats)
                else:
                    print(f"Simulator.__update_rides_state - Impossible to generate a refined route from {driver_current_edge_id} to {ride_info[RideIdentifier.DST_EDGE_ID.value]}.")
                    self.__safe_remotion(
                        timestamp,
                        driver_id,
                        customer_id,
                        ride_id,
                        DriverRemotionIdentifier.ROUTE_NOT_FOUND
                    )

        def __update_on_road_ride(ride_info: Type[RideInfo]):
            driver_id = ride_info[RideIdentifier.DRIVER_ID.value]
            assert not driver_id == None, "Simulator.__update_rides_state - unexpected id driver distance undefined [2]"
            driver = self.__drivers[driver_id]
            driver_info = driver.get_info()
            if self.__net.is_arrived(driver_info):
                people_in_vehicle = traci.vehicle.getPersonNumber(driver_id)
                if people_in_vehicle == 0:
                    print(f"Route completed for driver {driver_info['id']} [4]")
                    customer_id = ride_info[RideIdentifier.CUSTOMER_ID.value]
                    customer = self.__customers[customer_id]
                    customer_info = customer.update_end()
                    self.__customers_by_state[CustomerState.ON_ROAD.value].remove(customer_id)
                    self.__customers_by_state[CustomerState.INACTIVE.value].append(customer_id)
                    self.__sim_customers_ids.remove(customer_id)
                    assert (not ride_info[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_TIMESTAMP_ON_ROAD.value] == None) and type(ride_info[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_TIMESTAMP_ON_ROAD.value]), "Simulator.__update_rides_state - statistic [timestampOnRoad] not found or wrong type"
                    dst_travel_time = timestamp - ride_info[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_TIMESTAMP_ON_ROAD.value]
                    assert not ride_info[RideIdentifier.ROUTES.value][RouteIdentifier.DESTINATION_ROUTE.value] == None, "Simulator.__update_rides_state - destination route not found on road."
                    # this should be change according to an algorithm that compute the actual distance covered
                    dst_length = ride_info[RideIdentifier.ROUTES.value][RouteIdentifier.DESTINATION_ROUTE.value][RouteIdentifier.EXPECTED_LENGTH.value]
                    assert not ride_info[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_SURGE_MULTIPLIER.value] == None, "Simulator.__update_rides_state - surge multiplier undefined."
                    surge_multiplier = ride_info[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_SURGE_MULTIPLIER.value]
                    price = self.__provider.compute_price(
                        dst_travel_time,
                        dst_length,
                        surge_multiplier
                    )
                    stats = {
                        RideIdentifier.STAT_TIMESTAMP_END.value: timestamp,
                        RideIdentifier.STAT_RIDE_LENGTH.value: dst_length,
                        RideIdentifier.STAT_RIDE_TRAVEL_TIME.value: dst_travel_time,
                        RideIdentifier.STAT_PRICE.value: price
                    }
                    ride_info = self.__provider.update_ride_end(ride_info[RideIdentifier.RIDE_ID.value], stats)
                    self.__statistics.specific_indicators.add_ride_stats(
                        timestamp,
                        ride_info
                    )
                    self.__statistics.drivers_stats.ride_completed(
                        driver_id,
                        ride_info[RideIdentifier.RIDE_ID.value]
                    )
                    # print(f"Simulator.__update_rides_state | Driver {driver_info['id']} - generate random route")
                    driver_edge_id = traci.vehicle.getRoute(driver_id)[traci.vehicle.getRouteIndex(driver_id)]
                    driver_pos = traci.vehicle.getLanePosition(driver_id)
                    driver_taz_id = self.__net.get_taz_id_from_edge_id(driver_edge_id, NetType.BOUNDARY_NET)
                    try:
                        random_route = self.__generate_driver_random_route(
                            timestamp,
                            driver_id,
                            driver_taz_id
                        )
                        if random_route is not None:
                            self.__drivers_by_state[DriverState.ON_ROAD.value].remove(driver_id)
                            self.__drivers_by_state[DriverState.IDLE.value].append(driver_id)
                            driver_info = driver.update_end(timestamp, random_route)
                        else:
                            # print(f"Simulator.__update_rides_state | {driver_id} not found in calling net.is_arrived_by_sumo_edge method.")
                            # self.__generate_driver(
                            #    timestamp,
                            #    driver_taz_id,
                            #    last_ride_timestamp = driver_info[DriverIdentifiers.LAST_RIDE_TIMESTAMP.value],
                            #    rides_completed = driver_info[DriverIdentifiers.RIDES_COMPLETED.value]
                            # )
                            self.__remove_driver(
                                timestamp,
                                driver_id,
                                DriverRemotionIdentifier.ROUTE_NOT_FOUND
                            )
                    except:
                        self.__remove_driver(
                            timestamp,
                            driver_id,
                            DriverRemotionIdentifier.SET_ROUTE_FAILED
                        )
                        return
        pickup_rides = self.__provider.get_rides_info_by_state(RideState.PICKUP.value)
        on_road_rides = self.__provider.get_rides_info_by_state(RideState.ON_ROAD.value)

        for ride_info in pickup_rides:
            __update_pickup_ride(ride_info)
        for ride_info in on_road_rides:
            __update_on_road_ride(ride_info)

    def __update_surge_multiplier_not_served(
            self,
            timestamp: float,
            taz_id: str
    ):
        taz_info = self.__net.get_taz_info(taz_id)
        surge_multiplier = taz_info[ProviderIdentifier.SURGE_MULTIPLIERS.value][0]
        new_surge_multiplier = max(0.7, min(surge_multiplier + 0.05, 3.5))
        self.__net.update_taz_surge_multiplier(
            taz_id,
            new_surge_multiplier,
            NetType.BOUNDARY_NET
        )

    def run(self):
        step = 0
        stop = False
        start_simulation = time.perf_counter()
        while not stop:
            simulation_performances = {}
            start_iteration = time.perf_counter()
            timestamp = traci.simulation.getTime()
            print(f"timestamp: {timestamp}")
            traci.simulationStep()
            try:
                customers_to_generate = self.__generation_dict[str(int(timestamp))][HumanEnum.CUSTOMERS.value]
                drivers_to_generate = self.__generation_dict[str(int(timestamp))][HumanEnum.DRIVERS.value]
                start = time.perf_counter()
                for customer_gen_info in customers_to_generate:
                    self.__generate_sim_customer(
                        timestamp,
                        customer_gen_info[CustomerIdentifier.CUSTOMER_ID.value],
                        customer_gen_info[CustomerIdentifier.PERSONALITY.value],
                        customer_gen_info[CustomerIdentifier.SRC_EDGE_ID.value],
                        customer_gen_info[CustomerIdentifier.DST_EDGE_ID.value],
                        customer_gen_info[CustomerIdentifier.SRC_POS.value],
                        customer_gen_info[CustomerIdentifier.DST_POS.value]
                    )
                finish = time.perf_counter()
                print(f"Customer generation in {round(finish - start, 4)} second(s).")
                #self.check_route_consistency()
                simulation_performances["customer_generation"] = round(finish - start, 4)
                start = time.perf_counter()
                for driver_gen_info in drivers_to_generate:
                    self.__generate_sim_driver(
                        timestamp,
                        driver_gen_info[DriverIdentifiers.DRIVER_ID.value],
                        driver_gen_info[DriverIdentifiers.PERSONALITY.value],
                        driver_gen_info[DriverIdentifiers.SRC_POS.value],
                        driver_gen_info[DriverIdentifiers.DST_POS.value]
                    )
                finish = time.perf_counter()
                print(f"Driver generation in {round(finish - start, 4)} second(s).")
                #self.check_route_consistency()
                simulation_performances["driver_generation"] = round(finish - start, 4)
                start = time.perf_counter()
                self.__check_drivers_list(timestamp)
                finish = time.perf_counter()
                print(f"Checked drivers list in {round(finish - start, 4)} second(s).")
                #self.check_route_consistency()
                simulation_performances["check_driver_list"] = round(finish - start, 4)
                self.__check_customers_list(timestamp)
                finish = time.perf_counter()
                print(f"Checked customers list in {round(finish - start, 4)} second(s).")
                #self.check_route_consistency()
                simulation_performances["check_customer_list"] = round(finish - start, 4)
                if utils.random_choice(0.8):
                    start = time.perf_counter()
                    self.__generate_customer_requests(timestamp)
                    finish = time.perf_counter()
                    print(f"Generated customer requests in {round(finish - start, 4)} second(s).")
                    #self.check_route_consistency()
                    simulation_performances["customer_requests"] = round(finish - start, 4)
                else:
                    simulation_performances["customer_requests"] = 0.0
                    self.check_route_exist()
                start = time.perf_counter()
                self.__process_rides(timestamp)
                finish = time.perf_counter()
                print(f"Processed rides in {round(finish - start, 4)} second(s).")
                #self.check_route_consistency()
                simulation_performances["processed_rides"] = round(finish - start, 4)
                start = time.perf_counter()
                self.__manage_pending_request(timestamp)
                finish = time.perf_counter()
                print(f"Managed pending requests in {round(finish - start, 4)} second(s).")
                #self.check_route_consistency()
                simulation_performances["managed_pending_requests"] = round(finish - start, 4)
                start = time.perf_counter()
                self.__update_drivers(timestamp)
                finish = time.perf_counter()
                print(f"Updated drivers in {round(finish - start, 4)} second(s).")
                #self.check_route_consistency()
                simulation_performances["updated_drivers"] = round(finish - start, 4)
                start = time.perf_counter()
                self.__update_rides_state(timestamp)
                finish = time.perf_counter()
                print(f"Updated rides state in {round(finish - start, 4)} second(s).")
                #self.check_route_consistency()
                simulation_performances["updated_rides_state"] = round(finish - start, 4)
                if timestamp > 0 and (timestamp % self.__simulator_setup[ConfigEnum.CHECKPOINTS.value][ConfigEnum.TIME_MOVE_DRIVER.value]) == 0.0:
                    start = time.perf_counter()
                    self.__update_driver_movements(timestamp)
                    finish = time.perf_counter()
                    print(f"Updated drivers movements in {round(finish - start, 4)} second(s).")
                    #self.check_route_consistency()
                    simulation_performances["updated_drivers_movements"] = round(finish - start, 4)
                else:
                    simulation_performances["updated_drivers_movements"] = 0.0
                scenario_events = self.__scenario.check_events(timestamp)
                for event_type, params in scenario_events:
                    self.__perform_scenario_event(timestamp, event_type, params)
                start = time.perf_counter()
                self.__update_tazs(timestamp)
                finish = time.perf_counter()
                simulation_performances["updated_tazs"] = round(finish - start, 4)
                print(f"Updated tazs statistics in {round(finish - start, 4)} second(s).")
                if timestamp > 0 and timestamp % 1000.0 == 0:
                    self.export_statistics()
                if timestamp > 0 and timestamp % self.__simulator_setup[ConfigEnum.CHECKPOINTS.value][ConfigEnum.SIMULATION_DURATION.value] == 0:
                    print("STOP")
                    stop = True
                    self.export_statistics()
            except Exception as e:
                print(self.__drivers_by_state)
                print(traci.vehicle.getIDList())
                print(self.__customers_by_state)
                print(e)
                self.export_statistics()
                raise Exception("A Fatal error occurred in Simulator.")
            finish_iteration = time.perf_counter()
            print(f"Completed iteration in {round(finish_iteration-start_iteration, 4)} seconds.")
            simulation_performances["completed_iteration"] = round(finish_iteration - start_iteration, 4)
            self.__statistics.simulator_performances.save_simulator_performances(
                timestamp,
                simulation_performances
            )
            finish_simulation = time.perf_counter()
            print(f"Simulation ended in {round(finish_simulation - start_simulation, 4)} seconds.")
        traci.close()
        sys.stdout.flush()

    def export_statistics(self):
        self.__statistics.global_indicators.export_global_indicators()
        self.__statistics.specific_indicators.export_specific_indicators()
        self.__statistics.drivers_stats.export_drivers_stats_info()
        self.__statistics.simulator_performances.export_simulator_performances()
        self.__statistics.ride_stats.save_rides_stats(
            self.__provider.get_rides_info_by_state()
        )
        self.__statistics.ride_stats.export_rides_stats_info()

    def check_route_exist(self):
        for driver_id, driver in self.__drivers.items():
            driver_info = driver.get_info()
            if driver_id in traci.vehicle.getIDList():
                if driver_info[DriverIdentifiers.ROUTE.value] is None:
                    print(driver_info)
                assert driver_info[DriverIdentifiers.ROUTE.value] is not None, "Simulator.__get_drivers_info_moving_in_taz - driver route not found"

    def check_route_consistency(self):
        for driver_id, driver in self.__drivers.items():
            if driver_id in traci.vehicle.getIDList():
                driver_info = driver.get_info()
                driver_id = driver_info[DriverIdentifiers.DRIVER_ID.value]
                driver_state = driver_info[DriverIdentifiers.DRIVER_STATE.value]
                driver_route = driver_info[DriverIdentifiers.ROUTE.value]
                current_route_idx = traci.vehicle.getRouteIndex(driver_id)  ###
                route_edge_id_list = driver_info[DriverIdentifiers.ROUTE.value][RouteIdentifier.EDGE_ID_LIST.value]
                traci_driver_route = traci.vehicle.getRoute(driver_id)
                if not len(route_edge_id_list) == len(traci_driver_route):
                    print(current_route_idx)
                    print(len(route_edge_id_list))
                    print(route_edge_id_list)
                    print(traci.vehicle.getRoute(driver_id))
                    print(driver_info)
                    raise Exception("out of index")
                for idx, edge_id in enumerate(traci_driver_route):
                    if not edge_id == traci_driver_route[idx]:
                        print(current_route_idx)
                        print(len(route_edge_id_list))
                        print(route_edge_id_list)
                        print(traci.vehicle.getRoute(driver_id))
                        print(driver_info)
                        raise Exception("out of index")

    def print_customers(self):
        customers_info = []
        for customer in self.__customers.values():
            customers_info.append(customer.get_info())
        print(customers_info)

    def print_drivers(self):
        for driver in self.__drivers.values():
            driver_info = driver.get_info()
            driver_id = driver_info[DriverIdentifiers.DRIVER_ID.value]
            print(f"Driver info: {driver_info}")
            traci_drivers_list = traci.vehicle.getIDList()
            driver_route_idx = traci.vehicle.getRouteIndex(driver_id)
            if driver_info[driver_id] in traci_drivers_list:
                print(f"Driver route index: {driver_route_idx}")

    def print_person(self):
        traci_customers_list = traci.person.getIDList()
        for customer_id in traci_customers_list:
            customer_edges = traci.person.getEdges(customer_id)
            print(f"Person current edge: {customer_edges}")

    def print_drivers_by_state(self):
        print(self.__drivers_by_state)

    def print_customers_by_state(self):
        print(self.__customers_by_state)

    def get_customers(self):
        return self.__customers

    def get_drivers(self):
        return self.__drivers