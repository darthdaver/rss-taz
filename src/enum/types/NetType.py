from enum import Enum

class NetType(str, Enum):
    BOUNDARY_NET = "boundary"
    MOBILITY_NET = "mobility"
    ANALYTICS_NET = "analytics"