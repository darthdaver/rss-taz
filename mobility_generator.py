import optparse
from src.setup.MobilityGenerator import MobilityGenerator
from src.enum.setup.Dataset import Dataset
from src.enum.setup.City import City
from src.settings.Settings import Settings

env_settings = Settings()

CITY = City(env_settings.CITY)
DATASET_PICKUPS = Dataset(env_settings.DATASET_PICKUPS)
DATASET_TRAVEL_TIMES = Dataset(env_settings.DATASET_TRAVEL_TIMES)

if __name__ == "__main__":
    def get_options():
        optParser = optparse.OptionParser()
        optParser.add_option(
            "-b", "--begin",
            action="store",
            type="int",
            dest="begin",
            help="Begin simulation timestamp."
        )
        optParser.add_option(
            "-e", "--end",
            action="store",
            type="int",
            dest="end",
            help="End simulation timestamp."
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

    options = get_options()
    if (options.begin is not None) and (options.end is not None) and (options.net_path is not None):
        net = options.net_path
        begin = options.begin
        end = options.end
        mobility_generator = MobilityGenerator(
            net,
            CITY,
            DATASET_PICKUPS,
            DATASET_TRAVEL_TIMES,
            begin,
            end
        )
        mobility_generator.generate_mobility()