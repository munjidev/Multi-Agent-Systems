from agent import Car_Agent, Traffic_Light_Agent, Destination_Agent, Building_Agent, Road_Agent, Car_Spawner_Agent
from model import RandomModel, roads, buildings, cars, traffic_lights, destinations, spawners
from mesa.visualization.modules import CanvasGrid, BarChartModule
from mesa.visualization.ModularVisualization import ModularServer

import math
from flask import Flask, request, jsonify

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| v MESA ||||||||||||||||||||||||||||||||||||

def agent_portrayal(agent):
    if agent is None: return
    
    portrayal = {"Shape": "rect",
                 "Filled": "true",
                 "Layer": 0,
                 "w": 1,
                 "h": 1
                 }

    if (isinstance(agent, Car_Agent)):
        portrayal["Shape"] = "circle"
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.5
    

    if (isinstance(agent, Road_Agent)):
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 0
    
    if (isinstance(agent, Destination_Agent)):
        portrayal["Color"] = "lightgreen"
        portrayal["Layer"] = 0
    
    if (isinstance(agent, Car_Spawner_Agent)):
        portrayal["Color"] = "yellow"
        portrayal["Layer"] = 0

    if (isinstance(agent, Traffic_Light_Agent)):
        portrayal["Color"] = "red" if not agent.state else "green"
        portrayal["Layer"] = 0
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8

    if (isinstance(agent, Building_Agent)):
        portrayal["Color"] = "cadetblue"
        portrayal["Layer"] = 0
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8

    return portrayal

width = 0
height = 0

with open('base.txt') as baseFile:
    lines = baseFile.readlines()
    width = len(lines[0])-1
    height = len(lines)

model_params = {"map_path":"Assets/Data/2022_base.txt"}

grid = CanvasGrid(agent_portrayal, width, height, 500, 500)

server = ModularServer(RandomModel, [grid], "Traffic Base", model_params)

server.port = 8521 # The default
server.launch()

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ^ MESA ||||||||| v UNITY |||||||||||||||||||||||||||||||||||||||||||||

# app = Flask("Traffic example")

# # @app.route('/', methods=['POST', 'GET'])

# @app.route('/init', methods=['POST', 'GET'])
# def initModel():
#     global currentStep, randomModel, number_agents, number_packages, number_depots, width, height

#     if request.method == 'POST':

#         map_path = request.form.get('MapPath')

#         currentStep = 0

#         randomModel = RandomModel(map_path)

#         return jsonify({"message":"Parameters recieved, model initiated."})

# @app.route('/getRoads', methods=['GET'])
# def getRoads():
#     global randomModel

#     if request.method == 'GET':
#         roadData = [{"id": str(road.unique_id), "x": road.pos[0], "y":0, "z": road.pos[1], "direction": road.direction} for road in roads.values()]
#         return jsonify({'data': roadData})

# @app.route('/getCars', methods=['GET'])
# def getCars():
#     global randomModel

#     if request.method == 'GET':
#         carData = [{"id": str(car.unique_id), "x": car.pos[0], "y":0, "z": car.pos[1], "in_traffic": car.in_traffic} for car in cars.values()]
#         return jsonify({'data': carData})

# @app.route('/getTLights', methods=['GET'])
# def getTLights():
#     global randomModel

#     if request.method == 'GET':
#         tlightData = [{"id": str(tlight.unique_id), "x": tlight.pos[0], "y":0, "z": tlight.pos[1], "state": tlight.state} for tlight in traffic_lights.values()]
#         return jsonify({'data': tlightData})

# @app.route('/getSpawners', methods=['GET'])
# def getSpawners():
#     global randomModel

#     if request.method == 'GET':
#         spawnerData = [{"id": str(spawner.unique_id), "x": spawner.pos[0], "y":0, "z": spawner.pos[1], "spawned":spawner.spawned} for spawner in spawners.values()]
#         return jsonify({'data':spawnerData})

# @app.route('/getDestinations', methods=['GET'])
# def getDestinations():
#     global randomModel

#     if request.method == 'GET':
#         destinationData = [{"id": str(destination.unique_id), "x": destination.pos[0], "y":0.01, "z": destination.pos[1], "arrivals": destination.arrivals} for destination in destinations.values()]
#         return jsonify({'data':destinationData})

# @app.route('/getBuildings', methods=['GET'])
# def getBuildings():
#     global randomModel

#     if request.method == 'GET':
#         buildingPositions = [{"id": str(building.unique_id), "x": building.pos[0], "y":0.01, "z": building.pos[1]} for building in buildings.values()]
#         return jsonify({'positions':buildingPositions})

# @app.route('/update', methods=['GET'])
# def updateModel():
#     global currentStep, randomModel
#     if request.method == 'GET':
#         randomModel.step()
#         currentStep += 1
#         return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

# if __name__=='__main__':
#     app.run(host="localhost", port=8585, debug=True)