# @file    runner.py
# @author  Davide
# @date    2021-04-30

from __future__ import absolute_import
from __future__ import print_function
from src.controller.Simulator_new import Simulator
from src.settings.Settings import Settings

env_settings = Settings()
TRACI_PORT = env_settings.TRACI_PORT


if __name__ == "__main__":
    print("SIMULATOR START")
    simulator = Simulator(TRACI_PORT)
    print(f"INIT SIMULATOR")
    #simulator.run()

# @file    runner.py
# @author  Davide
# @date    2021-04-30

"""
from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import optparse
from sumolib import checkBinary
import traci
import sumolib
from src.enum.setup.FileSetup import FileSetup
from src.enum.setup.Env import Env
from src.enum.identifiers.Config import Config as ConfigIdentifier
import multiprocessing
from src.utils import utils
import time
from src.controller.Simulator_new import Simulator


env_variables = {}
simulator_setup = utils.read_setup(FileSetup.SIMULATOR.value)

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME_BREW' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME_BREW'], 'tools')
    bin = os.path.join(os.environ['SUMO_HOME_BREW'], 'bin')
    sys.path.append(tools)
    sys.path.append(bin)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true", default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options

if __name__ == "__main__":
    # first, generate the route file for this simulation
    options = get_options()
    # If you want to run this tutorial please uncomment following lines, that define the sumoBinary
    # and delete the line before traci.start, to use the gui
    if options.nogui:
        sumo_binary = checkBinary('sumo')
    else:
        sumo_binary = checkBinary('sumo')
        #sumo_binary = checkBinary('sumo-gui')

    traci_port = 7000 #sumolib.miscutils.getFreeSocketPort()
    env_variables[Env.TRACI_PORT] = traci_port
    with open(FileSetup.ENV, 'w') as env_file:
        for k,v in env_variables.items():
            env_file.write(f"{k}={v}")

    print("TRACI START")
    traci.start([
        f"{sumo_binary}",
        "-c",
        "net_config/sumo.sumocfg",
        "--num-clients",
        f"{1}"
    ], port=traci_port, label="sim_1")



    print("SIMULATOR START")
    simulator = Simulator(traci_port, traci.getConnection("sim_1"))
    print(f"INIT SIMULATOR")"""

