from src.enum.identifiers.Api import Api as ApiIdentifier
from src.enum.api.Api import Api
from src.utils import utils
from src.enum.identifiers.Customer import Customer as CustomerIdentifier
from src.model.Customer import Customer
from src.model.Driver import Driver
from src.model.Ride import Ride
from src.enum.identifiers.Ride import Ride as RideIdentifier
from typing import Type
from src.types.Driver import DriverInfo
from src.enum.identifiers.Driver import Driver as DriverIdentifier
from src.enum.identifiers.Request import Request as RequestIdentifier
import sumolib
from src.enum.setup.FileSetup import FileSetup
from src.model.Net import Net

sumo_net = sumolib.net.readNet(FileSetup.NET_SUMO.value, withInternal=True)

def collect_candidates(driver_info: Type[DriverInfo], meeting_edge_id, max_driver_distance, lock):
    driver_id = driver_info[DriverIdentifier.DRIVER_ID.value]
    driver_edge_id = driver_info[DriverIdentifier.CURRENT_EDGE_ID.value]
    """route_edge_id_list, cost = utils.sumo_net_api_call(
        Api.GET_OPTIMAL_PATH,
        {
            ApiIdentifier.SRC_EDGE_ID.value: meeting_edge_id,
            ApiIdentifier.DST_EDGE_ID.value: driver_edge_id
        }
    )"""
    src_edge_id = meeting_edge_id
    dst_edge_id = driver_edge_id
    src_edge = sumo_net.getEdge(src_edge_id)
    dst_edge = sumo_net.getEdge(dst_edge_id)
    route, cost = sumo_net.getOptimalPath(src_edge, dst_edge)
    if route is not None:
        route_edge_id_list = Net.convert_route_to_edge_id_list(route)
        if len(route_edge_id_list) > 0 and cost <= max_driver_distance:
            return {
                RequestIdentifier.CANDIDATE_ID.value: driver_id,
                RequestIdentifier.COST.value: cost,
                RequestIdentifier.RESPONSE_COUNT_DOWN.value: 15,
                RequestIdentifier.SEND_REQUEST_BACK_TIMER.value: utils.random_int_from_range(0, 11)
            }
    else:
        return None


def get_customer_info(customer_id: str, customers: list[Type[Customer]]):
    return customers[customer_id].get_info()


def get_driver_info(driver_id: str, drivers: list[Type[Driver]]):
    return drivers[driver_id].get_info()


def request_generator(customer_id: str, customers, ride_id_counter, lock):
    with lock:
        ride_id = f"ride_{ride_id_counter.value}"
        ride_id_counter.value += 1
    customer_info = customers[customer_id].get_info()
    src_edge_id = customer_info[CustomerIdentifier.SRC_EDGE_ID.value]
    dst_edge_id = customer_info[CustomerIdentifier.DST_EDGE_ID.value]
    src_pos = customer_info[CustomerIdentifier.SRC_POS.value]
    dst_pos = customer_info[CustomerIdentifier.DST_POS.value]
    stats = {
        RideIdentifier.STAT_SRC_TAZ_ID.value: src_edge_id,
        RideIdentifier.STAT_DST_TAZ_ID.value: dst_edge_id
    }
    return Ride(ride_id, customer_id, src_edge_id, dst_edge_id, src_pos, dst_pos, stats)


def next_traci_step(lock):
    print("next")
    with lock:
        response = utils.traci_api_call(Api.SIMULATION_STEP)


def solve_customers_inconsistencies(customer_id: str, traci_customers_list: list[str], sim_customers_ids: list[str], lock):
    if not customer_id in traci_customers_list:
        print(customer_id)
        return customer_id
    elif not customer_id in sim_customers_ids:
        # print(f"{customer_id} not removed by the sumo simulator.")
        print(customer_id)
        with lock:
            utils.traci_api_call(Api.REMOVE_CUSTOMER, { "id": customer_id })
        return -1
    return -1


def solve_drivers_inconsistencies(driver_id: str, traci_drivers_list: list[str], sim_drivers_ids: list[str], lock):
    if not driver_id in traci_drivers_list:
        #print(f"Sumo forced {driver_id} remotion.")
        return driver_id
    elif not driver_id in sim_drivers_ids:
        #print(f"{driver_id} not removed by the sumo simulator.")
        with lock:
            utils.traci_api_call(Api.REMOVE_DRIVER, { "id": driver_id })
        return -1
    return -1


def start_traci(lock):
    with lock:
        response = utils.traci_api_call(Api.START_TRACI)


def start_sumo_net(lock):
    with lock:
        response = utils.sumo_net_api_call(Api.START_SUMO_NET)