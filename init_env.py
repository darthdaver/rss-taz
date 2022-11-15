from src.enum.setup.Env import Env
import sumolib

if __name__ == "__main__":
    env_variables = {}
    traci_port = sumolib.miscutils.getFreeSocketPort()
    env_variables[Env.TRACI_PORT.value] = traci_port
    env_variables[Env.CITY.value] = str(input("City: "))
    env_variables[Env.DATASET_PICKUPS.value] = str(input("Dataset pickups: "))
    env_variables[Env.DATASET_TRAVEL_TIMES.value] = str(input("Dataset travel_times: "))
    env_variables[Env.NET_SUMO.value] = str(input("Sumo net name: "))
    env_variables[Env.SCENARIO.value] = str(input("Scenario type: "))
    env_variables[Env.BEGIN.value] = str(input("Begin Simulation Timestamp: "))
    env_variables[Env.END.value] = str(input("END Simulation Timestamp: "))
    with open('.env', 'w') as env_file:
        for k,v in env_variables.items():
            env_file.write(f"{k}={v}\n")