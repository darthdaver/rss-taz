from src.enum.identifiers.Api import Api as ApiIdentifier
from src.enum.api.Api import Api as ApiSimulator
from flask_restful import Resource, Api, reqparse
from src.enum.setup.FileSetup import FileSetup
import sumolib
from sumolib.net import Net
from typing import Type
from src.model.Net import Net
from src.utils import utils

sumo_net: Type[Net] = None

class SumoNet(Resource):
    def __init__(self, sumo_net):
        self.sumo_net: Type[Net] = sumo_net

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(ApiIdentifier.COMMAND, required=True, type=str, location="args")
        parser.add_argument(ApiIdentifier.EDGE_ID, required=False, type=str, location="args")
        parser.add_argument(ApiIdentifier.SRC_EDGE_ID, required=False, type=str, location="args")
        parser.add_argument(ApiIdentifier.DST_EDGE_ID, required=False, type=str, location="args")
        parser.add_argument(ApiIdentifier.VEHICLE_CLASS, required=False, type=str, location="args")
        parser.add_argument(ApiIdentifier.LANE_NUM, required=False, type=int, location="args")
        parser.add_argument(ApiIdentifier.ROUTE_STR, required=False, type=str, location="args")
        args = utils.decode_args(parser.parse_args())

        command = args[ApiIdentifier.COMMAND]
        if command == ApiSimulator.CHECK_EDGE_ALLOWS_VEHICLE:
            edge_id = args[ApiIdentifier.EDGE_ID]
            vehicle_class = args[ApiIdentifier.VEHICLE_CLASS]
            edge = self.sumo_net.getEdge(edge_id)
            return {
               ApiIdentifier.DATA.value: edge.allows(vehicle_class)
            }, 200
        if command == ApiSimulator.GET_EDGES:
            sumo_edges = self.__self.sumo_net.getEdges()
            sumo_edges_ids = list(map(lambda e: e.getID(), sumo_edges))
            return {
                ApiIdentifier.DATA.value: sumo_edges_ids
            }, 200
        if command == ApiSimulator.GET_EDGE_LENGTH:
            edge_id = args[ApiIdentifier.EDGE_ID]
            edge = self.sumo_net.getEdge(edge_id)
            return {
                ApiIdentifier.DATA.value: edge.getLength()
            }, 200
        if command == ApiSimulator.GET_EDGE_LANE_ID:
            edge_id = args[ApiIdentifier.EDGE_ID]
            lane_num = args[ApiIdentifier.LANE_NUM]
            edge = self.sumo_net.getEdge(edge_id)
            return {
                ApiIdentifier.DATA.value: edge.getLanes()[lane_num].getID()
            }, 200
        if command == ApiSimulator.GET_OPTIMAL_PATH:
            src_edge_id = args[ApiIdentifier.SRC_EDGE_ID]
            dst_edge_id = args[ApiIdentifier.DST_EDGE_ID]
            src_edge = self.sumo_net.getEdge(src_edge_id)
            dst_edge = self.sumo_net.getEdge(dst_edge_id)
            route, cost = self.sumo_net.getOptimalPath(src_edge, dst_edge)
            route_edge_id_list = Net.convert_route_to_edge_id_list(route)
            return {
               ApiIdentifier.DATA.value: [
                   route_edge_id_list,
                   cost
               ]
            }, 200
        if command == ApiSimulator.GET_ROUTE_LENGTH:
            route_edge_id_list = args[ApiIdentifier.ROUTE_STR].split(ApiIdentifier.SEPARATOR.value)
            return {
                ApiIdentifier.DATA.value: sumolib.route.getLength(self.sumo_net, route_edge_id_list)
            }
        if command == ApiSimulator.GET_EDGE_OUTGOINGS:
            edge_id = args[ApiIdentifier.EDGE_ID]
            edge = self.sumo_net.getEdge(edge_id)
            edge_outgoings = list(map(lambda e: e.getID(), edge.getOutgoing()))
            return {
                ApiIdentifier.DATA.value: edge_outgoings
            }, 200
        if command == ApiSimulator.HAS_EDGE:
            edge_id = args[ApiIdentifier.EDGE_ID]
            return {
                ApiIdentifier.DATA.value: self.sumo_net.hasEdge(edge_id)
            }
        if command == ApiSimulator.START_SUMO_NET:
            self.sumo_net = sumolib.net.readNet(FileSetup.NET_SUMO, withInternal=True)