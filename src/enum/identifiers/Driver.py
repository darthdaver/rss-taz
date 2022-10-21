from enum import Enum

class Driver(str, Enum):
    PERSONALITY = "personality"
    DRIVER_STATE = "state"
    DRIVER_ID = "id"
    ROUTE = "route"
    LAST_RIDE_TIMESTAMP = "last_ride_timestamp"
    RIDES_COMPLETED = "rides_completed"
    TIMESTAMP = "timestamp"
    SRC_POS = "src_pos"
    DST_POS = "dst_pos"
    DRIVER_ACCEPTANCE_DISTRIBUTION = "driver_acceptance_distribution"
    EDGE_ID_LIST = "edge_id_list"
    CURRENT_EDGE_ID = "current_edge_id"