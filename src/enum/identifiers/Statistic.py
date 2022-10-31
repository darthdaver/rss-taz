from enum import Enum

class Statistic(str, Enum):
    ID = "id"
    REMOTION_REASON = "remotion_reason"
    RIDES_COMPLETED = "rides_completed"
    START_TIMESTAMP = "start_timestamp"
    REMOTION_TIMESTAMP = "remotion_timestamp"
    RIDES_IDS_LIST = "rides_id_list"
    MOVING_TO_TAZS_LIST = "moving_to_tazs"
    REQUESTED = "requested"
    CANCELED = "canceled"
    ACCEPTED = "accepted"
    NOT_SERVED = "not_served"
    REJECTIONS = "rejections"
    IDLE_DRIVERS = "idle_drivers"
    RESPONDING_DRIVERS = "responding_drivers"
    PICKUP_DRIVERS = "pickup_drivers"
    ON_ROAD_DRIVERS = "on_road_drivers"
    MOVING_DRIVERS = "moving_drivers"
    ACTIVE_CUSTOMERS = "active_customers"
    PENDING_CUSTOMERS = "pending_customers"
    PICKUP_CUSTOMERS = "pickup_customers"
    ON_ROAD_CUSTOMERS = "on_road_customers"
    SIM_FAILURE_REJECTIONS = "sim_failure_rejections"
    SIM_FAILURE = "sim_failure"