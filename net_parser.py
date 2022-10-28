import optparse
from typing import Type
from src.setup.NetParser import NetParser
from src.enum.types.NetType import NetType
from src.enum.setup.Dataset import Dataset
from src.enum.setup.FileFormat import FileFormat
from src.enum.setup.City import City
from src.utils import utils
from src.settings.Settings import Settings

env_settings = Settings()
CITY = City(env_settings.CITY)

if __name__ == "__main__":
    def get_options():
        optParser = optparse.OptionParser()
        optParser.add_option(
            "-i", "--input",
            action="store",
            type="string",
            dest="input",
            help="path to the lists of datasets-nets couples."
        )
        optParser.add_option(
            "-c", "--city",
            action="store",
            type="string",
            dest="city",
            help="city name."
        )
        optParser.add_option(
            "-n", "--net_path",
            action="store",
            type="string",
            dest="net_path",
            help="net path."
        )
        options, args = optParser.parse_args()
        return options

    def parse_input_file(file_path: str):
        net_datasets_types = []
        file_content = utils.read_file_from_absolute_path_to_file(file_path, FileFormat.JSON)
        for dataset_str, net_type_str in file_content:
            net_datasets_types.append((
                Dataset(dataset_str),
                NetType(net_type_str)
            ))
        return net_datasets_types

    options = get_options()
    if (options.input is not None) and (options.city is not None) and (options.net_path is not None):
        net_datasets_types = parse_input_file(options.input)
        net = options.net_path
        net_parser: Type[NetParser] = NetParser(
            net,
            net_datasets_types,
            CITY
        )
        net_parser.collect_edges()
        net_parser.parse_taz_edges()
        net_parser.export_net()