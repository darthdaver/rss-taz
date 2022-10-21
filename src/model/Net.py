from src.utils import utils
from src.enum.setup.FileSetup import FileSetup
from src.enum.setup.FileFormat import FileFormat
from src.enum.identifiers.Ride import Ride as RideType
from src.enum.identifiers.Net import Net as NetIdentifiers
from src.enum.identifiers.Config import Config as ConfigIdentifier
from src.enum.identifiers.Driver import Driver as DriverIdentifier
from src.enum.identifiers.Provider import Provider as ProviderIdentifier
from src.enum.identifiers.Route import Route as RouteIdentifier
from src.types.Driver import DriverInfo, DriverState
from src.enum.types.NetType import NetType
from src.enum.types.HumanType import HumanType
from src.types.Net import TazInfo
from src.types.Net import EdgeInfo
from src.model.Route import Route
from src.enum.types.RouteType import RouteType
from src.types.Human import PersonalityDistribution
from typing import Type, Union, Optional
import traci
import sumolib
from sumolib.net import Net as SumoNet
from sumolib.net.edge import Edge as SumoEdge
import random

class Net:
    def __init__(self, net):
        self.__analytics = net[NetType.ANALYTICS_NET.value]
        self.__boundary = net[NetType.BOUNDARY_NET.value]
        self.__mobility = net[NetType.MOBILITY_NET.value]
        self.__sumo_net: Type[SumoNet] = sumolib.net.readNet(FileSetup.NET_SUMO.value, withInternal=True)
        self.__travel_times = utils.read_file_from_absolute_path_to_file(FileSetup.TRAVEL_TIMES.value, FileFormat.JSON)
        self.__missing_travel_time_couples = utils.read_file_from_absolute_path_to_file(FileSetup.TRAVEL_TIMES_MISSING_COUPLES.value, FileFormat.JSON)

    def check_connection_travel_time(self, src, dst):
        if src in self.__missing_travel_time_couples:
            if dst in self.__missing_travel_time_couples[src]:
                return False
        return True

    @staticmethod
    def convert_route_to_str(
            route: list[Type[SumoEdge]]
    ) -> str:
        edge: Type[SumoEdge]
        idx: int
        route_edge_str: str = ""
        for idx, edge in enumerate(route):
            route_edge_str += f"{edge.getID()}"
            if idx < (len(route) - 1):
                route_edge_str += " "
        return route_edge_str

    @staticmethod
    def convert_route_to_edge_id_list(
            route: list[Type[SumoEdge]]
    ) -> str:
        route_list = list(map(lambda e: e.getID(), route))
        return route_list

    def expected_route_analytics(
            self,
            route: list[str]
    ) -> (float, float, float):
        src_taz_id = self.get_taz_id_from_edge_id(route[0], NetType.ANALYTICS_NET)
        dst_taz_id = self.get_taz_id_from_edge_id(route[-1], NetType.ANALYTICS_NET)
        expected_travel_time = self.__travel_times[src_taz_id][dst_taz_id][NetIdentifiers.MEAN_TRAVEL_TIME.value]
        expected_travel_length = sumolib.route.getLength(self.__sumo_net, route)
        std_travel_time = self.__travel_times[src_taz_id][dst_taz_id][NetIdentifiers.STD_TRAVEL_TIME.value]
        return (expected_travel_time, std_travel_time, expected_travel_length)

    def generate_destination_edge(
            self,
            src_taz_id: str,
            ride_length: RideType,
            net_type: NetType = NetType.BOUNDARY_NET
    ) -> str:
        net = self.__select_net(net_type)
        dst_taz_candidate_ids: list[str] = net[NetIdentifiers.TAZ.value][src_taz_id][NetIdentifiers.DISTANCE.value][ride_length.value]
        if len(dst_taz_candidate_ids) > 0:
            dst_taz_id: str = utils.select_from_list(dst_taz_candidate_ids)
            dst_edge_id: str = self.get_random_edge_from_taz_id(dst_taz_id, net_type=net_type)
            return dst_edge_id
        #print(f'Net.generate_destination_edge - destination edge not found from taz {src_taz_id} and ride length {ride_length}')
        return None

    def get_random_edge_from_taz_id(
            self,
            taz_id: str,
            exclude_edges_ids:[str]=[],
            net_type: NetType = NetType.BOUNDARY_NET
    ) -> str:
        net = self.__select_net(net_type)
        taz_edge_ids: list[str] = [*net[NetIdentifiers.TAZ.value][taz_id][NetIdentifiers.EDGES.value]]
        while len(taz_edge_ids) > 0:
            random_edge_id: str = utils.select_from_list(taz_edge_ids)
            edge: Type[SumoEdge] = self.__sumo_net.getEdge(random_edge_id)
            edge_length: float = edge.getLength()
            if edge_length > 0.0 and not(random_edge_id in exclude_edges_ids):
                return random_edge_id
            taz_edge_ids.remove(random_edge_id)
        #print(f"Net.get_random_edge_from_taz_id - Edge not found in taz {taz_id}")
        return None

    def generate_random_sumolib_route_in_taz(
            self,
            taz_id: str,
            src_edge_id: str,
            net_type: NetType = NetType.BOUNDARY_NET
    ):
        route: list[Type[SumoEdge]]
        cost: str
        exclude_edges_ids: list[str] = [src_edge_id]
        for i in range(5):
            dst_random_edge_id: str = self.get_random_edge_from_taz_id(taz_id, exclude_edges_ids, net_type)
            if dst_random_edge_id is None:
                return (None, None)
            src_analytics_taz_id = self.get_taz_id_from_edge_id(src_edge_id, NetType.ANALYTICS_NET)
            dst_analytics_taz_id = self.get_taz_id_from_edge_id(dst_random_edge_id, NetType.ANALYTICS_NET)
            if not self.check_connection_travel_time(src_analytics_taz_id, dst_analytics_taz_id):
                return (None, None)
            src_edge = self.__sumo_net.getEdge(src_edge_id)
            dst_random_edge = self.__sumo_net.getEdge(dst_random_edge_id)
            route, cost = self.__sumo_net.getOptimalPath(src_edge, dst_random_edge)
            if not route is None:
                return (route, cost)
            exclude_edges_ids.append(dst_random_edge_id)
        return (None, None)

    def generate_random_sim_route_in_taz(
            self,
            timestamp: float,
            taz_id: str,
            src_edge_id: str,
            src_pos: Optional[float] = None,
            net_type: NetType = NetType.BOUNDARY_NET
    ):
        route, cost = self.generate_random_sumolib_route_in_taz(taz_id, src_edge_id, net_type)
        if route is not None:
            src_edge = self.__sumo_net.getEdge(src_edge_id)
            dst_edge = route[-1]
            route_edge_id_list = self.convert_route_to_edge_id_list(route)
            src_pos: float = round(random.uniform(0.01, src_edge.getLength()), 2) if src_pos is None else src_pos
            dst_pos: float = round(random.uniform(0.01, dst_edge.getLength()), 2)
            sim_route = self.generate_sim_route_from_edge_id_list(
                timestamp,
                route_edge_id_list,
                src_pos,
                dst_pos
            )
            return sim_route
        return None

    def generate_sim_route_from_edge_id_list(
            self,
            timestamp: float,
            edge_id_list: list[str],
            src_pos: float,
            dst_pos: float
    ):
        route_id = f"route_from_{edge_id_list[0]}_to_{edge_id_list[-1]}"
        if route_id not in traci.route.getIDList():
            try:
                traci.route.add(route_id, edge_id_list)
            except:
                return None
        expected_travel_time, std_travel_time, expected_length = self.expected_route_analytics(edge_id_list)
        sim_route = Route(
            timestamp,
            RouteType.SUMO,
            route_id,
            edge_id_list,
            expected_travel_time,
            std_travel_time,
            expected_length,
            src_pos,
            dst_pos
        )
        return sim_route

    def generate_sumolib_route_from_src_dst_edge_ids(
            self,
            src_edge_id: str,
            dst_edge_id: str
    ) -> Union[list[SumoEdge], None]:
        src_edge = self.__sumo_net.getEdge(src_edge_id)
        dst_edge = self.__sumo_net.getEdge(dst_edge_id)
        src_analytics_taz_id = self.get_taz_id_from_edge_id(src_edge_id, NetType.ANALYTICS_NET)
        dst_analytics_taz_id = self.get_taz_id_from_edge_id(dst_edge_id, NetType.ANALYTICS_NET)
        if not self.check_connection_travel_time(src_analytics_taz_id, dst_analytics_taz_id):
            return None
        route, cost = self.__sumo_net.getOptimalPath(src_edge, dst_edge)
        if route is not None:
            route_id = f"route_from_{src_edge_id}_to_{dst_edge_id}"
            route_edge_id_list = self.convert_route_to_edge_id_list(route)
            if route_id not in traci.route.getIDList():
                try:
                    traci.route.add(route_id, route_edge_id_list)
                except:
                    # Generated route is not connected
                    return None
        return route

    def generate_sim_route_from_src_dst_edge_ids(
            self,
            timestamp: float,
            src_edge_id: str,
            dst_edge_id: str,
            src_pos: float,
            dst_pos: float
    ) -> Union[Type[Route], None]:
        sumolib_route = self.generate_sumolib_route_from_src_dst_edge_ids(src_edge_id, dst_edge_id)
        if sumolib_route is not None:
            route_edge_id_list = self.convert_route_to_edge_id_list(sumolib_route)
            sim_route = self.generate_sim_route_from_edge_id_list(timestamp, route_edge_id_list, src_pos, dst_pos)
            return sim_route
        return None

    def get_sumo_net_edge_ids(self) -> list[str]:
        sumo_edges = self.__sumo_net.getEdges()
        sumo_edges_ids = list(map(lambda e: e.getID(), sumo_edges))
        return sumo_edges

    def get_taz_id_from_edge_id(
            self,
            edge_id: str,
            net_type: Type[NetType] = NetType.BOUNDARY_NET
    ) -> str:
        net = self.__select_net(net_type)
        if edge_id not in net[NetIdentifiers.EDGES.value]:
            #print(f"Net.get_taz_id_from_edge_id - edge {edge_id} not in net type {net_type.value}")
            #print(f"Net.get_taz_id_from_edge_id - Check outgoing edges for edge {edge_id}")
            found_outgoing_in_net = False
            if self.__sumo_net.hasEdge(edge_id):
                edge = self.__sumo_net.getEdge(edge_id)
                outgoing_edges = list(edge.getOutgoing().keys())
                while len(outgoing_edges) > 0 and not found_outgoing_in_net:
                    outgoing_edge = outgoing_edges.pop(0)
                    outgoing_edge_id = outgoing_edge.getID()
                    if outgoing_edge_id in net[NetIdentifiers.EDGES.value]:
                        #print(f"Net.get_taz_id_from_edge_id - Found outgoing edge {outgoing_edge_id} for edge {edge_id}")
                        edge_id = outgoing_edge_id
                        found_outgoing_in_net = True
                        break
                    else:
                        outgoing_edges.extend(list(outgoing_edge.getOutgoing().keys()))
                if not found_outgoing_in_net:
                    raise Exception(f"Net.get_taz_id_from_edge_id - edge {edge_id} not in net type {net_type.value}")
            else:
                raise Exception(f"Net.get_taz_id_from_edge_id - edge {edge_id} not in net type {net_type.value}")
        taz_id = net[NetIdentifiers.EDGES.value][edge_id][NetIdentifiers.TAZ_ID.value]
        return taz_id

    def get_taz_info(
            self,
            taz_id: str,
            net_type: NetType = NetType.BOUNDARY_NET
    ) -> TazInfo:
        net = self.__select_net(net_type)
        return {
            **net[NetIdentifiers.TAZ.value][taz_id]
        }

    def get_all_taz_ids(
            self,
            net_type: NetType = NetType.BOUNDARY_NET
    ):
        net = self.__select_net(net_type)
        all_taz_ids = [*net[NetIdentifiers.TAZ].keys()]
        return all_taz_ids

    def get_all_taz_info(
            self,
            net_type: NetType = NetType.BOUNDARY_NET
    ):
        net = self.__select_net(net_type)
        all_taz_info: dict[str, TazInfo] = {}
        for taz_id in net[NetIdentifiers.TAZ.value].keys():
            all_taz_info[taz_id] = self.get_taz_info(taz_id, net_type)
        return all_taz_info

    def is_arrived(
            self,
            driver_info: Type[DriverInfo]
    ):
        driver_id = driver_info[DriverIdentifier.DRIVER_ID.value]
        driver_state = driver_info[DriverIdentifier.DRIVER_STATE.value]
        driver_route = driver_info[DriverIdentifier.ROUTE.value]
        if driver_state in [DriverState.PICKUP, DriverState.ON_ROAD]:
            dst_edge_id = driver_route[RouteIdentifier.DST_EDGE_ID.value]
            current_edge_id = traci.vehicle.getRoadID(driver_id)
            dst_pos = driver_route[RouteIdentifier.DST_POS.value]
            distance = round(traci.vehicle.getDrivingDistance(driver_id, dst_edge_id, dst_pos))
            if dst_edge_id == current_edge_id and distance == 0:
                return True
            return False
        elif driver_state in [DriverState.IDLE, DriverState.RESPONDING, DriverState.MOVING]:
            current_route_idx = traci.vehicle.getRouteIndex(driver_id) - 1
            route = traci.vehicle.getRoute(driver_id)
            driver_route_edge_id_list = driver_route[RouteIdentifier.EDGE_ID_LIST.value]
            if current_route_idx < 0:
                return False
            if current_route_idx >= len(driver_route):
                return True
            #print(current_route_idx)
            #print(len(driver_route_edge_id_list))
            #print(driver_route_edge_id_list)
            #print(route)
            current_edge = driver_route_edge_id_list[current_route_idx]
            if current_edge == driver_route_edge_id_list[-2]:
                return True
            return False

    def is_taz_id_in_net(
            self,
            taz_id,
            net_type
    ):
        net = self.__select_net(net_type)
        return taz_id in net[NetIdentifiers.TAZ.value].keys()

    def __select_net(
            self,
            net_type: NetType
    ):
        if net_type == NetType.ANALYTICS_NET:
            return self.__analytics
        elif net_type == NetType.BOUNDARY_NET:
            return self.__boundary
        elif net_type == NetType.MOBILITY_NET:
            return self.__mobility
        assert False, f"Net.__select_net - unknown net type: {net_type}"

    def update_personality_distribution_in_taz(
            self,
            taz_id: str,
            personality_distribution: PersonalityDistribution,
            agent_type: Type[HumanType],
            net_type: Type[NetType] = NetType.BOUNDARY_NET
    ):
        net = self.__select_net(net_type)
        assert agent_type in [HumanType.DRIVER, HumanType.CUSTOMER], f"Map.update_personality_distribution - unknown label {agent_type}"
        taz = net[NetIdentifiers.TAZ.value][taz_id]
        taz[ConfigIdentifier.PERSONALITY_DISTRIBUTION.value][agent_type.value.lower()] = personality_distribution

    def update_taz_balance(
            self,
            taz_id: str,
            balance: float,
            net_type: Type[NetType] = NetType.BOUNDARY_NET
    ):
        net = self.__select_net(net_type)
        taz = net[NetIdentifiers.TAZ.value][taz_id]
        taz[ProviderIdentifier.BALANCES.value].insert(0, balance)

    def update_taz_surge_multiplier(
            self,
            taz_id: str,
            surge_multiplier: float,
            net_type: Type[NetType] = NetType.BOUNDARY_NET
    ):
        net = self.__select_net(net_type)
        taz = net[NetIdentifiers.TAZ.value][taz_id]
        taz[ProviderIdentifier.SURGE_MULTIPLIERS.value].insert(0, surge_multiplier)