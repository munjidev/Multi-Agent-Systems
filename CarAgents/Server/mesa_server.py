from agent import Car_Agent, Traffic_Light_Agent, Destination_Agent, Building_Agent, Road_Agent, Car_Spawner_Agent
from model import RandomModel, roads, buildings, cars, traffic_lights, destinations, spawners
from mesa.visualization.modules import CanvasGrid, BarChartModule
from mesa.visualization.ModularVisualization import ModularServer

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
        portrayal["Layer"] = 1
    
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