from typing import Union, List
import json
from fastapi import FastAPI
from pydantic import BaseModel
import os
from twilio.rest import Client

class TankValue(BaseModel):
    """
    TankValue is a model representing a tank's value with a custom name.

    Attributes:
        customName (str): The custom name of the tank. Defaults to None.
        value (str): The value associated with the tank. Defaults to None.
    """
    customName: str| None = None
    value: str | None = None

class Item(BaseModel):
    phoneNumber: str = None
    boatName: str = None   
    installationName: str = None
    freshWater1: str = None
    freshWater2: str = None
    lpg1: str = None
    lpg2: str = None
    batterySOC: str = None
    poop: str = None
    diesel: str = None
    tanks: List[TankValue] = []

low_alarm_list = ["hello world", "python programming", "data science", "machine learning"]
high_alarm_list = ["hello world", "python programming", "data science", "machine learning"]

def processDynamic(json_data):
    sentences = []
    warnings = []
    for key, value in json_data.items():
        sentences.append(f"{key.replace('_', ' ')} = {value}%")
        if any(substring in s for s in low_alarm_list) and (float(value) < 25):
            warnings.append(f"{key.replace('_', ' ')} = {value}%")
    return sentences

def processTanks(tank_data):
    sentences = []
    for tank in tank_data:
        sentences.append(f"{tank.customName} = {tank.value}")
    return sentences

def process(thing: Item):
    paragraph = (
        f"Status Report for {thing.boatName}\n\n"
        f"Battery = {thing.batterySOC}\n"
    )
    paragraph += '\n'.join(processTanks(thing.tanks))
    return paragraph
