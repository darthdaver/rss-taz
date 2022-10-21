import os
import xmltodict
from src.enum.setup.Paths import Paths
from src.enum.setup.Dataset import Dataset
from src.enum.setup.FileName import FileName
from src.enum.setup.FileFormat import FileFormat
from src.enum.setup.FileSetup import FileSetup
from src.enum.setup.City import City
from src.enum.types.NetType import NetType
from src.enum.identifiers.Net import Net as NetIdentifier
from src.enum.identifiers.Provider import Provider
from src.types.Net import TazInfo
from src.enum.identifiers.Human import Human
from src.enum.state.RideState import RideState
from src.enum.identifiers.Ride import Ride
from src.enum.identifiers.Config import Config
from src.types.Net import EdgeInfo
from src.enum.types.PersonalityType import PersonalityType
from src.utils import utils
from typing import Type
import sumolib

class NetParser():
    def __init__(self, net_datasets_types: list[[Type[Dataset],Type[NetType]]], city: City):
        self.__net_datasets_types = net_datasets_types
        self.__sumo_net = sumolib.net.readNet(FileSetup.NET_SUMO.value, withInternal=True)
        self.__customer_setup = utils.read_file_from_absolute_path_to_file(FileSetup.CUSTOMER.value, FileFormat.JSON)
        self.__driver_setup = utils.read_file_from_absolute_path_to_file(FileSetup.DRIVER.value, FileFormat.JSON)
        self.__city = city
        self.__net = { str(n_t.value): { NetIdentifier.TAZ.value: {}, NetIdentifier.EDGES.value: {}} for d, n_t in net_datasets_types }
        self.__edge_id_set = set([])

    def collect_edges(self):
        total_edge_id_sets = []
        for dataset, net_type in self.__net_datasets_types:
            dataset_edge_id_set = set([])
            input_edge_districts_absolute_path = utils.generate_absolute_path_to_file(
                Paths.EDGE,
                FileName.EDGE_DISTRICTS,
                FileFormat.XML,
                dataset,
                self.__city
            )
            edge_districts_xml_file = utils.read_file_from_absolute_path_to_file(input_edge_districts_absolute_path, FileFormat.XML)
            edge_districts_dict = xmltodict.parse(edge_districts_xml_file)
            for taz in edge_districts_dict["tazs"]["taz"]:
                edge_id_list = taz["@edges"].split(" ")
                dataset_edge_id_set.update(edge_id_list)
            total_edge_id_sets.append(dataset_edge_id_set)
        common_edge_ids = set([])
        for idx, edge_id_set in enumerate(total_edge_id_sets):
            if idx == 0:
                common_edge_ids = edge_id_set
            common_edge_ids = common_edge_ids.intersection(edge_id_set)
        self.__edge_id_set.update(common_edge_ids)
        print(f"Total edges: {len(common_edge_ids)}")
        print(f"Discarded {len(set.union(*total_edge_id_sets)) - len(self.__edge_id_set)} edges")


    def export_net(self):
        utils.check_path_exists(Paths.NET_SIMULATOR)
        output_absolute_path = FileSetup.NET_SIMULATOR
        utils.export_file_from_absolute_path(output_absolute_path, FileFormat.JSON, self.__net)

    def export_csv_disctrict_edges(self, edge_districts_dict: dict, dataset: Type[Dataset]):
        content = "taz_id,edge_id\n"
        for taz in edge_districts_dict:
            id = taz["@id"]
            edges = taz["@edges"].split(" ")
            for edge in edges:
                content += f"{id},{edge}\n"
        output_absolute_path = utils.generate_absolute_path_to_file(
            Paths.TAZ_EDGE,
            FileName.TAZ_EDGE,
            FileFormat.CSV,
            dataset,
            self.__city
        )
        utils.export_file_from_absolute_path(output_absolute_path, FileFormat.CSV, content)

    def parse_centroids(self):
        for dataset, net_type in self.__net_datasets_types:
            input_centroids_absolute_path = utils.generate_absolute_path_to_file(
                Paths.CENTROIDS_TAZ,
                FileName.CENTROIDS,
                FileFormat.JSON,
                dataset,
                self.__city
            )
            centroids = utils.read_file_from_absolute_path_to_file(input_centroids_absolute_path, FileFormat.JSON)
            taz_ids = self.__net[net_type][NetIdentifier.TAZ].keys()
            for taz_id in taz_ids:
                self.__net[net_type][NetIdentifier.TAZ.value][NetIdentifier.CENTROIDS.value] = centroids[taz_id]


    def parse_taz_edges(self):
        for dataset, net_type in self.__net_datasets_types:
            input_taz_poly_absolute_path = utils.generate_absolute_path_to_file(
                Paths.TAZ,
                FileName.TAZ_POLY_SUMO,
                FileFormat.XML,
                dataset,
                self.__city
            )
            input_edge_districts_absolute_path = utils.generate_absolute_path_to_file(
                Paths.EDGE,
                FileName.EDGE_DISTRICTS,
                FileFormat.XML,
                dataset,
                self.__city
            )
            output_taz_poly_absolute_path = utils.generate_absolute_path_to_file(
                Paths.TAZ,
                FileName.TAZ_POLY_DICT,
                FileFormat.JSON,
                dataset,
                self.__city
            )
            output_edge_districts_absolute_path = utils.generate_absolute_path_to_file(
                Paths.EDGE,
                FileName.EDGE_DISTRICTS_DICT,
                FileFormat.JSON,
                dataset,
                self.__city
            )
            taz_poly_dict, edge_districts_dict = self.taz_xml_to_json(input_taz_poly_absolute_path, input_edge_districts_absolute_path)
            self.__clean_taz(taz_poly_dict)
            self.__clean_taz(edge_districts_dict)
            utils.export_file_from_absolute_path(output_taz_poly_absolute_path, FileFormat.JSON, taz_poly_dict)
            utils.export_file_from_absolute_path(output_edge_districts_absolute_path, FileFormat.JSON, edge_districts_dict)
            self.export_csv_disctrict_edges(edge_districts_dict, dataset)
            self.__generate_taz_edge_info(edge_districts_dict, dataset, net_type)

    def taz_xml_to_json(self, taz_absolute_path: str, edge_absolute_path: str):
        taz_poly_xml_file = utils.read_file_from_absolute_path_to_file(taz_absolute_path, FileFormat.XML)
        edge_districts_xml_file = utils.read_file_from_absolute_path_to_file(edge_absolute_path, FileFormat.XML)
        taz_poly_dict = xmltodict.parse(taz_poly_xml_file)
        edge_districts_dict = xmltodict.parse(edge_districts_xml_file)
        return taz_poly_dict["additional"]["poly"], edge_districts_dict["tazs"]["taz"]

    def __clean_taz(self, taz_dict: dict):
        for taz in taz_dict:
            if '#' in taz["@id"]:
                taz["@id"] = taz["@id"][:taz["@id"].index('#')]
            if "param" in taz:
                params_dict = {}
                for param_dict in taz["param"]:
                    params_dict[param_dict["@key"]] = param_dict["@value"]
                taz["param"] = params_dict

    def __generate_taz_edge_info(self, edge_districts_dict: dict, dataset: Type[Dataset], net_type: Type[NetType]):
        taz_dict = {}
        edge_dict = {}
        input_centroids_absolute_path = utils.generate_absolute_path_to_file(
            Paths.CENTROIDS_TAZ,
            FileName.CENTROIDS,
            FileFormat.JSON,
            dataset,
            self.__city
        )
        centroids = utils.read_file_from_absolute_path_to_file(input_centroids_absolute_path, FileFormat.JSON)
        for taz in edge_districts_dict:
            taz_id = taz["@id"]
            edges = taz["@edges"].split(" ")
            taz_dict[taz_id]: Type[TazInfo] = {
                "id": taz_id,
                Config.PERSONALITY_DISTRIBUTION.value: {
                    Human.CUSTOMERS.value: list(map(lambda p: [p[0], PersonalityType(p[1])], self.__customer_setup[Config.PERSONALITY_DISTRIBUTION.value])),
                    Human.DRIVERS.value: list(map(lambda p: [p[0], PersonalityType(p[1])], self.__driver_setup[Config.PERSONALITY_DISTRIBUTION.value]))
                },
                Provider.BALANCES.value: [1],
                Provider.SURGE_MULTIPLIERS.value: [1],
                Ride.STARTED.value: 0,
                Ride.ENDED.value: 0,
                Ride.REQUESTED.value: 0,
                Ride.REJECTED.value: 0,
                Ride.CANCELED.value: 0,
                Ride.NOT_SERVED.value: 0,
                NetIdentifier.EDGES.value: [],
                NetIdentifier.DISTANCE.value: centroids[taz_id]
            }
            for edge_id in edges:
                if edge_id in self.__edge_id_set:
                    edge = self.__sumo_net.getEdge(edge_id)
                    taz_dict[taz_id][NetIdentifier.EDGES.value].append(edge_id)
                    edge_dict[edge_id] = {
                        "id": edge_id,
                        NetIdentifier.TAZ_ID.value: taz_id,
                        NetIdentifier.LENGTH.value: edge.getLength(),
                        NetIdentifier.SPEED.value: edge.getSpeed()
                    }
        self.__net[net_type][NetIdentifier.TAZ.value] = taz_dict
        self.__net[net_type][NetIdentifier.EDGES.value] = edge_dict

net_datasets_types = [
    (Dataset.SFCTA, NetType.MOBILITY_NET),
    (Dataset.STANFORD, NetType.BOUNDARY_NET),
    (Dataset.UBER, NetType.ANALYTICS_NET)
]

net_parser: Type[NetParser] = NetParser(net_datasets_types, City.SAN_FRANCISCO)
net_parser.collect_edges()
net_parser.parse_taz_edges()
net_parser.export_net()