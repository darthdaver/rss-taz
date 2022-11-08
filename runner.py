# @file    runner.py
# @author  Davide
# @date    2021-04-30

from __future__ import absolute_import
from __future__ import print_function
from src.controller.Simulator import Simulator
import os
import sys
import optparse
import traci
from sumolib import checkBinary
from src.settings.Settings import Settings
from src.enum.setup.City import City

env_settings = Settings()
TRACI_PORT = env_settings.TRACI_PORT
CITY = City(env_settings.CITY)

if __name__ == "__main__":
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        bin = os.path.join(os.environ['SUMO_HOME'], 'bin')
        sys.path.append(tools)
        sys.path.append(bin)
    else:
        sys.exit("please declare environment variable 'SUMO_HOME'")

    def get_options():
        optParser = optparse.OptionParser()
        optParser.add_option("--nogui", action="store_true", default=False, help="run the commandline version of sumo")
        options, args = optParser.parse_args()
        return options

    # first, generate the route file for this simulation
    options = get_options()
    # If you want to run this tutorial please uncomment following lines, that define the sumoBinary
    # and delete the line before traci.start, to use the gui
    if options.nogui:
        sumo_binary = checkBinary('sumo')
    else:
        sumo_binary = checkBinary('sumo-gui')

    print("TRACI START")

    traci.start(
        [
            f"{sumo_binary}",
            "-c",
            "net_config/sumo.sumocfg"
        ],
        label="sim_1",
        port=TRACI_PORT
    )

    print("SIMULATOR START")
    simulator = Simulator(
        CITY
    )
    print(f"INIT SIMULATOR")
    simulator.run()