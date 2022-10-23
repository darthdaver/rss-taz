from enum import Enum

class Api(str, Enum):
    DATA = "data"
    OK = "ok"
    KO = "ko"

    # TRACI
    COMMAND = "command"
    CUSTOMER_ID = "customer_id"
    DRIVER_ID = "driver_id"
    ROUTE_ID = "route_id"
    DST_EDGE_ID = "dst_edge_id"
    POS = "pos"
    DURATION = "duration"
    FLAGS = "flags"
    STAGE = "stage"
    DRIVING_STAGE = "driving_stage"
    WAITING_STAGE = "waiting_stage"
    STAGE_NUM = "stage_num"
    DST_POS = "dst_pos"

    # SUMO_NET
    EDGE_ID = "edge_id"
    SRC_EDGE_ID = "src_edge_id"
    VEHICLE_CLASS = "vehicle_class"
    LANE_NUM = "lane_num"
    ROUTE_STR = "route_str"
    SEPARATOR = "*"