from enum import Enum

class Customer(str, Enum):
    PERSONALITY = "personality"
    TIMESTAMP = "timestamp"
    CUSTOMER_STATE = "state"
    CUSTOMER_ID = "id"
    SRC_EDGE_ID = "src_edge_id"
    SRC_POS = "src_pos"
    DST_EDGE_ID = "dst_edge_id"
    DST_POS = "dst_pos"
    ACCEPTANCE_DISTRIBUTION = "acceptance_distribution"
