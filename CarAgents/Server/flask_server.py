from agent import Car_Agent, Traffic_Light_Agent, Destination_Agent, Building_Agent, Road_Agent, Car_Spawner_Agent
from model import RandomModel, roads, buildings, cars, traffic_lights, destinations, spawners
from mesa.visualization.modules import CanvasGrid, BarChartModule
from mesa.visualization.ModularVisualization import ModularServer

import math
from flask import Flask, request, jsonify

app = Flask("Traffic example")

@app.route('/init', methods=['POST', 'GET'])
def initModel():
    global currentStep, randomModel, number_agents, number_packages, number_depots, width, height

    if request.method == 'POST':

        map_path = request.form.get('MapPath')

        currentStep = 0

        randomModel = RandomModel(map_path)

        return jsonify({"message":"Parameters recieved, model initiated."})

@app.route('/getRoads', methods=['GET'])
def getRoads():
    global randomModel

    if request.method == 'GET':
        roadData = [{"id": str(road.unique_id), "x": road.pos[0], "y":0, "z": road.pos[1], "direction": road.direction} for road in roads.values()]
        return jsonify({'data': roadData})

@app.route('/getCars', methods=['GET'])
def getCars():
    global randomModel

    if request.method == 'GET':
        carData = [{"id": str(car.unique_id), "x": car.pos[0], "y":0, "z": car.pos[1], "in_traffic": car.in_traffic, "at_destination": car.at_destination} for car in cars.values()]
        return jsonify({'data': carData})

@app.route('/getTLights', methods=['GET'])
def getTLights():
    global randomModel

    if request.method == 'GET':
        tlightData = [{"id": str(tlight.unique_id), "x": tlight.pos[0], "y":0, "z": tlight.pos[1], "state": tlight.state} for tlight in traffic_lights.values()]
        return jsonify({'data': tlightData})

@app.route('/getSpawners', methods=['GET'])
def getSpawners():
    global randomModel

    if request.method == 'GET':
        spawnerData = [{"id": str(spawner.unique_id), "x": spawner.pos[0], "y":0, "z": spawner.pos[1], "spawned":spawner.spawned} for spawner in spawners.values()]
        return jsonify({'data':spawnerData})

@app.route('/getDestinations', methods=['GET'])
def getDestinations():
    global randomModel

    if request.method == 'GET':
        destinationData = [{"id": str(destination.unique_id), "x": destination.pos[0], "y":0.01, "z": destination.pos[1], "arrivals": destination.arrivals} for destination in destinations.values()]
        print(destinationData)
        return jsonify({'data':destinationData})

@app.route('/getBuildings', methods=['GET'])
def getBuildings():
    global randomModel

    if request.method == 'GET':
        buildingPositions = [{"id": str(building.unique_id), "x": building.pos[0], "y":0.01, "z": building.pos[1]} for building in buildings.values()]
        return jsonify({'positions':buildingPositions})

@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, randomModel
    if request.method == 'GET':
        randomModel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=True)