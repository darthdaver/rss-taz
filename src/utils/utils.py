import os
import random
import json
import csv
from xml.dom import minidom
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Type
from src.enum.setup.City import City
from src.enum.setup.FileFormat import FileFormat
from src.enum.setup.FileName import FileName
from src.enum.setup.Dataset import Dataset
from src.enum.setup.Scenario import Scenario
from src.enum.identifiers.Api import Api as ApiIdentifier
from src.enum.setup.Paths import Paths
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
from typing import Union, Dict
import requests

def check_path_exists(path, is_path_file=False):
    if is_path_file:
        path = path[:path.rindex('/')]
    if not os.path.exists(path):
        os.makedirs(path)


def check_paths_exists(paths: list[[str, bool]]):
    for path, is_file in paths:
        check_path_exists(path, is_path_file=is_file)


def export_file(file_path: Type[Paths], file_name: Type[FileName], file_format: Type[FileFormat], dataset: Type[Dataset],  content: Union[str, dict, Type[Element]], city: Union[Type[City], None], mode: str = "w"):
    check_path_exists(file_path.value)
    complete_file_path = f"{os.path.join(file_path.value, dataset.value, file_format.value)}"
    city_prefix = f"{city.value}_" if not city is None else ""
    complete_file_name = f"{city_prefix}_{dataset.value}_{file_name.value}"
    absolute_path_to_file = f"{os.path.join(complete_file_path, complete_file_name)}.{file_format.value}"
    if file_format == FileFormat.CSV:
        assert type(content) == str, f"utils.export_file - unknown content type: {type(content)} instead of str"
        with open(absolute_path_to_file, mode) as csv_out_file:
            csv_out_file.write(content)
        return
    elif file_format == FileFormat.JSON:
        assert type(content) == dict or type(content) == list, f"utils.export_file - unknown content type: {type(content)} instead of dict"
        with open(absolute_path_to_file, mode) as json_out_file:
            json.dump(content, json_out_file)
        return
    elif file_format == FileFormat.XML:
        assert type(content) == Element, f"utils.export_file - unknown content type: {type(content)} instead of xml.ElementTree.Element"
        xml_str = minidom.parseString(ET.tostring(content)).toprettyxml(indent="   ")
        with open(absolute_path_to_file, mode) as xml_out_file:
            xml_out_file.write(xml_str)
        return


def export_file_from_absolute_path(absolute_path_to_file: str, file_format: Type[FileFormat], content: Union[str, dict, Type[Element]], mode: str = "w"):
    check_path_exists(absolute_path_to_file, is_path_file=True)
    if file_format == FileFormat.CSV:
        assert type(content) == str, f"utils.export_file - unknown content type: {type(content)} instead of str"
        with open(absolute_path_to_file, mode) as csv_out_file:
            csv_out_file.write(content)
        return
    elif file_format == FileFormat.JSON:
        assert type(content) == dict or type(content) == list, f"utils.export_file - unknown content type: {type(content)} instead of dict"
        with open(absolute_path_to_file, mode) as json_out_file:
            json.dump(content, json_out_file, indent=4)
        return
    elif file_format == FileFormat.XML:
        assert type(content) == Element, f"utils.export_file - unknown content type: {type(content)} instead of xml.ElementTree.Element"
        xml_str = minidom.parseString(ET.tostring(content)).toprettyxml(indent="   ")
        with open(absolute_path_to_file, mode) as xml_out_file:
            xml_out_file.write(xml_str)
        return


def generate_absolute_path_to_dir(path: Type[Paths], file_format: Type[FileFormat], dataset: Type[Dataset]):
    return f"{os.path.join(path.value, dataset.value, file_format.value)}"


def generate_absolute_path_to_file(path: Type[Paths], file_name: Type[FileName], file_format: Type[FileFormat], dataset: Type[Dataset], city: Type[City]):
    complete_file_name = f"{city.value}_{dataset.value}_{file_name.value}"
    complete_path = f"{os.path.join(path.value, dataset.value, file_format.value)}"
    return f"{os.path.join(complete_path, complete_file_name)}.{file_format.value}"


def generate_absolute_path_to_file(path: Type[Paths], file_name: Type[FileName], file_format: Type[FileFormat], identifier: Union[Type[Dataset],Type[Scenario]], city: Type[City]):
    complete_file_name = f"{city.value}_{identifier.value}_{file_name.value}"
    complete_path = f"{os.path.join(path.value, identifier.value, file_format.value)}"
    return f"{os.path.join(complete_path, complete_file_name)}.{file_format.value}"


def list_data_files_in_dir(path_to_dir: str, starts_with_str: Union[str, None] = None):
    file_name_list = []
    for file_name in os.listdir(path_to_dir):
        if (starts_with_str is not None) or file_name.startswith(starts_with_str):
            # remove file format
            #file_name = file_name[:file_name.rindex('.')]
            file_name_list.append(file_name)
    return file_name_list


def random_choice(p=0.5):
    return random.random() < p


def random_int_from_range(min_int, max_int):
    return random.randint(min_int, max_int)


def read_file(input_file_path: Type[Paths], input_file_name: Type[FileName], input_file_format: Type[FileFormat], input_dataset: Type[Dataset]):
    absolute_path_to_file = f"{os.path.join(input_file_path.value, input_dataset.value, input_file_format.value, input_file_name.value)}.{input_file_format.value}"
    if input_file_format == FileFormat.CSV:
        with open(absolute_path_to_file) as input_file:
            csv_reader = csv.reader(input_file, delimiter=',')
            return csv_reader
    elif input_file_format == FileFormat.JSON:
        with open(absolute_path_to_file) as input_file:
            input_obj = json.load(input_file)
            return input_obj
    elif input_file_format == FileFormat.XML:
        with open(absolute_path_to_file, 'r') as input_file:
            return input_file.read()


def read_file_from_absolute_path_to_file(absolute_path_to_file: str, file_format: Type[FileFormat]):
    if file_format == FileFormat.CSV:
        with open(absolute_path_to_file) as input_file:
            csv_reader = csv.reader(input_file, delimiter=',')
            return csv_reader
    elif file_format == FileFormat.JSON:
        with open(absolute_path_to_file) as input_file:
            input_obj = json.load(input_file)
            return input_obj
    elif file_format == FileFormat.XML:
        with open(absolute_path_to_file, 'r') as input_file:
            return input_file.read()


def read_setup(path):
    # net parameters
    with open(Path(path)) as setup_json:
        setup_obj = json.load(setup_json)
        return setup_obj


def select_from_distribution(distribution):
    p = random.random()
    min_value = 0
    for threshold, value in distribution:
        if min_value <= p <= threshold:
            return value
        min_value = threshold
    return select_from_list(distribution)[1]


def select_from_list(lst):
    lst_len = len(lst)
    if lst_len > 0:
        idx = random.randint(0, lst_len - 1)
        return lst[idx]
    return None


def encode_url(url: str):
    return url.replace("#","AST")


def decode_args(args):
    for k,v in args.items():
        if type(v) == str:
            args[k] = v.replace("AST","#")
    return args


def traci_api_call(command: ApiIdentifier, params: Dict[str,str] = {}) -> any:
    api_url = f"http://localhost:5000/traci?command={command.value}"
    if bool(params):
        for k, v in params.items():
            api_url += f"&{k}={v}"
    encoded_url = encode_url(api_url)
    response = requests.get(encoded_url)
    return response.json()[ApiIdentifier.DATA]


def sumo_net_api_call(command: ApiIdentifier, params: Dict[str,str] = {}) -> any:
    api_url = f"http://localhost:5000/sumo_net?command={command.value}"
    if bool(params):
        for k, v in params.items():
            api_url += f"&{k}={v}"
    encoded_url = encode_url(api_url)
    response = requests.get(encoded_url)
    return response.json()[ApiIdentifier.DATA]