from agent import Car_Agent, Traffic_Light_Agent, Destination_Agent, Obstacle_Agent, Road_Agent, Car_Spawner_Agent, agents, destinations, spawners
from model import RandomModel
from mesa.visualization.modules import CanvasGrid, BarChartModule
from mesa.visualization.ModularVisualization import ModularServer

import math
from flask import Flask, request, jsonify

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| v MESA ||||||||||||||||||||||||||||||||||||

# def agent_portrayal(agent):
#     if agent is None: return
    
#     portrayal = {"Shape": "rect",
#                  "Filled": "true",
#                  "Layer": 0,
#                  "w": 1,
#                  "h": 1
#                  }

#     if (isinstance(agent, Car_Agent)):
#         portrayal["Shape"] = "circle"
#         portrayal["Color"] = "blue"
#         portrayal["Layer"] = 1
#         portrayal["r"] = 0.5
    

#     if (isinstance(agent, Road_Agent)):
#         portrayal["Color"] = "grey"
#         portrayal["Layer"] = 0
    
#     if (isinstance(agent, Destination_Agent)):
#         portrayal["Color"] = "lightgreen"
#         portrayal["Layer"] = 0
    
#     if (isinstance(agent, Car_Spawner_Agent)):
#         portrayal["Color"] = "yellow"
#         portrayal["Layer"] = 0

#     if (isinstance(agent, Traffic_Light_Agent)):
#         portrayal["Color"] = "red" if not agent.state else "green"
#         portrayal["Layer"] = 0
#         portrayal["w"] = 0.8
#         portrayal["h"] = 0.8

#     if (isinstance(agent, Obstacle_Agent)):
#         portrayal["Color"] = "cadetblue"
#         portrayal["Layer"] = 0
#         portrayal["w"] = 0.8
#         portrayal["h"] = 0.8

#     return portrayal

# width = 0
# height = 0

# with open('base.txt') as baseFile:
#     lines = baseFile.readlines()
#     width = len(lines[0])-1
#     height = len(lines)

# model_params = {"N":5}

# grid = CanvasGrid(agent_portrayal, width, height, 500, 500)

# server = ModularServer(RandomModel, [grid], "Traffic Base", model_params)

# server.port = 8521 # The default
# server.launch()

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ^ MESA ||||||||| v UNITY |||||||||||||||||||||||||||||||||||||||||||||

app = Flask("Traffic example")

# @app.route('/', methods=['POST', 'GET'])

@app.route('/init', methods=['POST', 'GET'])
def initModel():
    global currentStep, randomModel, number_agents, number_packages, number_depots, width, height



    if request.method == 'POST':

        number_agents = int(request.form.get('NCars'))

        width = int(request.form.get('width'))
        height = int(request.form.get('height'))
        currentStep = 0

        randomModel = RandomModel(number_agents, width, height)

        return jsonify({"message":"Parameters recieved, model initiated."})

@app.route('/getCars', methods=['GET'])
def getCars():
    global randomModel

    if request.method == 'GET':
        agentData = [{"id": str(agent.unique_id), "x": agent.pos[0], "y":0, "z": agent.pos[1], "in_traffic": agent.has_package} for agent in agents.values()]
        return jsonify({'data': agentData})

@app.route('/getSpawners', methods=['GET'])
def getSpawners():
    global randomModel

    if request.method == 'GET':
        # Get all packages and build a list of dictionaries with their id, position and state
        packageData = [{"id": str(spawner.unique_id), "x": spawner.x, "y": 0.3, "z":spawner.y, "spawned": spawner.spawned} for spawner in spawners.values()]
        return jsonify({'data':packageData})

@app.route('/getDestinations', methods=['GET'])
def getDestinations():
    global randomModel

    if request.method == 'GET':
        # Get depot positions and package amounts from the global depot dictionary
        destinationData = [{"id": str(destination.unique_id), "x": destination.x, "y":0.01, "z": destination.y, "package_num": destiantion.arrivals} for destination in destiantions.values()]
        return jsonify({'data':destinationData})

@app.route('/getObstacles', methods=['GET'])
def getObstacles():
    global randomModel

    if request.method == 'GET':
        carPositions = [{"id": str(a.unique_id), "x": x, "y":0.5, "z":z} for (a, x, z) in randomModel.grid.coord_iter() if isinstance(a, ObstacleAgent)]

        return jsonify({'positions':carPositions})

@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, randomModel
    if request.method == 'GET':
        randomModel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=True)