from enum import Enum
import os

# Considering the current position of the file (root-->src-->state)
PROJECT_ROOT_PATH = f"{os.getcwd()}/../.."

class MobilityXML(str, Enum):
    # Elements
    ROUTES = "routes"
    TRIP = "trip"
    PERSON = "person"
    VEHICLE = "vehicle"
    VEHICLE_TYPE = "vType"
    STOP = "stop"
    WALK = "walk"
    RIDE = "ride"
    ROUTE = "route"

    # Attributes
    ID = "id"
    DEPART = "depart"
    DEPART_POS = "departPos"
    START_POS = "startPos"
    DURATION = "duration"
    LANE = "lane"
    EDGES = "edges"

