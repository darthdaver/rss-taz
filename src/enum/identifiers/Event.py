from enum import Enum

class Event(str, Enum):
    GENERATION_DISTRIBTUON = "generation_distribution"
    AGENT_TYPE = "agent_type"
    TAZ_LIST = "taz_list"
    TAZ_ID = "taz_id"
    START = "start"