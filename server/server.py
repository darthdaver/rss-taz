from __future__ import absolute_import
from __future__ import print_function
from flask import Flask
from flask_restful import Api
from server.Traci import Traci
from server.SumoNet import SumoNet
import sumolib
from src.enum.setup.FileSetup import FileSetup

app = Flask(__name__)
api = Api(app)

sumo_net = sumolib.net.readNet(FileSetup.NET_SUMO, withInternal=True)

api.add_resource(Traci, '/traci')
api.add_resource(SumoNet, '/sumo_net', resource_class_kwargs={ 'sumo_net': sumo_net })

app.run()