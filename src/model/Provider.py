import random
from typing import Type, Dict, Union
from src.model.Ride import Ride
from src.model.Route import Route
from src.enum.types.RouteType import RouteType
from src.types.Route import RouteInfo
from src.types.Customer import CustomerInfo
from src.types.Driver import DriverInfo
import multiprocessing_on_dill as multiprocessing
from src.enum.identifiers.Human import Human as HumanIdentifier
from src.enum.identifiers.Driver import Driver as DriverIdentifier
from src.enum.identifiers.Ride import Ride as RideIdentifier
from src.enum.identifiers.Provider import Provider as ProviderIdentifier
from src.enum.identifiers.Route import Route as RouteIdentifier
from src.enum.identifiers.Request import Request as RequestIdentifier
from src.enum.setup.FileSetup import FileSetup
from src.model.Map import Map
from src.enum.state.DriverState import DriverState
from src.enum.state.CustomerState import CustomerState
from src.enum.state.RideState import RideState
from src.enum.state.RideRequestState import RideRequestState
from src.utils import utils
from src.enum.types.HumanType import HumanType
from src.types.Config import ProviderSetup, FareSetup, RequestSetup
from src.types.Ride import Candidate, RideInfo
from src.types.Driver import DriverInfo
from sumolib.net import Net as SumoNet
import sumolib
import time
from src.enum.identifiers.Request import Request as RequestIdentifier
from joblib import wrap_non_picklable_objects
from src.task import tasks
from src.enum.identifiers.Api import Api as ApiIdentifier
from src.enum.api.Api import Api
import traci
from haversine import haversine, Unit

class Provider:
    def __init__(
            self,
            provider_setup: ProviderSetup,
            sumo_net: Type[SumoNet]
    ):
        self.__rides: Dict[str, Ride] = {}
        self.__rides_by_state: Dict[str, list[str]] = {k.value: [] for k in RideState}
        self.__fare: FareSetup = provider_setup[ProviderIdentifier.FARE.value]
        self.__request: RequestSetup = provider_setup[ProviderIdentifier.REQUEST.value]
        self.__cpu_cores = multiprocessing.cpu_count()
        self.__sumo_net = sumo_net


    def add_ride(
            self,
            ride: Type[Ride]
    ):
        self.__rides[ride.get_id()] = ride

    def add_candidate_to_ride(
            self,
            ride_id: str,
            driver_candidate: Type[Candidate]
    ) -> RideInfo:
        ride_info = self.__rides[ride_id].add_driver_candidate(driver_candidate)
        return ride_info

    def find_ride_by_agent_id(
            self,
            agent_info: Union[Type[CustomerInfo], Type[DriverInfo]],
            agent_type: Type[HumanType]
    ):
        def __search_ride(ride_id: str):
            nonlocal found_ride_info
            ride = self.__rides[ride_id]
            ride_info = ride.get_info()
            if agent_type == HumanType.DRIVER:
                if state == RideState.PENDING:
                    if ride_info[RideIdentifier.REQUEST.value][RequestIdentifier.CURRENT_CANDIDATE.value][
                        RequestIdentifier.CANDIDATE_ID.value] == agent_info[HumanIdentifier.HUMAN_ID.value]:
                        found_ride_info = ride_info
                else:
                    if ride_info[RideIdentifier.DRIVER_ID.value] == agent_info[HumanIdentifier.HUMAN_ID.value]:
                        found_ride_info = ride_info
            elif agent_type == HumanType.CUSTOMER:
                if ride_info[RideIdentifier.CUSTOMER_ID.value] == agent_info[HumanIdentifier.HUMAN_ID.value]:
                    found_ride_info = ride_info
        assert agent_type in [HumanType.DRIVER, HumanType.CUSTOMER], f"Provider.find_ride_by_agent_id - unexpected agent type {agent_type}"
        state = None
        found_ride_info = None
        if agent_info[HumanIdentifier.HUMAN_STATE.value] in [DriverState.PICKUP, CustomerState.PICKUP]:
            state = RideState.PICKUP
        elif agent_info[HumanIdentifier.HUMAN_STATE.value] in [DriverState.ON_ROAD, CustomerState.ON_ROAD]:
            state = RideState.ON_ROAD
        elif agent_info[HumanIdentifier.HUMAN_STATE.value] in [DriverState.RESPONDING, CustomerState.PENDING]:
            state = RideState.PENDING
        elif agent_info[HumanIdentifier.HUMAN_STATE.value] == CustomerState.ACTIVE:
            state = RideState.REQUESTED
        else:
            assert False, f"Provider.find_ride_by_agent_id - unexpected agent state {agent_info[HumanIdentifier.HUMAN_STATE.value]}"
        for ride_id in self.__rides_by_state[state.value]:
            if found_ride_info is None:
                __search_ride(ride_id)
            else:
                break
        return found_ride_info

    def compute_balance(
            self,
            idle_customers_count: int,
            idle_drivers_count: int,
            num_not_served: int
    ):
        if idle_customers_count > 0:
            if idle_drivers_count == 0:
                return 1 / (idle_customers_count + 1)
            else:
                return 0.7 + (idle_drivers_count / (5*idle_customers_count))
        else:
            return max(0.9 + (idle_drivers_count / 10) - 0.1 * num_not_served, 0)

    def compute_price(
            self,
            travel_time: float,
            ride_length: float,
            surge_multiplier: float
    ):
        base_fare = self.__fare[ProviderIdentifier.BASE_FARE.value]
        fee_per_minute = self.__fare[ProviderIdentifier.FEE_PER_MINUTE.value]
        fee_per_mile = self.__fare[ProviderIdentifier.FEE_PER_MILE.value]
        price = (base_fare + (fee_per_minute * travel_time) + (fee_per_mile * ride_length/1000)) * surge_multiplier
        return price

    def compute_surge_multiplier_increment(
            self,
            balance: float
    ):
        for min_balance, max_balance, value in self.__fare[ProviderIdentifier.SURGE_MULTIPLIER_DISTRIBUTION.value]:
            if min_balance <= balance < max_balance:
                return value
        assert False, f"Provider.compute_surge_multiplier_increment - sourge multiplier increment not found for balance {balance}"

    def get_ride_meeting_route_info(
            self,
            ride_id: str
    ) -> Type[RouteInfo]:
        ride = self.__rides[ride_id]
        return ride.get_meeting_route_info()

    def get_ride_destination_route_info(
            self,
            ride_id: str
    ) -> Type[RouteInfo]:
        ride = self.__rides[ride_id]
        return ride.get_destination_route_info()

    def get_pending_rides(self):
        def __filter_pending_rides(ride: Type[Ride]):
            nonlocal pending_rides_info
            ride_info = ride.get_info()
            if ride_info[RideIdentifier.RIDE_STATE.value] in [RideState.REQUESTED, RideState.PENDING]:
                pending_rides_info.append(ride_info)
        rides_array = list(self.__rides.values())
        pending_rides_info = []
        """Parallel(
                n_jobs=self.__cpu_cores,
                backend="threading"
        )(
            delayed(__filter_pending_rides)(ride_id)
            for ride_id in rides_array
        )"""

        for ride_id in rides_array:
            __filter_pending_rides(ride_id)
        return pending_rides_info

    def get_ride_info(
            self,
            ride_id: str
    ):
        ride = self.__rides[ride_id]
        return ride.get_info()

    def get_rides_info_by_state(
            self,
            state: str = "all"
    ):
        filtered_rides_info = []
        ride_list = self.__rides.keys() if state == "all" else self.__rides_by_state[state]
        for ride_id in ride_list:
            ride = self.__rides[ride_id]
            filtered_rides_info.append(ride.get_info())
        return filtered_rides_info

    def get_ride_info_by_customer_id(
            self,
            customer_id: str
    ):
        def __filter_ride_info_by_customer(ride: Type[Ride]):
            nonlocal customer_id
            nonlocal filtered_rides_info
            if ride.get_info()[RideIdentifier.CUSTOMER_ID.value] == customer_id:
                filtered_rides_info.append(ride.get_info())
        filtered_rides_info = []
        """Parallel(
                n_jobs=self.__cpu_cores,
                backend="threading"
        )(
            delayed(__filter_ride_info_by_customer)(ride)
            for ride in self.__rides.values()
        )"""
        for ride in self.__rides.values():
            __filter_ride_info_by_customer(ride)
        assert filtered_rides_info == 1, "Provider.get_ride_info_by_customer_id - unknown number of rides associated to the same customer"
        return filtered_rides_info[0]

    def get_unprocessed_requests(self):
        return [
            *self.__rides_by_state[RideState.REQUESTED.value]
        ]

    def manage_pending_request(
            self,
            ride_info: Type[RideInfo],
            drivers_info: Dict[str, Type[DriverInfo]]
    ):
        ride = self.__rides[ride_info[RideIdentifier.RIDE_ID.value]]
        if ride_info[RideIdentifier.REQUEST.value][RideIdentifier.RIDE_STATE.value] in [RideRequestState.REJECTED, RideRequestState.UNPROCESSED]:
            self.set_ride_request_state(ride_info[RideIdentifier.RIDE_ID.value], RideRequestState.SEARCHING_CANDIDATES)
            free_drivers_info = self.__free_drivers_info(drivers_info)
            free_drivers_ids = list(map(lambda d: d[DriverIdentifier.DRIVER_ID.value], free_drivers_info))
            candidate = self.__select_driver_candidate(ride_info, free_drivers_ids)
            if candidate:
                ride_info = ride.set_candidate(candidate)
                ride_info = ride.set_request_state(RideRequestState.SENT)
                return (ride_info, RideRequestState.SENT, candidate[RequestIdentifier.CANDIDATE_ID.value])
            else:
                ride_info = ride.set_request_state(RideRequestState.NONE)
                ride_info = self.__ride_not_served(ride)
                return [ride_info, RideRequestState.NONE, None]
        elif ride_info[RideIdentifier.REQUEST.value][RideIdentifier.RIDE_STATE.value] == RideRequestState.SEARCHING_CANDIDATES:
            return (ride_info, RideRequestState.SEARCHING_CANDIDATES, None)
        elif ride_info[RideIdentifier.REQUEST.value][RideIdentifier.RIDE_STATE.value] in [RideRequestState.SENT, RideRequestState.WAITING]:
            current_candidate = ride_info[RideIdentifier.REQUEST.value][RequestIdentifier.CURRENT_CANDIDATE.value]
            assert current_candidate is not None, "Provider.manage_pending_request - candidate undefined [1]"
            if current_candidate and current_candidate[RequestIdentifier.RESPONSE_COUNT_DOWN.value] == current_candidate[RequestIdentifier.SEND_REQUEST_BACK_TIMER.value]:
                return (ride_info, RideRequestState.RESPONSE, current_candidate[RequestIdentifier.CANDIDATE_ID.value])
            else:
                ride.decrement_count_down_request()
                assert current_candidate is not None, "Provider.manage_pending_request - candidate undefined [2]"
                return (ride_info, RideRequestState.WAITING, current_candidate[RequestIdentifier.CANDIDATE_ID.value])
        elif ride_info[RideIdentifier.REQUEST.value][RideIdentifier.RIDE_STATE.value] == RideRequestState.ROUTE_NOT_FOUND:
            self.remove_ride_simulation_error(ride_info[RideIdentifier.RIDE_ID.value])
            return (ride_info, RideRequestState.ROUTE_NOT_FOUND, None)
        return (ride_info, RideRequestState.NONE, None)

    def print_ride_info(
            self,
            ride_id: str
    ):
        ride = self.__rides[ride_id]
        print(ride.get_info())

    def process_customer_request(
            self,
            timestamp: float,
            ride_info: Type[RideInfo],
            meeting_edge_id: str,
            available_drivers_info
    ):
        ride = self.__rides[ride_info[RideIdentifier.RIDE_ID.value]]
        ride_info = ride.update_pending(timestamp)
        self.__nearby_drivers(
            ride_info,
            meeting_edge_id,
            available_drivers_info
        )
        assert ride_info[RideIdentifier.RIDE_ID.value] in self.__rides_by_state[RideState.REQUESTED.value], "Provider.process_customer_request - ride request not included in unprocessed request"
        self.__rides_by_state[RideState.REQUESTED.value].remove(ride_info[RideIdentifier.RIDE_ID.value])
        self.__rides_by_state[RideState.PENDING.value].append(ride_info[RideIdentifier.RIDE_ID.value])

    def receive_request(
            self,
            ride: Type[Ride]
    ):
        ride_info = ride.get_info()
        self.__rides[ride_info[RideIdentifier.RIDE_ID.value]] = ride
        self.__rides_by_state[RideState.REQUESTED.value].append(ride_info[RideIdentifier.RIDE_ID.value])

    def refine_ride_route(
            self,
            ride_id: str,
            route: Type[Route],
            route_type: Type[RouteType]
    ):
        assert route_type in ["meeting_route","destination_route"], f"Provider.refine_ride_route - unexpected route_type {route_type}"
        ride = self.__rides[ride_id]
        ride_info = ride.refine_route(route_type, route)
        return ride_info

    def remove_ride_simulation_error(
            self,
            ride_id: str
    ):
        ride = self.__rides[ride_id]
        ride_info = ride.get_info()
        self.__rides_by_state[ride_info[RideIdentifier.RIDE_STATE.value].value].remove(ride_id)
        ride.set_state(RideState.SIMULATION_ERROR)
        self.__rides_by_state[RideState.SIMULATION_ERROR.value].append(ride_id)

    def ride_request_canceled(
            self,
            ride_id: str
    ):
        assert ride_id in self.__rides_by_state[RideState.REQUESTED.value], f"Provider.ride_request_canceled - Unexpected ride state for {ride_id}."
        self.__rides_by_state[RideState.REQUESTED.value].remove(ride_id)
        self.__rides_by_state[RideState.CANCELED.value].append(ride_id)
        ride = self.__rides[ride_id]
        return ride.request_canceled()

    def ride_request_rejected(
            self,
            ride_id: str,
            driver_id: str
    ):
        ride = self.__rides[ride_id]
        ride_info = ride.get_info()
        assert ride_info[RideIdentifier.RIDE_STATE.value] == RideState.PENDING, f"Unexpected ride state {ride_info[RideIdentifier.RIDE_STATE.value]} for {ride_id}"
        return ride.request_rejected(driver_id)

    def set_ride_request_state(
            self,
            ride_id: str,
            ride_request_state: Type[RideRequestState]
    ):
        ride = self.__rides[ride_id]
        return ride.set_request_state(ride_request_state)

    def set_ride_state(
            self,
            ride_id: str,
            ride_state: Type[RideState]
    ):
        ride = self.__rides[ride_id]
        ride_info = ride.get_info()
        self.__rides_by_state[ride_info[RideIdentifier.RIDE_STATE.value].value].remove(ride_id)
        self.__rides_by_state[ride_state].append(ride_id)
        return ride.set_state(ride_state)

    def update_ride_accepted(
            self,
            ride_id: str,
            driver_id: str,
            meeting_route: Type[Route],
            destination_route: Type[Route],
            stats: Dict
    ):
        ride = self.__rides[ride_id]
        ride_info = ride.get_info()
        self.set_ride_request_state(ride_info[RideIdentifier.RIDE_ID.value], RideRequestState.ACCEPTED)
        return ride.update_accepted(driver_id, meeting_route, destination_route, stats)

    def update_ride_pickup(
            self,
            ride_id: str
    ):
        ride = self.__rides[ride_id]
        ride_info = ride.get_info()
        assert ride_info[RideIdentifier.RIDE_STATE.value] == RideState.PENDING, f"Provider.update_ride_pickup - unexpected ride state {ride_info['state']} for {ride_id}"
        self.__rides_by_state[RideState.PENDING.value].remove(ride_id)
        self.__rides_by_state[RideState.PICKUP.value].append(ride_id)
        return ride.update_pickup()

    def update_ride_on_road(
            self,
            ride_id: str,
            stats: Dict
    ):
        ride = self.__rides[ride_id]
        ride_info = ride.get_info()
        assert ride_info[RideIdentifier.RIDE_STATE.value] == RideState.PICKUP, f"Provider.update_ride_pickup - unexpected ride state {ride_info['state']} for {ride_id}"
        self.__rides_by_state[RideState.PICKUP.value].remove(ride_id)
        self.__rides_by_state[RideState.ON_ROAD.value].append(ride_id)
        return ride.update_on_road(stats)

    def update_ride_end(
            self,
            ride_id: str,
            stats: Dict
    ):
        ride = self.__rides[ride_id]
        ride_info = ride.get_info()
        assert ride_info[RideIdentifier.RIDE_STATE.value] == RideState.ON_ROAD, f"Provider.update_ride_pickup - unexpected ride state {ride_info['state']} for {ride_id}"
        self.__rides_by_state[RideState.ON_ROAD.value].remove(ride_id)
        self.__rides_by_state[RideState.END.value].append(ride_id)
        return ride.update_end(stats)

    def __free_drivers_info(
            self,
            drivers_info: Dict[str, Type[DriverInfo]]
    ):
        def __filter_free_drivers(driver_info: Type[DriverInfo]):
            nonlocal free_drivers
            traci_drivers_ids_list = traci.vehicle.getIDList()
            if driver_info[DriverIdentifier.DRIVER_ID.value] in traci_drivers_ids_list:
                free_drivers.append(driver_info)
        free_drivers = []
        """Parallel(
                n_jobs=self.__cpu_cores,
                backend="threading"
        )(
            delayed(__filter_free_drivers)(drivers_info)
            for drivers_info in drivers_info.values()
        )"""
        for drivers_info in drivers_info.values():
            __filter_free_drivers(drivers_info)
        return free_drivers

    def __get_rides_by_state(
            self,
            states: list[Type[RideState]]
    ):
        def __filter_ride_by_state(state: str, rides_ids_by_state: list[str]):
            nonlocal filtered_rides
            filtered_rides.extend(rides_ids_by_state)
        states = map(lambda s: s.value, states)
        filtered_rides = []
        """Parallel(
                n_jobs=self.__cpu_cores,
                backend="threading"
        )(
            delayed(__filter_ride_by_state)(state, rides_ids_by_state)
            for state, rides_ids_by_state in self.__rides_by_state.items()
            if state in states
        )"""
        for state, rides_ids_by_state in self.__rides_by_state.items():
            if state in states:
                __filter_ride_by_state(state, rides_ids_by_state)
        return filtered_rides

    def __nearby_drivers(
            self,
            ride_info: Type[RideInfo],
            meeting_edge_id: str,
            drivers_info: Type[DriverInfo]
    ):
        drivers_info_array = list(drivers_info.values())
        random.shuffle(drivers_info_array)
        for driver_info in drivers_info_array:
            driver_id = driver_info[DriverIdentifier.DRIVER_ID.value]
            customer_id = ride_info[RideIdentifier.CUSTOMER_ID.value]
            customer_position = traci.person.getPosition(customer_id)
            driver_position = traci.vehicle.getPosition(driver_id)
            customer_coordinates = traci.simulation.convertGeo(customer_position[0],customer_position[1])
            driver_coordinates = traci.simulation.convertGeo(driver_position[0],driver_position[1])
            distance = haversine(
                (driver_coordinates[1],driver_coordinates[0]),
                (customer_coordinates[1],customer_coordinates[0]),
                unit=Unit.METERS
            )
            if distance < self.__request[ProviderIdentifier.MAX_DRIVER_DISTANCE.value]:
                ride_info = self.add_candidate_to_ride(ride_info[RideIdentifier.RIDE_ID.value], {
                    RequestIdentifier.CANDIDATE_ID.value: driver_id,
                    RequestIdentifier.COST.value: distance,
                    RequestIdentifier.RESPONSE_COUNT_DOWN.value: 15,
                    RequestIdentifier.SEND_REQUEST_BACK_TIMER.value: utils.random_int_from_range(0, 11)
                })
        if len(ride_info[RideIdentifier.REQUEST.value][RequestIdentifier.DRIVERS_CANDIDATE.value]) == 0:
            # print(f"Provider.__nearby_drivers - {ride_info[RideIdentifier.CUSTOMER_ID.value]} has 0 candidates.")
            self.set_ride_request_state(ride_info[RideIdentifier.RIDE_ID.value], RideRequestState.ROUTE_NOT_FOUND)
        ride_info = self.__rides[ride_info[RideIdentifier.RIDE_ID.value]].sort_candidates()
    def __ride_not_served(
            self,
            ride: Type[Ride]
    ):
        ride_info = ride.get_info()
        self.__rides_by_state[ride_info[RideIdentifier.RIDE_STATE.value].value].remove(ride_info[RideIdentifier.RIDE_ID.value])
        self.__rides_by_state[RideState.NOT_SERVED.value].append(ride_info[RideIdentifier.RIDE_ID.value])
        return ride.set_state(RideState.NOT_SERVED)

    def __select_driver_candidate(self, ride_info, free_drivers_ids):
        drivers_candidates = ride_info[RideIdentifier.REQUEST.value][RequestIdentifier.DRIVERS_CANDIDATE.value]
        for candidate in drivers_candidates:
            if candidate and candidate[RequestIdentifier.CANDIDATE_ID.value] in free_drivers_ids:
                return candidate
        return None
