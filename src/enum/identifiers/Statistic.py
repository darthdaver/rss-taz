from enum import Enum

class Statistic(str, Enum):
    ID = "id"
    REMOTION_REASON = "remotion_reason"
    RIDES_COMPLETED = "rides_completed"
    START_TIMESTAMP = "start_timestamp"
    REMOTION_TIMESTAMP = "remotion_timestamp"
    RIDES_IDS_LIST = "rides_id_list"
    MOVING_TO_TAZS_LIST = "moving_to_tazs"
