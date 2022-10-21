from src.model.Human import Human
from src.enum.state.DriverState import DriverState
from src.enum.types.PersonalityType import PersonalityType
from src.model.Route import Route
from src.types.Driver import DriverInfo
from typing import Type

class Driver(Human):
    def __init__(
            self,
            timestamp: float,
            id: str,
            personality: Type[PersonalityType],
            route: Type[Route],
            state: Type[DriverState],
            last_ride_timestamp: float = None,
            rides_completed: int = 0,
            routes_updates: int = 0
    ):
        super().__init__(timestamp, id, state, personality)
        self.__route: Type[Route] = route
        self.__current_edge_id: str = route.get_source_edge_id()
        self.__last_ride_timestamp: float = timestamp if last_ride_timestamp is None else last_ride_timestamp
        self.__rides_completed: int = rides_completed
        self.__routes_updates: int = routes_updates

    def change_personality(self, new_personality: Type[PersonalityType]) -> DriverInfo:
        super().change_personality(new_personality)
        return self.get_info()

    def get_info(self) -> DriverInfo:
        return {
            **super().get_info(),
            "route": None if self.__route is None else self.__route.to_dict(),
            "last_ride_timestamp": self.__last_ride_timestamp,
            "rides_completed": self.__rides_completed,
            "current_edge_id": self.__current_edge_id
        }

    def receive_request(self) -> DriverInfo:
        self.state = DriverState.RESPONDING
        return self.get_info()

    def reject_request(self) -> DriverInfo:
        self.state = DriverState.IDLE
        return self.get_info()

    def set_route(self, route: Type[Route]) -> DriverInfo:
        self.__route = route
        return self.get_info()

    def set_route_destination_position(self, dst_pos: float):
        self.__route.set_destination_position(dst_pos)

    def set_state(self, state: Type[DriverState]) -> DriverInfo:
        self.state = state
        return self.get_info()

    def update_cancel(self):
        pass

    def update_current_edge_id(self, current_edge_id):
        self.__current_edge_id = current_edge_id

    def update_end(self, timestamp: float, route: Type[Route]) -> DriverInfo:
        self.state = DriverState.IDLE
        self.__route = route
        self.__last_ride_timestamp = timestamp
        self.__rides_completed += 1
        return self.get_info()

    def update_end_moving(self, route: Type[Route]) -> DriverInfo:
        self.state = DriverState.IDLE
        self.__route = route
        return self.get_info()

    def update_on_road(self, route: Route) -> DriverInfo:
        self.__route = route
        self.state = DriverState.ON_ROAD
        return self.get_info()

    def update_pickup(self, route: Type[Route]) -> DriverInfo:
        self.state = DriverState.PICKUP
        self.__route = route
        return self.get_info()
    