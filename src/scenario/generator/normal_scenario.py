from src.enum.identifiers.Scenario import Scenario as ScenarioIdentifier
from src.enum.setup.City import City
from src.enum.setup.FileFormat import FileFormat
from src.enum.setup.FileName import FileName
from src.enum.setup.Paths import Paths
from src.enum.setup.Scenario import Scenario
from src.types.Scenario import ScenarioNormalParams
from src.utils import utils


def normal_scenario(params: ScenarioNormalParams):
    city = params[ScenarioIdentifier.CITY.value]
    scenario_dict = {
        ScenarioIdentifier.NAME.value: Scenario.NORMAL.value,
        ScenarioIdentifier.MOBILITY_PLANNER.value: [],
        ScenarioIdentifier.SIMULATION_PLANNER.value: []
    }
    output_absolute_path = utils.generate_absolute_path_to_file(
        Paths.SCENARIO,
        FileName.SCENARIO_PLANNER,
        FileFormat.JSON,
        Scenario.NORMAL,
        city
    )
    utils.export_file_from_absolute_path(
        output_absolute_path,
        FileFormat.JSON,
        scenario_dict
    )