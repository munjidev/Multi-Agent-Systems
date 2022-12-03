/*
TC2008B. Sistemas Multiagentes y Gráficas Computacionales
AgentController.cs | 2022
Salvador Federico Milanes Braniff
Juan Muniain Otero
Miguel Bustamante Perez
Manuel Barrera Lopez Portillo

Script to control the agents in the scene.
*/

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

//CLASSES OF DISCRETE AGENT TYPES AND ATTRIBUTES |||||||||||||||||||||||||||||||||||||||||||||||
[Serializable]
public class AgentData
{
    //Class for an Agent: Contains the agent's id and position.
    public string id;
    public float x, y, z;

    public AgentData(string id, float x, float y, float z)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
    }
}

[Serializable]
public class RoadData : AgentData
{
    //Class for a Road: Inherits from AgentData and adds the road's direction.
    public string direction;

    public RoadData(string id, float x, float y, float z, string direction) : base(id, x, y, z)
    {
        this.direction = direction;
    }
}

[Serializable]
public class CarData : AgentData
{
    //Class for a Car: Inherits from AgentData and adds the car-in-traffic state.
    public bool in_traffic;

    public CarData(string id, float x, float y, float z, bool in_traffic) : base(id, x, y, z)
    {
        this.in_traffic = in_traffic;
    }
}

[Serializable]
public class TrafficLightData : AgentData
{
    //Class for a Traffic Light: Inherits from AgentData and adds the traffic light's state.
    public bool state;

    public TrafficLightData(string id, float x, float y, float z, bool state) : base(id, x, y, z)
    {
        this.state = state;
    }
}

[Serializable]
public class DestinationData : AgentData
{
    //Class for a Destination: Inherits from AgentData and adds the destination's arrival count.
    public int arrivals;

    public DestinationData(string id, float x, float y, float z, int arrivals) : base(id, x, y, z)
    {
        this.arrivals = arrivals;
    }
}

[Serializable]
public class SpawnerData : AgentData
{
    //Class for a Destination: Inherits from AgentData and adds the spawner's spawn count.
    public int spawned;

    public SpawnerData(string id, float x, float y, float z, int spawned) : base(id, x, y, z)
    {
        this.spawned = spawned;
    }
}

// CLASSES OF LISTS OF AGENTS: CARS, DESTINATIONS AND SPAWNERS |||||||||||||||||||||||||||||||||||||||||||||||
[Serializable]
public class AgentsData
{
    public List<AgentData> positions;

    public AgentsData() => this.positions = new List<AgentData>();
}

[Serializable]
public class RoadsData
{
    public List<RoadData> data;

    public RoadsData() => this.data = new List<RoadData>();
}

[Serializable]
public class CarsData
{
    public List<CarData> data;

    public CarsData() => this.data = new List<CarData>();
}

[Serializable]
public class TrafficLightsData
{
    public List<TrafficLightData> data;

    public TrafficLightsData() => this.data = new List<TrafficLightData>();
}
[Serializable]
public class DestinationsData
{
    public List<DestinationData> data;

    public DestinationsData() => this.data = new List<DestinationData>();
}

[Serializable]
public class SpawnersData
{
    public List<SpawnerData> data;

    public SpawnersData() => this.data = new List<SpawnerData>();
}


public class AgentController : MonoBehaviour
{
    // private string url = "https://agents.us-south.cf.appdomain.cloud/";
    string serverUrl = "http://localhost:8585";
    string getRoadsEndpoint = "/getRoads";
    string getCarsEndpoint = "/getCars";
    string getTLightsEndpoint = "/getTLights";
    string getBuildingsEndpoint = "/getBuildings";
    string getDestinationsEndpoint = "/getDestinations";
    string getSpawnersEndpoint = "/getSpawners";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";

    RoadsData roadsData;
    CarsData carsData;
    TrafficLightsData tLightsData;
    AgentsData buildingsData;
    DestinationsData destinationsData;
    SpawnersData spawnersData;
    Dictionary<string, GameObject> roads, cars, tLights, destinations, spawners;
    Dictionary<string, Vector3> prevPositions, currPositions;

    bool updated = false, roadsStarted = false, carsStarted = false, tLightsStarted = false, destinationsStarted = false, spawnersStarted = false;

    public GameObject roadPrefab, tLightPrefab, destinationPrefab, spawnerPrefab;

    public GameObject[] carPrefabVariants, buildingPrefabVariants;

    public string MapPath = "Assets/Data/2022_base.txt";

    public float timeToUpdate = 5.0f;

    private float timer, dt;

    private int carsSpawned, arrivals;

    void Start()
    {
        roadsData = new RoadsData();
        carsData = new CarsData();
        tLightsData = new TrafficLightsData();
        buildingsData = new AgentsData();
        destinationsData = new DestinationsData();
        spawnersData = new SpawnersData();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        roads = new Dictionary<string, GameObject>();
        cars = new Dictionary<string, GameObject>();
        tLights = new Dictionary<string, GameObject>();
        destinations = new Dictionary<string, GameObject>();
        spawners = new Dictionary<string, GameObject>();

        timer = timeToUpdate;

        StartCoroutine(SendConfiguration());
    }

    private void Update()
    {
        if(timer < 0)
        {
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(UpdateSimulation());
        }

        if (updated)
        {
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            foreach(var car in currPositions)
            {
                Vector3 currentPosition = car.Value;
                Vector3 previousPosition = prevPositions[car.Key];

                Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);
                Vector3 direction = currentPosition - interpolated;

                cars[car.Key].transform.localPosition = interpolated;
                if(direction != Vector3.zero) cars[car.Key].transform.rotation = Quaternion.LookRotation(direction);
            }
        }
    }
 
    IEnumerator UpdateSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            StartCoroutine(GetCarsData());
            StartCoroutine(GetTLightsData());
            StartCoroutine(GetDestinationsData());
            StartCoroutine(GetSpawnersData());
        }
    }
    IEnumerator SendConfiguration()
    {
        WWWForm form = new WWWForm();

        form.AddField("MapPath", MapPath.ToString());

        UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            // Debug.Log("Configuration upload complete!");
            StartCoroutine(GetRoadsData());
            StartCoroutine(GetBuildingsData());
            // Debug.Log("Getting Agents positions");
            StartCoroutine(GetCarsData());
            // Debug.Log("Getting Spawner and Destination information");
            StartCoroutine(GetTLightsData());
            StartCoroutine(GetDestinationsData());
            StartCoroutine(GetSpawnersData());
        }
    }
    IEnumerator GetRoadsData()
    {
        // Debug.Log("Getting Roads");
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getRoadsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else 
        {
            roadsData = JsonUtility.FromJson<RoadsData>(www.downloadHandler.text);
            // Debug.Log(www.downloadHandler.text);

            foreach (RoadData road in roadsData.data)
            {
                if(!roadsStarted)
                {
                    roads[road.id] = Instantiate(roadPrefab, new Vector3(road.x, road.y, road.z), Quaternion.identity);
                    //Apply rotation to the road depending on the direction
                    if(road.direction == "Up" || road.direction == "Down")
                    {
                        roads[road.id].transform.Rotate(0, 90, 0);
                    }
                }
            }
            updated = true;
            if(!roadsStarted) roadsStarted = true;
        }
    }
    IEnumerator GetCarsData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getCarsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            carsSpawned = 0;
            carsData = JsonUtility.FromJson<CarsData>(www.downloadHandler.text);

            // Update the positions of the agents
            foreach(CarData car in carsData.data)
            {
                Vector3 newCarPosition = new Vector3(car.x, car.y, car.z);

                if(!carsStarted)
                {
                    prevPositions[car.id] = newCarPosition;
                    // Choose a random car prefab variant and add it to the scene
                    GameObject carPrefab = carPrefabVariants[UnityEngine.Random.Range(0, carPrefabVariants.Length)];
                    cars[car.id] = Instantiate(carPrefab, newCarPosition, Quaternion.identity);
                }
                else
                {
                    Vector3 currentPosition = new Vector3();
                    //Check if new cars are present in scene, if not, add them
                    if(!cars.ContainsKey(car.id))
                    {
                        prevPositions[car.id] = newCarPosition;
                        GameObject carPrefab = carPrefabVariants[UnityEngine.Random.Range(0, carPrefabVariants.Length)];
                        cars[car.id] = Instantiate(carPrefab, newCarPosition, Quaternion.identity);
                    }
                    
                    if(currPositions.TryGetValue(car.id, out currentPosition))
                        prevPositions[car.id] = currentPosition;
                    currPositions[car.id] = newCarPosition;
                    // currentPosition = cars[car.id].transform.localPosition;
                

                    // Turn rear lights on if car is in traffic queue
                    // if(car.in_traffic)
                    // {
                    //     cars[car.id].transform.GetChild(0).gameObject.SetActive(true);
                    // }
                    // else
                    // {
                    //     cars[car.id].transform.GetChild(0).gameObject.SetActive(false);
                    // }
                }
                carsSpawned++;
            }
            Debug.Log("CARS SPAWNED: " + carsSpawned);

            updated = true;
            if(!carsStarted) carsStarted = true;
        }
    }
    IEnumerator GetTLightsData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getTLightsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            tLightsData = JsonUtility.FromJson<TrafficLightsData>(www.downloadHandler.text);
            //Debug.Log(www.downloadHandler.text);

            foreach(TrafficLightData tLight in tLightsData.data)
            {
                if(!tLightsStarted)
                {
                    tLights[tLight.id] = Instantiate(tLightPrefab, new Vector3(tLight.x, tLight.y, tLight.z), Quaternion.identity);
                    //Check if any of the road objects are neighbours of the traffic light
                    foreach (RoadData road in roadsData.data)
                    {
                        if((road.x == tLight.x+1 && road.z == tLight.z) || (road.x == tLight.x-1 && road.z == tLight.z) || (road.x == tLight.x && road.z == tLight.z+1) || (road.x == tLight.x && road.z == tLight.z-1))
                        {
                            // Debug.Log("MATCH FOUND ++++++++++++++++++++++++++++++++++++++++++");
                            // Debug.Log("ID "+ tLight.id + " is a neighbour of road " + road.id);

                            //Check if the road points to the traffic light
                            if(road.direction == "Up" && road.z == tLight.z-1)
                            {
                                // Debug.Log(tLight.id +"(" + tLight.x +", " + tLight.z + ")" + " FACING UP (" + road.id + ")");
                                tLights[tLight.id].transform.Rotate(0, -90, 0);
                            }
                            else if(road.direction == "Down" && road.z == tLight.z+1)
                            {
                                // Debug.Log(tLight.id +"(" + tLight.x +", " + tLight.z + ")" + " FACING DOWN (" + road.id + ")");
                                tLights[tLight.id].transform.Rotate(0, 90, 0);
                            }
                            else if(road.direction == "Left" && road.x == tLight.x+1)
                            {
                                // Debug.Log(tLight.id +"(" + tLight.x +", " + tLight.z + ")" + " FACING LEFT (" + road.id + ")");
                                tLights[tLight.id].transform.Rotate(0, 180, 0);
                            }
                            else if(road.direction == "Right" && road.x == tLight.x-1)
                            {
                                // Debug.Log(tLight.id +"(" + tLight.x +", " + tLight.z + ")" + " FACING RIGHT (" + road.id + ")");
                                tLights[tLight.id].transform.Rotate(0, 0, 0);
                            }
                        }
                    }
                }
                else
                {
                    GameObject flicker = tLights[tLight.id].transform.GetChild(0).gameObject;
                    // Change the color of the traffic light depending on the state
                    if(tLight.state)
                    {    
                        //If state is true, hide yellow and red child objects and show green
                        flicker.transform.GetChild(0).gameObject.SetActive(true);
                        flicker.transform.GetChild(1).gameObject.SetActive(false);
                        flicker.transform.GetChild(2).gameObject.SetActive(false);
                    }
                    else
                    {
                        //If state is false, hide green and yellow child objects and show red
                        flicker.transform.GetChild(0).gameObject.SetActive(false);
                        flicker.transform.GetChild(1).gameObject.SetActive(true);
                        flicker.transform.GetChild(2).gameObject.SetActive(false);
                    }
                }
            }
            updated = true;
            if(!tLightsStarted) tLightsStarted = true;
        }
    }
    IEnumerator GetSpawnersData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getSpawnersEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            spawnersData = JsonUtility.FromJson<SpawnersData>(www.downloadHandler.text);
            // Debug.Log(www.downloadHandler.text);

            foreach(SpawnerData spawner in spawnersData.data)
            {

                if(!spawnersStarted)
                {
                    // Debug.Log("Creating spawner");
                    spawners[spawner.id] = Instantiate(spawnerPrefab, new Vector3(spawner.x, spawner.y, spawner.z), Quaternion.identity);
                }
            }

            updated = true;
            if(!spawnersStarted) spawnersStarted = true;
        }
    }
    IEnumerator GetDestinationsData()
    {
        // Debug.Log("Getting Destinations data");
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getDestinationsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            arrivals = 0;
            destinationsData = JsonUtility.FromJson<DestinationsData>(www.downloadHandler.text);
            // Debug.Log(www.downloadHandler.text);

            foreach(DestinationData destination in destinationsData.data)
            {
                if(!destinationsStarted)
                {
                    destinations[destination.id] = Instantiate(destinationPrefab, new Vector3(destination.x, destination.y, destination.z), Quaternion.identity);
                }
                else
                {
                    // Debug.Log(destination.arrivals + " vehicles have arrived at Destination " + destination.id + ".");
                    arrivals += destination.arrivals;
                }
            }
            Debug.Log("TOTAL ARRIVALS: " + arrivals);

            updated = true;
            if(!destinationsStarted) destinationsStarted = true;
        }
    }
    IEnumerator GetBuildingsData() 
    {
        // Debug.Log("Getting Buildings data");
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getBuildingsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            buildingsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);
            // Debug.Log(www.downloadHandler.text);

            foreach(AgentData building in buildingsData.positions)
            {
                // Choose a random building prefab variant and add it to the scene
                GameObject buildingPrefab = buildingPrefabVariants[UnityEngine.Random.Range(0, buildingPrefabVariants.Length)];
                Instantiate(buildingPrefab, new Vector3(building.x, building.y, building.z), Quaternion.identity);
            }
        }
    }
}