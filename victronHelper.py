import requests
import json
from typing import Union
import json
from fastapi import FastAPI
from pydantic import BaseModel
import os
from twilio.rest import Client
from fastapi import Request, FastAPI
import processor

class installationInfo(BaseModel):
    token : str = None
    user_ID : int = None
    installationID : int = None

    

#VictonURLs 
login_url = 'https://vrmapi.victronenergy.com/v2/auth/login'



def getToken(request: Request):
    
    response = requests.post(login_url ,request)
    raw = json.loads(response.text)
    token = raw["token"]
    info = installationInfo()
    info.token = token
    idUser = raw["idUser"]
    info.user_ID = idUser
    #get installation id 
    url =f"https://vrmapi.victronenergy.com/v2/users/{idUser}/installations"
    headers = {
    "Content-Type": "application/json",
    "x-authorization": "Bearer " + token
    }
    response = requests.request("GET", url, headers=headers)
    
    raw = json.loads(response.text)
    installationID = raw["records"][2]["idSite"]
    info.installationID = installationID
    
    return info   

def requestHelper(headers, url):
    response = requests.request("GET", url, headers=headers)
    data = json.loads(response.text)
    return data

def get_tank_device_info(json_data):
    devices = json_data.get("records", {}).get("devices", [])
    # Filter and extract 'customName' and 'instance' for devices with 'name' as "Tank"
    tank_info = [{"customName": device.get("customName"), "instance": device.get("instance")}
                 for device in devices if device.get("name") == "Tank"]
    return tank_info

def get_tank_values(tankInfo):
    tanks = []
    
    for tank in tankInfo:
        tank_url = f"https://vrmapi.victronenergy.com/v2/installations/(info.installationID)/widgets/TankSummary?instance={tank.instance}"
        data = requestHelper(headers, tank_url)
        tankDetails = data.get("records", {}).get("data", {})
        for attribute in tankDetails:
            if attribute.get("code") == "tl":
                tanks.append({tank.customName: attribute.get("formattedValue")})
            
    return tanks

def getValues(info: installationInfo):
    values =processor.Item()
    headers = {
    "Content-Type": "application/json",
    "x-authorization": "Bearer " + info.token
    }
     #Get SOC
    batterysummary = f"https://vrmapi.victronenergy.com/v2/installations/{info.installationID}/widgets/BatterySummary"
    response = requests.request("GET", batterysummary, headers=headers)
    data = json.loads(response.text)
    socInfo = data.get("records", {}).get("data", {}).get("51")
    values.batterySOC= socInfo.get("formattedValue")
    
    system = f"https://vrmapi.victronenergy.com/v2/installations/{info.installationID}/system-overview"
    data = requestHelper(headers, system)
    
    tanks = get_tank_device_info(data)
    tankValues = get_tank_values(tanks)
    info.tanks = tankValues

    return info

