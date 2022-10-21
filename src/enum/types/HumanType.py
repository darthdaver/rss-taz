from enum import Enum

class HumanType(str, Enum):
    DRIVER = "driver"
    CUSTOMER = "customer"