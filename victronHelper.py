import requests
import json
from typing import Union
from fastapi import Request
from pydantic import BaseModel
import processor
from processor import TankValue

class installationInfo(BaseModel):
    token: str = None
    user_ID: int = None
    installationID: int = None
    installationName: str = None

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

    url = f"https://vrmapi.victronenergy.com/v2/users/{idUser}/installations"
    headers = {
        "Content-Type": "application/json",
        "x-authorization": "Bearer " + token
    }
    response = requests.get(url, headers=headers)
    raw = response.json()
    installationID = raw["records"][2]["idSite"]
    info.installationID = installationID
    info.installationName = raw["records"][2]["name"]

    return info

def requestHelper(headers, url):
    response = requests.get(url, headers=headers)
    return response.json()

def get_tank_device_info(json_data):
    devices = json_data.get("records", {}).get("devices", [])
    tank_info = [{"customName": device.get("customName"), "instance": device.get("instance")}
                 for device in devices if device.get("name") == "Tank"]
    return tank_info

def get_tank_values(tankInfo, headers, installationID):
    tanks = []
    for tank in tankInfo:
        tank_url = f"https://vrmapi.victronenergy.com/v2/installations/{installationID}/widgets/TankSummary?instance={tank['instance']}"
        data = requestHelper(headers, tank_url)
        tankDetails = data.get("records", {}).get("data", [])
        
        for key, item in tankDetails.items():
    # Ensure we're dealing with a dictionary containing the "code" field
         if isinstance(item, dict) and item.get("code") == "tl":
            tankLevel = item
            tanks.append(TankValue(customName=tank.get("customName"), value=tankLevel.get("formattedValue")))
            break  # Stop once the section is found
        
    
    return tanks

def getValues(info: installationInfo):
    values = processor.Item()
    values.name = info.installationName
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