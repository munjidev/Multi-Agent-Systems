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
public class RobotData
{
    public string id;
    public float x, y, z;
    public bool has_package;

    public RobotData(string id, bool has_package, float x, float y, float z)
    {
        this.id = id;
        this.has_package = has_package;
        this.x = x;
        this.y = y;
        this.z = z;
    }
}

[Serializable]
public class DepotData
{
    public string id;
    public int package_num;
    public float x, y, z;

    public DepotData(string id, int package_num, float x, float y, float z)
    {
        this.id = id;
        this.package_num = package_num;
        this.x = x;
        this.y = y;
        this.z = z;
    }
}

[Serializable]
public class PackageData
{
    public string id;
    public bool picked_up;
    public float x, y, z;

    public PackageData(string id, bool picked_up, float x, float y, float z)
    {
        this.id = id;
        this.picked_up = picked_up;
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
public class RobotsData
{
    public List<RobotData> data;

    public RobotsData() => this.data = new List<RobotData>();
}

[Serializable]
public class DepotsData
{
    public List<DepotData> data;

    public DepotsData() => this.data = new List<DepotData>();
}

[Serializable]
public class PackagesData
{
    public List<PackageData> data;

    public PackagesData() => this.data = new List<PackageData>();
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
    RobotsData agentsData;
    DepotsData depotsData;
    PackagesData packagesData;
    Dictionary<string, GameObject> agents, depots, packages;
    Dictionary<string, Vector3> prevPositions, currPositions;

    bool updated = false, agentsStarted = false, depotsStarted = false, packagesStarted = false;

    public GameObject agentPrefab, obstaclePrefab, packagePrefab, depotPrefab, floor;
    public int NAgents, NPackages, width, height;
    public float timeToUpdate = 5.0f;
    private int NDepots;
    private float timer, dt;

    void Start()
    {
        agentsData = new RobotsData();
        depotsData = new DepotsData();
        packagesData = new PackagesData();
        obstacleData = new AgentsData();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        agents = new Dictionary<string, GameObject>();
        depots = new Dictionary<string, GameObject>();
        packages = new Dictionary<string, GameObject>();

        floor.transform.localScale = new Vector3((float)width/10, 1, (float)height/10);
        floor.transform.localPosition = new Vector3((float)width/2-0.5f, 0, (float)height/2-0.5f);
        
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
            //End simulation if all packages states are picked up
            for (int i = 0; i < packagesData.data.Count; i++)
            {
                if (!packagesData.data[i].picked_up)
                {
                    break;
                }
                if (i == packagesData.data.Count - 1)
                {
                    Debug.Log("SUCCESS");
                    Debug.Log("All packages picked up");
                    UnityEditor.EditorApplication.isPlaying = false;
                }
            }

            // These coroutines will update the data of the agents, depots and packages
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetDepotsData());
            StartCoroutine(GetPackagesData());
        }
    }

    IEnumerator SendConfiguration()
    {
        WWWForm form = new WWWForm();

        form.AddField("NAgents", NAgents.ToString());
        form.AddField("NPackages", NPackages.ToString());
        form.AddField("NDepots", NDepots.ToString());
        form.AddField("width", width.ToString());
        form.AddField("height", height.ToString());

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
            Debug.Log("Getting Packages positions");
            StartCoroutine(GetPackagesData());
            StartCoroutine(GetObstacleData());
            StartCoroutine(GetDepotsData());
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
            agentsData = JsonUtility.FromJson<RobotsData>(www.downloadHandler.text);

            // Update the positions of the agents
            foreach(RobotData agent in agentsData.data)
            {
                Vector3 newAgentPosition = new Vector3(agent.x, agent.y, agent.z);

                if(!agentsStarted)
                {
                    prevPositions[agent.id] = newAgentPosition;
                    agents[agent.id] = Instantiate(agentPrefab, newAgentPosition, Quaternion.identity);
                }
                else
                {
                    Vector3 currentPosition = new Vector3();
                    if(currPositions.TryGetValue(agent.id, out currentPosition))
                        prevPositions[agent.id] = currentPosition;
                    currPositions[agent.id] = newAgentPosition;

                    if(agent.has_package)
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
                    Debug.Log("Depot #" + depot.id + " has " + depot.package_num + " packages");
                    if (depot.package_num==0)
                    {
                        depots[depot.id].transform.GetChild(0).gameObject.SetActive(false);
                        depots[depot.id].transform.GetChild(1).gameObject.SetActive(false);
                        depots[depot.id].transform.GetChild(2).gameObject.SetActive(false);
                        depots[depot.id].transform.GetChild(3).gameObject.SetActive(false);
                        depots[depot.id].transform.GetChild(4).gameObject.SetActive(false);

                    }
                    else if (depot.package_num==1)
                    {
                        depots[depot.id].transform.GetChild(0).gameObject.SetActive(true);
                        depots[depot.id].transform.GetChild(1).gameObject.SetActive(false);
                        depots[depot.id].transform.GetChild(2).gameObject.SetActive(false);
                        depots[depot.id].transform.GetChild(3).gameObject.SetActive(false);
                        depots[depot.id].transform.GetChild(4).gameObject.SetActive(false);
                    }
                    else if (depot.package_num==2)
                    {
                        depots[depot.id].transform.GetChild(0).gameObject.SetActive(true);
                        depots[depot.id].transform.GetChild(1).gameObject.SetActive(true);
                        depots[depot.id].transform.GetChild(2).gameObject.SetActive(false);
                        depots[depot.id].transform.GetChild(3).gameObject.SetActive(false);
                        depots[depot.id].transform.GetChild(4).gameObject.SetActive(false);
                    }
                    else if (depot.package_num==3)
                    {
                        depots[depot.id].transform.GetChild(0).gameObject.SetActive(true);
                        depots[depot.id].transform.GetChild(1).gameObject.SetActive(true);
                        depots[depot.id].transform.GetChild(2).gameObject.SetActive(true);
                        depots[depot.id].transform.GetChild(3).gameObject.SetActive(false);
                        depots[depot.id].transform.GetChild(4).gameObject.SetActive(false);
                    }
                    else if (depot.package_num==4)
                    {
                        depots[depot.id].transform.GetChild(0).gameObject.SetActive(true);
                        depots[depot.id].transform.GetChild(1).gameObject.SetActive(true);
                        depots[depot.id].transform.GetChild(2).gameObject.SetActive(true);
                        depots[depot.id].transform.GetChild(3).gameObject.SetActive(true);
                        depots[depot.id].transform.GetChild(4).gameObject.SetActive(false);
                    }
                    else if (depot.package_num==5)
                    {
                        depots[depot.id].transform.GetChild(0).gameObject.SetActive(true);
                        depots[depot.id].transform.GetChild(1).gameObject.SetActive(true);
                        depots[depot.id].transform.GetChild(2).gameObject.SetActive(true);
                        depots[depot.id].transform.GetChild(3).gameObject.SetActive(true);
                        depots[depot.id].transform.GetChild(4).gameObject.SetActive(true);
                    }
                }
            }

            updated = true;
            if(!depotsStarted) depotsStarted = true;
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