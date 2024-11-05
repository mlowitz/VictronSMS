import json
from mmap import ACCESS_COPY
from typing import Literal, Union

import requests
from fastapi import HTTPException, Request
from pydantic import BaseModel

import src.VictronProcessors.processor as processor
from src.VictronProcessors.processor import TankValue


class installationInfo(BaseModel):
    access_token: str = None
    user_ID: int = None
    installationID: int = None
    installation_Name: str = None
    phone_number: str = None
    message_time: str = None


def get_tank_device_info(json_data):
    devices = json_data.get("records", {}).get("devices", [])
    tank_info = [
        {
            "customName": device.get("customName"),
            "instance": device.get("instance"),
        }
        for device in devices
        if device.get("name") == "Tank"
    ]
    return tank_info


def get_tank_values(tank_info, headers, installationID):
    tanks = []
    for tank in tank_info:
        tank_url = f"https://vrmapi.victronenergy.com/v2/installations/{installationID}/widgets/TankSummary?instance={tank['instance']}"
        data = requestHelper(headers, tank_url)
        tankDetails = data.get("records", {}).get("data", [])

        for key, item in tankDetails.items():

            customName = tank.get("customName")
            if isinstance(item, dict) and item.get("code") == "tl":
                tank_level = item
                if any(x.customName == customName for x in tanks):
                    for tank_entry in tanks:
                        if tank_entry.customName == customName:
                            tank_entry.value = tank_level.get("formattedValue")

                else:
                    tanks.append(
                        TankValue(
                            customName=customName,
                            value=tank_level.get("formattedValue"),
                        )
                    )

            if isinstance(item, dict) and item.get("code") == "tf":
                tank_info = item
                if any(x.customName == customName for x in tanks):
                    for tank_entry in tanks:
                        if tank_entry.customName == customName:
                            tank_entry.type = tank_info.get("formattedValue")

                else:
                    tanks.append(
                        TankValue(
                            customName=customName,
                            type=tank_info.get("formattedValue"),
                        )
                    )
                    # Stop once the section is found

    return tanks


def requestHelper(headers, url):
    response = requests.get(url, headers=headers)
    return response.json()


def getValues(info: installationInfo):
    values = processor.Item()
    values.boatName = info.installation_Name
    headers = {
        "Content-Type": "application/json",
        "x-authorization": "Token " + info.access_token,
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
