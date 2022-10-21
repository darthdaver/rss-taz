from enum import Enum

class FileFormat(str, Enum):
    CSV = "csv"
    GEOJSON = "geojson"
    JSON = "json"
    XML = "xml"