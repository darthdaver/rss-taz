from enum import Enum


class Route(str, Enum):
    MEETING_ROUTE = "meeting_route"
    DESTINATION_ROUTE = "destination_route"
    ROUTE_ID = "id"
    ROUTE_TYPE = "route_type"
    ROUTE = "route"
    EXPECTED_TRAVEL_TIME = "expected_travel_time"
    EXPECTED_LENGTH = "expected_length"
    STD_TRAVEL_TIME = "std_travel_time"
    SRC_POS = "src_pos"
    DST_POS = "dst_pos"
    EDGE_ID_LIST = "edge_id_list"
    COST = "cost"
    DST_EDGE_ID = "dst_edge_id"
    SRC_EDGE_ID = "src_edge_id"