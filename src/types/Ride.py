from typing import Type, TypedDict, Union, Optional
from src.types.Route import RouteInfo
from src.model.Route import Route
from src.enum.state.RideRequestState import RideRequestState


class Candidate(TypedDict):
    id = str
    response_count_down = int
    meeting_route = Type[Route]
    send_request_back_timer = int
    expected_distance = float
    expected_duration = float
    current_edge_id = str
    air_distance = float

class RequestInfo(TypedDict):
    state = Type[RideRequestState]
    drivers_candidate = list[Candidate]
    rejections = int
    current_candidate = str

class RideRoutes(TypedDict):
    meeting_route = Type[Route]
    destination_route = Type[Route]

class RideRoutesInfo(TypedDict):
    meeting_route = RouteInfo
    destination_route = RouteInfo

class RideStats(TypedDict):
    timestamp_request = float


class RideInfo(TypedDict):
    id = str
    customer_id = str
    driver_id = Union[str, None]
    src_edge_id = str
    dst_edge_id = str
    src_pos = float
    dst_pos = float
    request = RequestInfo
    routes = RideRoutesInfo
    stats = RideStats
