import math
from typing import Type
from src.model.Route import Route
from src.enum.identifiers.Route import Route as RouteIdentifiers
from src.enum.identifiers.Ride import Ride as RideIdentifiers
from src.enum.state.RideState import RideState
from src.enum.state.RideRequestState import RideRequestState
from src.enum.identifiers.Request import Request as RequestIdentifiers
from src.types.Ride import Candidate, RideInfo, RideStats
from src.types.Route import RouteInfo


class Ride:
    def __init__(
            self,
            id: str,
            customer_id: str,
            src_edge_id: str,
            dst_edge_id: str,
            src_pos: float = 0.0,
            dst_pos: float = 0.0,
            stats={}
    ):
        self.__id = id
        self.__customer_id = customer_id
        self.__driver_id = None
        self.__src_edge_id = src_edge_id
        self.__dst_edge_id = dst_edge_id
        self.__src_pos = src_pos
        self.__dst_pos = dst_pos
        self.__state = RideState.REQUESTED
        self.__request = {
            RequestIdentifiers.REQUEST_STATE.value: RideRequestState.UNPROCESSED,
            RequestIdentifiers.DRIVERS_CANDIDATE.value: [],
            RequestIdentifiers.REJECTIONS.value: [],
            RequestIdentifiers.CURRENT_CANDIDATE.value: None
        }
        self.__routes = {
            RouteIdentifiers.MEETING_ROUTE.value : None,
            RouteIdentifiers.DESTINATION_ROUTE.value: None
        }
        self.__stats = stats

    def add_driver_candidate(self, driver_candidate: Candidate) -> RideInfo:
        self.__request[RequestIdentifiers.DRIVERS_CANDIDATE.value].append(driver_candidate)
        return self.get_info()

    def decrement_count_down_request(self):
        assert self.__request[RequestIdentifiers.CURRENT_CANDIDATE.value] is not None, "Ride.decrement_count_down_request - candidate is undefined."
        if self.__request[RequestIdentifiers.CURRENT_CANDIDATE.value]:
            self.__request[RequestIdentifiers.CURRENT_CANDIDATE.value][RequestIdentifiers.RESPONSE_COUNT_DOWN.value] -= 1

    def get_destination_route_info(self) -> RouteInfo:
        destination_route = self.__routes[RouteIdentifiers.DESTINATION_ROUTE.value].get_info()
        return destination_route

    def get_id(self) -> int:
        return self.__id

    def get_info(self) -> RideInfo:
        return {
            RideIdentifiers.RIDE_ID.value: self.__id,
            RideIdentifiers.CUSTOMER_ID.value: self.__customer_id,
            RideIdentifiers.DRIVER_ID.value: self.__driver_id,
            RideIdentifiers.SRC_EDGE_ID.value: self.__src_edge_id,
            RideIdentifiers.DST_EDGE_ID.value: self.__dst_edge_id,
            RideIdentifiers.SRC_POS.value: self.__src_pos,
            RideIdentifiers.DST_POS.value: self.__dst_pos,
            RideIdentifiers.REQUEST.value: {
                **self.__request
            },
            RideIdentifiers.ROUTES.value: self.routes_to_dict(),
            RideIdentifiers.RIDE_STATE.value: self.__state,
            RideIdentifiers.RIDE_STATS.value: {
                **self.__stats
            }
        }

    def get_meeting_route_info(self) -> Type[RouteInfo]:
        meeting_route_info = self.__routes[RouteIdentifiers.MEETING_ROUTE.value].get_info()
        return meeting_route_info

    def refine_route(self, route_type: RouteIdentifiers, route: Type[Route]) -> RideInfo:
        self.__routes[route_type] = route
        return self.get_info()

    def request_canceled(self) -> RideInfo:
        self.__request[RideIdentifiers.RIDE_STATE.value] = RideRequestState.CANCELED
        self.__state = RideState.CANCELED
        return self.get_info()

    def request_rejected(self, driver_id: str, idle_driver: bool = True) -> RideInfo:
        if idle_driver:
            self.__request[RequestIdentifiers.REJECTIONS.value].append(driver_id)
        self.__request[RequestIdentifiers.REQUEST_STATE] = RideRequestState.REJECTED
        return self.get_info()

    def routes_to_dict(self) -> RouteInfo:
        return {
            RouteIdentifiers.MEETING_ROUTE.value: None if self.__routes[RouteIdentifiers.MEETING_ROUTE.value] is None else self.__routes[RouteIdentifiers.MEETING_ROUTE.value].to_dict(),
            RouteIdentifiers.DESTINATION_ROUTE.value: None if self.__routes[RouteIdentifiers.DESTINATION_ROUTE.value] is None else self.__routes[RouteIdentifiers.DESTINATION_ROUTE.value].to_dict()
        }

    def set_candidate(self, candidate: Candidate) -> RideInfo:
        self.__request[RequestIdentifiers.CURRENT_CANDIDATE.value] = candidate
        assert candidate in self.__request[RequestIdentifiers.DRIVERS_CANDIDATE.value], "Ride.set_candidate - candidate is not included in drivers candidates"
        self.__request[RequestIdentifiers.DRIVERS_CANDIDATE.value] = list(filter(lambda d: not d[RequestIdentifiers.CANDIDATE_ID.value] == candidate[RequestIdentifiers.CANDIDATE_ID.value], self.__request[RequestIdentifiers.DRIVERS_CANDIDATE.value]))
        return self.get_info()

    def set_driver(self, driver_id: str) -> RideInfo:
        self.__driver_id = driver_id
        return self.get_info()

    def set_request_state(self, state: Type[RideRequestState]) -> RideInfo:
        self.__request[RequestIdentifiers.REQUEST_STATE.value] = state
        return self.get_info()

    def set_state(self, state: Type[RideState]) -> RideInfo:
        self.__state = state
        return self.get_info()

    def sort_candidates(self) -> RideInfo:
        self.__request[RequestIdentifiers.DRIVERS_CANDIDATE.value] = sorted(self.__request[RequestIdentifiers.DRIVERS_CANDIDATE.value], key=lambda d: d[RequestIdentifiers.COST.value])
        return self.get_info()

    def update_request_minimal(self, candidates_count: int):
        self.__request[RequestIdentifiers.CANDIDATES_COUNT.value] = candidates_count

    def update_cancel(self):
        pass

    def update_end(self, stats: Type[RideStats]) -> RideInfo:
        self.__state = RideState.END
        self.__set_stats(stats)
        return self.get_info()

    def update_on_road(
            self,
            dst_route: Type[Route],
            stats: Type[RideStats]
    ) -> RideInfo:
        self.__state = RideState.ON_ROAD
        self.__set_route(RouteIdentifiers.DESTINATION_ROUTE, dst_route)
        self.__set_stats(stats)
        return self.get_info()

    def update_pending(self, timestamp: float) -> RideInfo:
        self.__state = RideState.PENDING
        self.__stats[RideIdentifiers.STAT_TIMESTAMP_REQUEST.value] = timestamp
        return self.get_info()

    def update_accepted(self, driver_id: str, meeting_route: Type[Route], stats: Type[RideStats])-> RideInfo:
        self.__driver_id = driver_id
        self.__set_route(RouteIdentifiers.MEETING_ROUTE, meeting_route)
        self.__set_stats(stats)
        self.__request[RequestIdentifiers.REQUEST_STATE.value] = RideRequestState.ACCEPTED
        return self.get_info()

    def update_pickup(self) -> RideInfo:
        self.__state = RideState.PICKUP
        return self.get_info()

    def __set_route(self, route_type: Type[RouteIdentifiers], route: Type[Route]) -> RideInfo:
        if route_type == RouteIdentifiers.MEETING_ROUTE:
            self.__routes[RouteIdentifiers.MEETING_ROUTE.value] = route
        if route_type == RouteIdentifiers.DESTINATION_ROUTE:
            self.__routes[RouteIdentifiers.DESTINATION_ROUTE.value] = route
        return self.get_info()

    def __set_stats(self, stats: Type[RideStats]) -> RideInfo:
        self.__stats = {
            **self.__stats,
            **stats
        }
        return self.get_info()

