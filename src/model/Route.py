from typing import Type
from src.enum.types.RouteType import RouteType
from src.enum.identifiers.Route import Route as RouteIdentifiers
from src.types.Route import RouteInfo

class Route:
    def __init__(
            self,
            timestamp: float,
            route_type: Type[RouteType],
            route_id: str,
            edge_id_list: list[str],
            expected_travel_time: float,
            std_travel_time: float,
            expected_length: float,
            src_pos: float = 0.0,
            dst_pos: float = 0.0
    ):
        self.__timestamp = timestamp
        self.__id = route_id
        self.__route_type = route_type
        self.__edge_id_list = edge_id_list
        self.__expected_length = expected_length
        self.__expected_travel_time = expected_travel_time
        self.__std_travel_time = std_travel_time
        self.__src_pos = src_pos
        self.__dst_pos = dst_pos

    def get_destination_edge_id(self) -> str:
        return self.__edge_id_list[-1]

    def get_destination_position(self) -> float:
        return self.__dst_pos

    def get_expected_length(self) -> float:
        return self.__expected_length

    def get_expected_travel_time(self) -> float:
        return self.__expected_travel_time

    def get_info(self) -> RouteInfo: ###
        route_info = self.to_dict()
        return route_info

    def get_std_travel_time(self) -> float:
        return self.__std_travel_time

    def get_route_edge_id_list(self) -> list[str]:
        return [*self.__edge_id_list]

    def get_route_id(self) -> str:
        return self.__id

    def get_route_type(self) -> Type[RouteType]:
        return self.__route_type

    def get_source_edge_id(self) -> str:
        return self.__edge_id_list[0]

    def get_timestamp(self) -> float:
        return self.__timestamp

    def set_destination_position(self, destination_position: float):
        self.__dst_pos = destination_position

    def to_dict(self) -> RouteInfo: ###
        return {
            RouteIdentifiers.ROUTE_ID.value: self.__id,
            RouteIdentifiers.ROUTE_TYPE.value: self.__route_type,
            RouteIdentifiers.EDGE_ID_LIST.value: self.__edge_id_list,
            RouteIdentifiers.EXPECTED_LENGTH.value: self.__expected_length,
            RouteIdentifiers.EXPECTED_TRAVEL_TIME.value: self.__expected_travel_time,
            RouteIdentifiers.STD_TRAVEL_TIME.value: self.__std_travel_time,
            RouteIdentifiers.SRC_POS.value: self.__src_pos,
            RouteIdentifiers.DST_POS.value: self.__dst_pos,
            RouteIdentifiers.DST_EDGE_ID.value: self.get_destination_edge_id(),
            RouteIdentifiers.SRC_EDGE_ID.value: self.get_source_edge_id()
        }