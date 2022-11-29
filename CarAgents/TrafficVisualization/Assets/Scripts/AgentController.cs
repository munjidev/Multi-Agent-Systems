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

[Serializable]
public class AgentData
{
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
public class CarData
{
    public string id;
    public float x, y, z;
    public bool in_traffic;

    public CarData(string id, bool in_traffic, float x, float y, float z)
    {
        this.id = id;
        this.in_traffic = in_traffic;
        this.x = x;
        this.y = y;
        this.z = z;
    }
}

[Serializable]
public class DestinationData
{
    public string id;
    public int arrivals;
    public float x, y, z;

    public DestinationData(string id, int arrivals, float x, float y, float z)
    {
        this.id = id;
        this.arrivals = arrivals;
        this.x = x;
        this.y = y;
        this.z = z;
    }
}

[Serializable]
public class SpawnerData
{
    public string id;
    public int spawned;
    public float x, y, z;

    public SpawnerData(string id, int spawned, float x, float y, float z)
    {
        this.id = id;
        this.spawned == spawned;
        this.x = x;
        this.y = y;
        this.z = z;
    }
}

[Serializable]
public class AgentsData
{
    public List<AgentData> positions;

    public AgentsData() => this.positions = new List<AgentData>();
}

[Serializable]
public class CarsData
{
    public List<CarData> data;

    public CarsData() => this.data = new List<CarData>();
}

[Serializable]
public class DestinationsData
{
    public List<DestinationsData> data;

    public DestinationsData() => this.data = new List<DestinationsData>();
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
    string getAgentsEndpoint = "/getAgents";
    string getDepotsEndpoint = "/getDepots";
    string getPackagesEndpoint = "/getPackages";
    string getObstaclesEndpoint = "/getObstacles";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";

    AgentsData obstacleData;
    CarsData agentsData;
    DestinationsData destinationsData;
    SpawnersData spawnersData;
    Dictionary<string, GameObject> cars, destinations, spawners;
    Dictionary<string, Vector3> prevPositions, currPositions;

    bool updated = false, carsStarted = false, tlightsStarted = false, destinationsStarted = false, spawnersStarted = false;

    public GameObject carPrefab, buildingPrefab, tlightPrefab, destinationPrefab, spawnerPrefab;
    public int NAgents;
    public float timeToUpdate = 5.0f;
    private int NDepots;
    private float timer, dt;

    void Start()
    {
        carsData = new CarsData();
        destinationsData = new DestinationsData();
        spawnersData = new SpawnersData();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        cars = new Dictionary<string, GameObject>();
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

            foreach(var agent in currPositions)
            {
                Vector3 currentPosition = agent.Value;
                Vector3 previousPosition = prevPositions[agent.Key];

                Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);
                Vector3 direction = currentPosition - interpolated;

                agents[agent.Key].transform.localPosition = interpolated;
                if(direction != Vector3.zero) agents[agent.Key].transform.rotation = Quaternion.LookRotation(direction);
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
            // These coroutines will update the data of the agents, depots and packages
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetDestinationsData());
            StartCoroutine(GetSpawnersData());
        }
    }

    IEnumerator SendConfiguration()
    {
        // WWWForm form = new WWWForm();

        // form.AddField("NAgents", NAgents.ToString());

        UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            Debug.Log("Configuration upload complete!");
            Debug.Log("Getting Agents positions");
            StartCoroutine(GetAgentsData());
            Debug.Log("Getting Spawner and Destination positions");
            StartCoroutine(GetDestinationsData());
            StartCoroutine(GetSpawnersData());
        }
    }

    IEnumerator GetAgentsData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getAgentsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            agentsData = JsonUtility.FromJson<CarsData>(www.downloadHandler.text);

            // Update the positions of the agents
            foreach(CarsData car in carsData.data)
            {
                Vector3 newCarPosition = new Vector3(car.x, car.y, car.z);

                if(!carsStarted)
                {
                    prevPositions[car.id] = newCarPosition;
                    cars[car.id] = Instantiate(carPrefab, newAgentPosition, Quaternion.identity);
                }
                else
                {
                    Vector3 currentPosition = new Vector3();
                    if(currPositions.TryGetValue(car.id, out currentPosition))
                        prevPositions[car.id] = currentPosition;
                    currPositions[car.id] = newCarPosition;

                    if(car.in_traffic)
                    {
                        agents[agent.id].transform.GetChild(0).gameObject.SetActive(true);
                    }
                    else
                    {
                        agents[agent.id].transform.GetChild(0).gameObject.SetActive(false);
                    }
                }
            }

            updated = true;
            if(!agentsStarted) agentsStarted = true;
        }
    }

    IEnumerator GetPackagesData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getPackagesEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            packagesData = JsonUtility.FromJson<PackagesData>(www.downloadHandler.text);
            Debug.Log(www.downloadHandler.text);

            foreach(PackageData package in packagesData.data)
            {

                if(!packagesStarted)
                {
                    Debug.Log("Creating package");
                    packages[package.id] = Instantiate(packagePrefab, new Vector3(package.x, package.y, package.z), Quaternion.identity);
                }
                else
                {
                    Debug.Log("Package #" + package.id + " was picked up: " + package.picked_up);
                    if (package.picked_up)
                    {
                        //Hide the prefab instance
                        packages[package.id].SetActive(false);

                    }
                    else
                    {
                        //Show the prefab instance
                        packages[package.id].SetActive(true);
                    }
                }
            }

            updated = true;
            if(!packagesStarted) packagesStarted = true;
        }
    }

    IEnumerator GetDepotsData()
    {
        Debug.Log("Getting Depots data");
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getDepotsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            
            depotsData = JsonUtility.FromJson<DepotsData>(www.downloadHandler.text);
            // Debug.Log(www.downloadHandler.text);

            foreach(DepotData depot in depotsData.data)
            {
                if(!depotsStarted)
                {
                    Debug.Log("Creating depot");
                    depots[depot.id] = Instantiate(depotPrefab, new Vector3(depot.x, depot.y, depot.z), Quaternion.identity);
                }
                else
                {
                    Debug.Log(destination.arrivals + " vehicles have arrived at Destination " + destination.id + ".");
                }
            }

            updated = true;
            if(!destinationsStarted) destinationsStarted = true;
        }
    }

    IEnumerator GetObstacleData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getObstaclesEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            obstacleData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            Debug.Log(obstacleData.positions);

            foreach(AgentData obstacle in obstacleData.positions)
            {
                Instantiate(obstaclePrefab, new Vector3(obstacle.x, obstacle.y, obstacle.z), Quaternion.identity);
            }
        }
    }
}