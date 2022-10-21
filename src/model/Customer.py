from typing import Type
from src.model.Human import Human
from src.enum.identifiers.Customer import Customer as CustomerIdentifiers
from src.enum.state.CustomerState import CustomerState
from src.enum.types.PersonalityType import PersonalityType
from src.types.Customer import CustomerInfo


class Customer(Human):
    def __init__(
            self,
            timestamp: float,
            id: str,
            personality: Type[PersonalityType],
            state: CustomerState,
            src_edge_id: str,
            dst_edge_id: str,
            src_pos: str,
            dst_pos: str
    ):
        super().__init__(timestamp, id, state, personality)
        self.__src_edge_id = src_edge_id
        self.__dst_edge_id = dst_edge_id
        self.__src_pos = src_pos
        self.__dst_pos = dst_pos

    def get_info(self) -> CustomerInfo:
        return {
            **super().get_info(),
            CustomerIdentifiers.SRC_EDGE_ID.value: self.__src_edge_id,
            CustomerIdentifiers.DST_EDGE_ID.value: self.__dst_edge_id,
            CustomerIdentifiers.SRC_POS.value: self.__src_pos,
            CustomerIdentifiers.DST_POS.value: self.__dst_pos
        }

    def set_state(self, state: CustomerState) -> CustomerInfo:
        self.state = state
        return self.get_info()

    def update_cancel(self) -> CustomerInfo:
        self.state = CustomerState.INACTIVE
        return self.get_info()

    def update_end(self) -> CustomerInfo:
        self.state = CustomerState.INACTIVE
        return self.get_info()

    def update_on_road(self) -> CustomerInfo:
        self.state = CustomerState.ON_ROAD
        return self.get_info()

    def update_pending(self) -> CustomerInfo:
        self.state = CustomerState.PENDING
        return self.get_info()

    def update_pickup(self) -> CustomerInfo:
        self.state = CustomerState.PICKUP
        return self.get_info()
