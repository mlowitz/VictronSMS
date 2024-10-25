from typing import Union
import json
from fastapi import FastAPI
from pydantic import BaseModel
import os
from twilio.rest import Client

class Item(BaseModel):
    phoneNumber: str
    boatName: str   
    installationName: str
    freshWater1: str
    freshWater2: str
    lpg1: str
    lpg2: str
    batterySOC: str
    poop: str
    diesel: str
    
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


# Next Version will create the paragraph from a key value pair 
def process(thing=Item):
    # This line of code is creating a formatted string `x` that represents a status report for a boat.
    # It includes various parameters such as the boat's name, battery state of charge, fresh water
    # levels, LPG levels, poop levels (assuming this is related to waste management), and diesel
    # levels. The values for these parameters are taken from the `thing` object, which is an instance
    # of the `Item` class. The `f` before the string indicates an f-string in Python, allowing for
    # variable interpolation within the string.
    paragraph = (
    f"Status Report for , {thing.boatName}\n\n"
    f"Battery = {thing.batterySOC}%\n"
    f"FreshWater 1 = {thing.freshWater1}%\n"
    f"FreshWater2 = {thing.freshWater2}%\n"
    f"LPG 1 = {thing.lpg1}%\n"
    f"Poop = {thing.poop}%\n"
    f"Diesel = {thing.diesel}%\n"
    )
    return paragraph
