# -*- coding: utf-8 -*-
"""
# TC2008B. Sistemas Multiagentes y Gráficas Computacionales
# server.py | 2022
# Salvador Federico Milanes Braniff
# Juan Muniain Otero
# Miguel Bustamante Perez
# Manuel Barrera Lopez Portillo

# Python flask server to interact with Unity. Based on the code provided by Sergio Ruiz.
# Octavio Navarro. October 2021
"""
from RandomAgents import RandomModel, RandomAgent, ObstacleAgent, PackageAgent, DepotAgent
from mesa.visualization.modules import CanvasGrid, BarChartModule, PieChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

import math
from flask import Flask, request, jsonify
from RandomAgents import *

# Size of the board:
number_agents = 10
number_packages = 17
width = 28
height = 28
randomModel = None
currentStep = 0

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| v MESA ||||||||||||||||||||||||||||||||||||

# def agent_portrayal(agent):
#     if agent is None: return
    
#     portrayal = {"Shape": "circle",
#                  "Filled": "true",
#                  "Layer": 1,
#                  "Color": "red",
#                  "r": 0.5}

#     if (isinstance(agent, ObstacleAgent)):
#         portrayal["Shape"] = "circle"
#         portrayal["Color"] = "gray"
#         portrayal["Layer"] = 1
#         portrayal["r"] = 1

#     if (isinstance(agent, PackageAgent)):
#         portrayal["Color"] = "brown"
#         portrayal["Layer"] = 0
#         portrayal["r"] = 0.6

#     if (isinstance(agent, DepotAgent)):
#         portrayal["Color"] = "blue"
#         portrayal["Layer"] = 1
#         portrayal["r"] = 0.8

#     return portrayal


# grid = CanvasGrid(agent_portrayal, 5, 5, 500, 500)

# server = ModularServer(RandomModel, [grid], "Random Agents",
# {
#     "N": UserSettableParameter('slider', 'Number of agents', 1, 1, 10, 1),
#     "P": UserSettableParameter('slider', 'Number of packages', 1, 1, 10, 1),
#     "D": UserSettableParameter('slider', 'Number of depots', 1, 1, 10, 1),
#     "width": 5, # UserSettableParameter('slider', 'Room Width', 10, 4, 100, 1),
#     "height": 5 # UserSettableParameter('slider', 'Room Height', 10, 4, 100, 1),
# })

# server.port = 8522 # The default
# server.launch()

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ^ MESA ||||||||| v UNITY |||||||||||||||||||||||||||||||||||||||||||||

app = Flask("Traffic example")

# @app.route('/', methods=['POST', 'GET'])

@app.route('/init', methods=['POST', 'GET'])
def initModel():
    global currentStep, randomModel, number_agents, number_packages, number_depots, width, height



    if request.method == 'POST':

        number_agents = int(request.form.get('NAgents'))
        number_packages = int(request.form.get('NPackages'))
        number_depots = int(math.ceil(number_packages/5))

        width = int(request.form.get('width'))
        height = int(request.form.get('height'))
        currentStep = 0

        # print(request.form)
        # print(number_agents, number_packages, number_depots, width, height)
        randomModel = RandomModel(number_agents, number_packages, number_depots, width, height)

        return jsonify({"message":"Parameters recieved, model initiated."})

@app.route('/getAgents', methods=['GET'])
def getAgents():
    global randomModel

    if request.method == 'GET':
        agentPositions = [{"id": str(a.unique_id), "x": x, "y":0, "z":z} for (a, x, z) in randomModel.grid.coord_iter() if isinstance(a, RandomAgent)]
        # read whether agent is carrying a package
        # agentStates = [{"id": str(a.unique_id), "hasPackage": a.hasPackage} for (a, x, z) in randomModel.grid.coord_iter() if isinstance(a, RandomAgent)]
        agentStates = [{"id": str(a.unique_id)} for (a, x, z) in randomModel.grid.coord_iter() if isinstance(a, RandomAgent)]

        return jsonify({'positions':agentPositions, "states":agentStates})

@app.route('/getPackages', methods=['GET'])
def getPackages():
    global randomModel

    if request.method == 'GET':
        packagePositions = [{"id": str(a.unique_id), "x": x, "y":0.3, "z":z} for (a, x, z) in randomModel.grid.coord_iter() if isinstance(a, PackageAgent)]
        
        return jsonify({'positions':packagePositions})

@app.route('/getDepots', methods=['GET'])
def getDepots():
    global randomModel

    if request.method == 'GET':
        depotData = [{"id": str(a.unique_id), "package_num": str(a.get_packages()), "x": x, "y":0.01, "z":z} for (a, x, z) in randomModel.grid.coord_iter() if isinstance(a, DepotAgent)]
        
        return jsonify({'data':depotData})

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