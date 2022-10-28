from src.utils import utils
from src.enum.setup.Paths import Paths
from src.enum.setup.FileName import FileName
from src.enum.setup.FileFormat import FileFormat
from src.enum.setup.Dataset import Dataset
from src.enum.setup.City import City
from src.enum.identifiers.Net import Net as NetIdentifier
import random
import math

def generate_travel_times_files(taz_poly):
    travel_times = {taz["@id"]: {} for taz in taz_poly}
    travel_times_missing_couples = {taz["@id"]: [] for taz in taz_poly}
    for taz in taz_poly:
        taz_id = taz["@id"]
        centroid = (float(taz["param"]["centroid_x"]), float(taz["param"]["centroid_y"]))
        for other_taz in taz_poly:
            other_taz_id = other_taz["@id"]
            other_centroid = (float(other_taz["param"]["centroid_x"]), float(other_taz["param"]["centroid_y"]))
            distance = math.dist(centroid, other_centroid)
            if other_taz_id not in travel_times[taz_id]:
                travel_times[taz_id][other_taz_id] = {}
            travel_times[taz_id][other_taz_id][NetIdentifier.MEAN_TRAVEL_TIME] = distance
            travel_times[taz_id][other_taz_id][NetIdentifier.STD_TRAVEL_TIME] = distance / 2
    output_absolute_file_path = utils.generate_absolute_path_to_file(
        Paths.MOBILITY,
        FileName.TRAVEL_TIME_OUT,
        FileFormat.JSON,
        Dataset.TEST,
        City.CITY
    )
    utils.export_file_from_absolute_path(
        output_absolute_file_path,
        FileFormat.JSON,
        travel_times
    )
    output_absolute_file_path = utils.generate_absolute_path_to_file(
        Paths.MOBILITY,
        FileName.TRAVEL_TIME_MISSING_COUPLES,
        FileFormat.JSON,
        Dataset.TEST,
        City.CITY
    )
    utils.export_file_from_absolute_path(
        output_absolute_file_path,
        FileFormat.JSON,
        travel_times_missing_couples
    )


def generate_pickups_file(taz_poly):
    travel_times = {taz["@id"]: {} for taz in taz_poly}
    travel_times_missing_couples = {taz["@id"]: [] for taz in taz_poly}
    pickups = {}
    seed = random.seed(123)
    for taz in taz_poly:
        taz_id = taz["@id"]
        pickups[taz_id] = {
            "taz": taz_id,
            "sum": max(0.5, random.random()) * 1000,
            "max": max(0.5, random.random()) * 1000,
            "min": max(0.5, random.random()) * 1000,
            "mean": max(0.5, random.random()) * 1000,
            "std": max(0.5, random.random()) * 1000,
            "25p": max(0.5, random.random()) * 1000,
            "50p": max(0.5, random.random()) * 1000,
            "75p": max(0.5, random.random()) * 1000
        }
    output_absolute_file_path = utils.generate_absolute_path_to_file(
        Paths.MOBILITY,
        FileName.PICKUPS_STATS,
        FileFormat.JSON,
        Dataset.TEST,
        City.CITY
    )
    utils.export_file_from_absolute_path(
        output_absolute_file_path,
        FileFormat.JSON,
        pickups
    )

if __name__ == "__main__":
    input_absolute_file_path = utils.generate_absolute_path_to_file(
        Paths.TAZ,
        FileName.TAZ_POLY_DICT,
        FileFormat.JSON,
        Dataset.TEST,
        City.CITY
    )
    taz_poly = utils.read_file_from_absolute_path_to_file(
        input_absolute_file_path,
        FileFormat.JSON
    )
    generate_travel_times_files(taz_poly)
    generate_pickups_file(taz_poly)
