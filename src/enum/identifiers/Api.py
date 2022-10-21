from enum import Enum

class Api(str, Enum):
    DATA = "data"

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

    # SUMO_NET
    EDGE_ID = "edge_id"
    SRC_EDGE_ID = "src_edge_id"