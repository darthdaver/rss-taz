import optparse
from typing import Type

from script import scenario
from src.enum.setup.Scenario import Scenario
from src.setup.NetParser import NetParser
from src.enum.types.NetType import NetType
from src.enum.setup.Dataset import Dataset
from src.enum.setup.FileFormat import FileFormat
from src.enum.setup.City import City
from src.utils import utils
from src.settings.Settings import Settings

env_settings = Settings()
CITY = City(env_settings.CITY)
SCENARIO = Scenario(env_settings.SCENARIO)


if __name__ == "__main__":
    if SCENARIO == Scenario.NORMAL:
        scenario.normal_scenario(CITY)
    elif SCENARIO == Scenario.DRIVER_STRIKE:
        scenario.driver_strike_scenario(
            CITY, [])
