from typing import TypedDict
from src.enum.types.RouteType import RouteType


class RouteInfo(TypedDict):
    id: str
    route_type: RouteType
    edge_id_list: list[str]
    expected_length: float
    expected_travel_time: float
    std_travel_time: float
    src_pos: float
    dst_pos: float