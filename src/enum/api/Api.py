from enum import Enum

class Api(str, Enum):
    # TRACI
    CUSTOMERS_ID_LIST = "customers_id_list"
    DRIVERS_ID_LIST = "drivers_id_list"
    START_TRACI = "start_traci"
    REMOVE_CUSTOMER = "remove_customer"
    REMOVE_DRIVER = "remove_driver"
    SIMULATION_STEP = "simulation_step"
    SIMULATION_TIME = "simulation_time"
    CUSTOMER_CURRENT_EDGE_ID = "customer_current_edge_id"
    DRIVER_CURRENT_EDGE_ID = "driver_current_edge_id"
    CUSTOMER_CURRENT_POS = "customer_current_pos"
    DRIVER_CURRENT_POS = "driver_current_pos"
    SET_ROUTE_ID = "set_route_id"
    SET_STOP = "set_stop"
    APPEND_STAGE = "append_stage"
    REMOVE_CUSTOMER_STAGE = "remove_customer_stage"
    GET_PERSON_NUMBER = "get_person_number"
    CLOSE_TRACI = "close_traci"
    GET_ROUTE_INDEX = "get_route_index"
    CUSTOMER_GET_EDGES = "customer_get_edges"

    # SUMO_NET
    GET_EDGE_OUTGOINGS = "get_edge_outgoings"
    GET_EDGE_LENGTH = "get_edge_outgoings"
    GET_OPTIMAL_PATH = "get_optimal_path"
    START_SUMO_NET = "start_sumo_net"