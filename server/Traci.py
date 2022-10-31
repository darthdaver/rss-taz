import os
import sys
import optparse
import traci
from sumolib import checkBinary
from src.enum.identifiers.Api import Api as ApiIdentifier
from src.enum.api.Api import Api as ApiSimulator
from flask_restful import Resource, Api, reqparse
from src.enum.setup.FileSetup import FileSetup
from src.enum.setup.Env import Env
from src.utils import utils
import sumolib

env_variables = {}

def start_traci():
    # we need to import python modules from the $SUMO_HOME/tools directory
    if 'SUMO_HOME_BREW' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME_BREW'], 'tools')
        bin = os.path.join(os.environ['SUMO_HOME_BREW'], 'bin')
        sys.path.append(tools)
        sys.path.append(bin)
    else:
        sys.exit("please declare environment variable 'SUMO_HOME_BREW'")

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
        sumo_binary = checkBinary('sumo')
        #sumo_binary = checkBinary('sumo-gui')

    traci_port = sumolib.miscutils.getFreeSocketPort()
    env_variables[Env.TRACI_PORT] = traci_port
    with open(FileSetup.ENV, 'w') as env_file:
        for k,v in env_variables.items():
            env_file.write(f"{k}={v}")

    print("TRACI START")
    traci.start(
        [
            f"{sumo_binary}",
            "-c",
            "net_config/sumo.sumocfg"
        ],
        label="sim_1",
        port=traci_port
    )

class Traci(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(ApiIdentifier.COMMAND, required=True, type=str, location="args")
        parser.add_argument(ApiIdentifier.CUSTOMER_ID, required=False, type=str, location="args")
        parser.add_argument(ApiIdentifier.DRIVER_ID, required=False, type=str, location="args")
        parser.add_argument(ApiIdentifier.DST_EDGE_ID, required=False, type=str, location="args")
        parser.add_argument(ApiIdentifier.POS, required=False, type=float, location="args")
        parser.add_argument(ApiIdentifier.DURATION, required=False, type=float, location="args")
        parser.add_argument(ApiIdentifier.FLAGS, required=False, type=int, location="args")
        parser.add_argument(ApiIdentifier.ROUTE_ID, required=False, type=str, location="args")
        parser.add_argument(ApiIdentifier.STAGE_NUM, required=False, type=int, location="args")
        parser.add_argument(ApiIdentifier.ROUTE_STR, required=False, type=str, location="args")
        args = utils.decode_args(parser.parse_args())
        command = args[ApiIdentifier.COMMAND]
        print(args)
        if command == ApiSimulator.ADD_ROUTE:
            route_id = args[ApiIdentifier.ROUTE_ID]
            route_edge_id_list = args[ApiIdentifier.ROUTE_STR].split(ApiIdentifier.SEPARATOR.value)
            result = ApiIdentifier.OK.value
            try:
                traci.route.add(route_id, route_edge_id_list)
            except:
                result = ApiIdentifier.KO.value
            return {
               ApiIdentifier.DATA.value: result
            }, 200
        if command == ApiSimulator.APPEND_STAGE:
            stage = args[ApiIdentifier.STAGE]
            if stage == ApiIdentifier.DRIVING_STAGE.value:
                customer_id = args[ApiIdentifier.CUSTOMER_ID]
                dst_edge_id = args[ApiIdentifier.DST_EDGE_ID]
                driver_id = args[ApiIdentifier.DRIVER_ID]
                traci.person.appendDrivingStage(customer_id, dst_edge_id, driver_id)
            elif stage == ApiIdentifier.WAITING_STAGE.value:
                customer_id = args[ApiIdentifier.CUSTOMER_ID]
                duration = args[ApiIdentifier.DURATION]
                traci.person.appendWaitingStage(customer_id, duration)
            return {
                ApiIdentifier.DATA.value: ApiIdentifier.OK.value
            }, 200
        if command == ApiSimulator.CLOSE_TRACI:
            traci.close(False)
        if command == ApiSimulator.CUSTOMER_CURRENT_EDGE_ID:
            customer_id = args[ApiIdentifier.CUSTOMER_ID]
            return {
                ApiIdentifier.DATA.value: traci.person.getRoadID(customer_id)
            }, 200
        if command == ApiSimulator.CUSTOMER_CURRENT_POS:
            customer_id = args[ApiIdentifier.CUSTOMER_ID]
            return {
                ApiIdentifier.DATA.value: traci.person.getLanePosition(customer_id)
            }, 200
        if command == ApiSimulator.CUSTOMER_GET_EDGES:
            customer_id = args[ApiIdentifier.CUSTOMER_ID]
            return{
                ApiIdentifier.DATA.value: traci.person.getEdges(customer_id)
            }
        if command == ApiSimulator.CUSTOMERS_ID_LIST:
            return {
               ApiIdentifier.DATA.value: traci.person.getIDList()
            }, 200
        if command == ApiSimulator.DRIVERS_ID_LIST:
            return {
               ApiIdentifier.DATA.value: traci.vehicle.getIDList()
            }, 200
        if command == ApiSimulator.DRIVER_CURRENT_EDGE_ID:
            driver_id = args[ApiIdentifier.DRIVER_ID]
            return {
                ApiIdentifier.DATA.value: traci.vehicle.getRoadID(driver_id)
            }, 200
        if command == ApiSimulator.DRIVER_CURRENT_POS:
            customer_id = args[ApiIdentifier.CUSTOMER_ID]
            return {
                ApiIdentifier.DATA.value: traci.vehicle.getLanePosition(customer_id)
            }, 200
        if command == ApiSimulator.DRIVING_DISTANCE:
            driver_id = args[ApiIdentifier.DRIVER_ID]
            dst_edge_id = args[ApiIdentifier.DST_EDGE_ID]
            dst_pos = args[ApiIdentifier.DST_POS]
            return {
                ApiIdentifier.DATA.value: traci.vehicle.getDrivingDistance(driver_id, dst_edge_id, dst_pos)
            }, 200
        if command == ApiSimulator.GET_PERSON_NUMBER:
            driver_id = args[ApiIdentifier.DRIVER_ID]
            return {
                ApiIdentifier.DATA.value: traci.vehicle.getPersonNumber(driver_id)
            }
        if command == ApiSimulator.GET_ROUTE_INDEX:
            driver_id = args[ApiIdentifier.DRIVER_ID]
            return {
                ApiIdentifier.DATA.value: traci.vehicle.getRouteIndex(driver_id)
            }
        if command == ApiSimulator.REMOVE_CUSTOMER:
            customer_id = args[ApiIdentifier.CUSTOMER_ID]
            traci.person.remove(customer_id)
            return {
               ApiIdentifier.DATA.value: ApiIdentifier.OK.value
            }, 200
        if command == ApiSimulator.REMOVE_DRIVER:
            driver_id = args[ApiIdentifier.DRIVER_ID]
            print(traci.vehicle.getIDList())
            traci.vehicle.remove(driver_id)
            return {
               ApiIdentifier.DATA.value: ApiIdentifier.OK.value
            }, 200
        if command == ApiSimulator.REMOVE_CUSTOMER_STAGE:
            customer_id = args[ApiIdentifier.CUSTOMER_ID]
            stage_num = args[ApiIdentifier.STAGE_NUM]
            traci.person.removeStage(customer_id, stage_num)
            return {
               ApiIdentifier.DATA.value: ApiIdentifier.OK.value
            }, 200
        if command == ApiSimulator.ROUTE_ID_LIST:
            return {
               ApiIdentifier.DATA.value: traci.route.getIDList()
            }, 200
        if command == ApiSimulator.SET_ROUTE_ID:
            driver_id = args[ApiIdentifier.DRIVER_ID]
            route_id = args[ApiIdentifier.ROUTE_ID]
            traci.vehicle.setRouteID(driver_id, route_id)
            return {
                ApiIdentifier.DATA.value: ApiIdentifier.OK.value
            }, 200
        if command == ApiSimulator.SET_STOP:
            driver_id = args[ApiIdentifier.DRIVER_ID]
            dst_edge_id = args[ApiIdentifier.DST_EDGE_ID]
            stop_pos = args[ApiIdentifier.POS]
            duration = args[ApiIdentifier.DURATION]
            flags = args[ApiIdentifier.FLAGS]
            traci.vehicle.setStop(driver_id, dst_edge_id, stop_pos, duration=duration, flags=flags)
            return {
                ApiIdentifier.DATA.value: ApiIdentifier.OK.value
            }, 200
        if command == ApiSimulator.SIMULATION_STEP:
            traci.simulationStep()
            return {
               ApiIdentifier.DATA.value: ApiIdentifier.OK.value
            }, 200
        if command == ApiSimulator.SIMULATION_TIME:
            simulation_time = traci.simulation.getTime()
            return {
                ApiIdentifier.DATA.value: simulation_time
            }, 200
        if command == ApiSimulator.START_TRACI:
            start_traci()
            return {
                ApiIdentifier.DATA.value: ApiIdentifier.OK.value
            }, 200