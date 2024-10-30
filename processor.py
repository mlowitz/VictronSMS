from typing import Union
import json
from fastapi import FastAPI
from pydantic import BaseModel
import os
from twilio.rest import Client

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
    diesel: str = None,
    tanks: [] = None
    
   #Tank Type is going to be this going forward with programmable warning levels  
low_alarm_list = ["hello world", "python programming", "data science", "machine learning"]
high_alarm_list = ["hello world", "python programming", "data science", "machine learning"]
    

def processDynamic(json_data):
    sentences = ""
    warnings = ""
    for key, value in json_data.items():
        # Create a sentence combining key and value for strings
        sentences.append(f"{key.replace('_', ' ')} = {value}%")
        if (any(substring in s for s in low_alarm_list)& (float(value) < 25)):
            warnings.append(f"{key.replace('_', ' ')} = {value}%")
    return sentences

def processTanks(tank_data):
    sentences = []
    for tank in tank_data:
        sentences.append(f"{tank['customName']} = {tank['value']}%\n")
    return sentences

# Next Version will create the paragraph from a key value pair 
def process(thing: Item):
    paragraph = (
        f"Status Report for {thing.boatName}\n\n"
        f"Battery = {thing.batterySOC}%\n"
    )
    paragraph += ''.join(processTanks(thing.tanks))
    return paragraph
