import requests
import json
from typing import Literal, Union
from fastapi import Request
from pydantic import BaseModel
import processor
from processor import TankValue

class installationInfo(BaseModel):
    token: str = None
    user_ID: int = None
    installationID: int = None
    installation_Name: str = None
    supplied_name: str = None

login_url = 'https://vrmapi.victronenergy.com/v2/auth/login'
name =""
def getToken(request: dict):
    response = requests.post(login_url, json=request)
    raw = response.json()
    token = raw["token"]
    info = installationInfo()
    info.token = token
    idUser = raw["idUser"]
    info.user_ID = idUser
    info.supplied_name = request.get("supplied_name")

    url = f"https://vrmapi.victronenergy.com/v2/users/{idUser}/installations"
    headers = {
        "Content-Type": "application/json",
        "x-authorization": "Bearer " + token
    }
    response = requests.get(url, headers=headers)
    raw = response.json()
    # if user does not supply installation name
    if info.supplied_name == None:
        info.installationID = raw["records"][0]["idSite"]
        info.installation_Name = raw["records"][0]["name"]
        return info
    
    records = raw.get("records", [])
    for item in records:
        # Ensure we're dealing with a dictionary containing the "code" field        
        if isinstance(item, dict) and info.supplied_name.lower() in item.get("name", "").lower():
            info.installation_Name = item.get("name")
            info.installationID = item.get("idSite")
            break

    return info

def requestHelper(headers, url):
    response = requests.get(url, headers=headers)
    return response.json()

def get_tank_device_info(json_data):
    devices = json_data.get("records", {}).get("devices", [])
    tank_info = [{"customName": device.get("customName"), "instance": device.get("instance")}
                 for device in devices if device.get("name") == "Tank"]
    return tank_info

def get_tank_values(tank_info, headers, installationID):
    tanks = []
    for tank in tank_info:
        tank_url = f"https://vrmapi.victronenergy.com/v2/installations/{installationID}/widgets/TankSummary?instance={tank['instance']}"
        data = requestHelper(headers, tank_url)
        tankDetails = data.get("records", {}).get("data", [])
        
        for key, item in tankDetails.items():
    
            customName= tank.get("customName")
            if isinstance(item, dict) and item.get("code") == "tl":
                tank_level = item
                if any(x.customName == customName for x in tanks):
                    for tank_entry in tanks:
                        if tank_entry.customName == customName:
                            tank_entry.value = tank_level.get("formattedValue")
                            
                else:
                    tanks.append(TankValue(customName= customName, value=tank_level.get("formattedValue")))
                    
         
            if isinstance(item, dict) and item.get("code") == "tf":
                tank_info = item
                if any(x.customName == customName for x in tanks):
                    for tank_entry in tanks:
                        if tank_entry.customName == customName:
                            tank_entry.value = tank_info.get("formattedValue")
                            
                else:
                    tanks.append(TankValue(customName=customName, type=tank_info.get("formattedValue")))
                      # Stop once the section is found
        
    return tanks

def getValues(info: installationInfo):
    values = processor.Item()
    values.boatName = info.installation_Name
    headers = {
        "Content-Type": "application/json",
        "x-authorization": "Bearer " + info.token
    }

    battery_summary = f"https://vrmapi.victronenergy.com/v2/installations/{info.installationID}/widgets/BatterySummary"
    response = requests.get(battery_summary, headers=headers)
    data = response.json()
    socInfo = data.get("records", {}).get("data", {}).get("51")
    values.batterySOC = socInfo.get("formattedValue")

    system = f"https://vrmapi.victronenergy.com/v2/installations/{info.installationID}/system-overview"
    data = requestHelper(headers, system)

    tanks = get_tank_device_info(data)
    tankValues = get_tank_values(tanks, headers, info.installationID)
    values.tanks = tankValues

    return values