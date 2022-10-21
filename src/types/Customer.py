from typing import TypedDict
from src.types.Human import HumanInfo


class CustomerInfo(HumanInfo):
    src_edge_id = str
    dst_edge_id = str
    src_pos = str
    dst_pos = str