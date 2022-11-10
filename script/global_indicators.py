from src.enum.setup.City import City
from src.enum.setup.FileFormat import FileFormat
from src.enum.setup.FileName import FileName
from src.enum.setup.Paths import Paths
from src.model.Scenario import Scenario
from src.settings.Settings import Settings
from src.utils import utils


env_settings = Settings()
CITY = City(env_settings.CITY)
SCENARIO = Scenario(env_settings.SCENARIO)

def global_indicators_to_json(
        tazs: list[list[str]],
        interval: int = 1
):
    input_absolute_path = utils.generate_absolute_path_to_file(
        Paths.SIM_OUTPUT,
        FileName.GLOBAL_INDICATORS,
        FileFormat.JSON,
        SCENARIO,
        CITY
    )
    g_i_dict = utils.read_file_from_absolute_path_to_file(
        input_absolute_path,
        FileFormat.JSON
    )
    header = ""
    content = ""
    indicators_list_dict = {}
    csv_rows = []
    keys = g_i_dict.keys()
    for k_idx, k in enumerate(keys):
        header += f"{k}," if (k_idx < (len(keys) - 1)) else f"{k}"
        g_i_k_dict = g_i_dict[k]
        timestamps = g_i_k_dict.keys()
        indicator_list = []
        for timestamp in range(interval, timestamps[-1]):
            indicator_sum = 0
            for taz_id in tazs:
                for i in range(timestamp-interval, timestamp):
                    indicator_sum += g_i_k_dict[i][taz_id]
            indicator_list.append(indicator_sum)
        indicators_list_dict[k] = indicator_list
    csv_rows = list(zip(*indicators_list_dict.values()))
    content += f"{header}\n"
    for row in csv_rows:
        content += f"{','.join(str(x) for x in row)}"
    output_absolute_path = utils.generate_absolute_path_to_file(
        Paths.SIM_OUTPUT,
        FileName.GLOBAL_INDICATORS,
        FileFormat.CSV,
        SCENARIO,
        CITY
    )
    utils.export_file_from_absolute_path(
        output_absolute_path,
        FileFormat.CSV,
        content
    )