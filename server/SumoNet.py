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
from sumolib.net import Net
from typing import Type

sumo_net: Type[Net] = None

class SumoNet(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(ApiIdentifier.COMMAND, required=True, type=str, location="args")
        parser.add_argument(ApiIdentifier.EDGE_ID, required=False, type=str, location="args")
        parser.add_argument(ApiIdentifier.SRC_EDGE_ID, required=False, type=str, location="args")
        parser.add_argument(ApiIdentifier.DST_EDGE_ID, required=False, type=str, location="args")
        args = parser.parse_args()
        command = args[ApiIdentifier.COMMAND]
        if command == ApiSimulator.GET_EDGE_LENGTH:
            edge_id = args[ApiIdentifier.EDGE_ID]
            edge = sumo_net.getEdge(edge_id)
            return {
                "data": edge.getLength()
            }, 200
        if command == ApiSimulator.GET_OPTIMAL_PATH:

        if command == ApiSimulator.GET_EDGE_OUTGOINGS:
            src_edge_id = args[ApiIdentifier.SRC_EDGE_ID]
            dst_edge_id = args[ApiIdentifier.DST_EDGE_ID]
            src_edge = sumo_net.getEdge(src_edge_id)
            dst_edge = sumo_net.getEdge(dst_edge_id)
            route, cost = sumo_net.getOptimalPath(src_edge, dst_edge)
            return {
                "data": edge.getOutgoing()
            }, 200
        if command == ApiSimulator.START_SUMO_NET:
            sumolib.net.readNet(FileSetup.NET_SUMO, withInternal=True)