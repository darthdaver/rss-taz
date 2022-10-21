from __future__ import absolute_import
from __future__ import print_function
from flask import Flask
from flask_restful import Api
import Traci
import SumoNet

app = Flask(__name__)
api = Api(app)


api.add_resource(Traci, '/traci')
api.add_resource(SumoNet, '/sumo_net')

app.run()