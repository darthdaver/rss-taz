from src.enum.identifiers.Route import Route as RouteIdentifier
from src.enum.identifiers.Statistic import Statistic as StatisticIdentifier
from src.enum.identifiers.Ride import Ride as RideIdentifier
from src.enum.setup.City import City
from src.enum.setup.FileFormat import FileFormat
from src.enum.setup.FileName import FileName
from src.enum.setup.Paths import Paths
from src.enum.setup.Scenario import Scenario
from src.settings.Settings import Settings
from src.utils import utils


env_settings = Settings()
CITY = City(env_settings.CITY)
SCENARIO = Scenario(env_settings.SCENARIO)

def specific_indicators_to_json(
        tazs: list[list[str]],
        interval: int = 1
):
    input_absolute_path = utils.generate_absolute_path_to_file(
        Paths.SIM_OUTPUT,
        FileName.SPECIFIC_INDICATORS,
        FileFormat.JSON,
        SCENARIO,
        CITY
    )
    s_i_dict = utils.read_file_from_absolute_path_to_file(
        input_absolute_path,
        FileFormat.JSON
    )
    header = f"{StatisticIdentifier.TIMESTAMP.value}," \
             f"{StatisticIdentifier.DRIVERS_CANDIDATE.value}," \
             f"{StatisticIdentifier.REJECTIONS.value}," \
             f"{RideIdentifier.STAT_EXPECTED_MEETING_LENGTH}," \
             f"{RideIdentifier.STAT_EXPECTED_MEETING_TRAVEL_TIME}," \
             f"{RideIdentifier.STAT_MEETING_LENGTH}," \
             f"{RideIdentifier.STAT_MEETING_TRAVEL_TIME}," \
             f"{RideIdentifier.STAT_EXPECTED_RIDE_LENGTH}," \
             f"{RideIdentifier.STAT_EXPECTED_RIDE_TRAVEL_TIME}," \
             f"{RideIdentifier.STAT_RIDE_LENGTH}," \
             f"{RideIdentifier.STAT_RIDE_TRAVEL_TIME}," \
             f"{RideIdentifier.STAT_TIMESTAMP_REQUEST}," \
             f"{RideIdentifier.STAT_TIMESTAMP_PICKUP}," \
             f"{RideIdentifier.STAT_TIMESTAMP_ON_ROAD}," \
             f"{RideIdentifier.STAT_TIMESTAMP_END}," \
             f"{RideIdentifier.STAT_EXPECTED_PRICE}," \
             f"{RideIdentifier.STAT_PRICE}," \
             f"{RideIdentifier.STAT_SURGE_MULTIPLIER}\n"
    content = header

    timestamps = list(s_i_dict.keys())
    for timestamp in timestamps:
        s_i_timestamp_rides_list = s_i_dict[timestamp]
        if not s_i_timestamp_rides_list == []:
            for ride in s_i_timestamp_rides_list:
                content += f"{len(ride[RideIdentifier.REQUEST.value][StatisticIdentifier.DRIVERS_CANDIDATE.value])},"
                content += f"{len(ride[RideIdentifier.REQUEST.value][StatisticIdentifier.REJECTIONS.value])},"
                content += f"{round(ride[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_EXPECTED_MEETING_LENGTH.value], 2)},"
                content += f"{round(ride[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_EXPECTED_MEETING_TRAVEL_TIME.value], 2)},"
                content += f"{round(ride[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_MEETING_LENGTH.value], 2)},"
                content += f"{round(ride[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_MEETING_TRAVEL_TIME.value], 2)},"
                content += f"{round(ride[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_EXPECTED_RIDE_LENGTH.value], 2)},"
                content += f"{round(ride[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_EXPECTED_RIDE_TRAVEL_TIME.value], 2)},"
                content += f"{round(ride[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_RIDE_LENGTH.value], 2)},"
                content += f"{round(ride[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_RIDE_TRAVEL_TIME.value], 2)},"
                content += f"{round(ride[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_TIMESTAMP_REQUEST.value], 2)},"
                content += f"{round(ride[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_TIMESTAMP_PICKUP.value], 2)},"
                content += f"{round(ride[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_TIMESTAMP_ON_ROAD.value], 2)},"
                content += f"{round(ride[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_TIMESTAMP_END.value], 2)},"
                content += f"{round(ride[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_EXPECTED_PRICE.value], 2)},"
                content += f"{round(ride[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_PRICE.value], 2)},"
                content += f"{round(ride[RideIdentifier.RIDE_STATS.value][RideIdentifier.STAT_SURGE_MULTIPLIER.value], 2)}\n"
    output_absolute_path = utils.generate_absolute_path_to_file(
        Paths.SIM_OUTPUT,
        FileName.SPECIFIC_INDICATORS,
        FileFormat.CSV,
        SCENARIO,
        CITY
    )
    utils.export_file_from_absolute_path(
        output_absolute_path,
        FileFormat.CSV,
        content
    )

specific_indicators_to_json(
    ["po_0","po_1","po_2","po_3"],
    interval=1
)