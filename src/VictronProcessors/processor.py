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

    customName: str | None = None
    value: str | None = None
    type: str | None = None


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


low_alarm_list = ["Diesel", "LPG", "Fresh water", "Fuel", "Gasoline", "LNG"]
high_alarm_list = [
    "Black water (sewage)",
    "python programming",
    "data science",
    "machine learning",
]


def addWarnings(tank_data):
    warnings = []
    for tank in tank_data:
        if any(substring in tank.type for substring in low_alarm_list) and (
            float(tank.value.replace("%", "")) < 30
        ):
            warnings.append(f"Warning  {tank.customName} Low Level")
        if any(substring in tank.type for substring in high_alarm_list) and (
            float(tank.value.replace("%", "")) > 75
        ):
            warnings.append(f"Warning  {tank.customName} High Level")
    return warnings


def processTanks(tank_data):
    sentences = []
    for tank in tank_data:
        sentences.append(f"{tank.customName} = {tank.value}")
    return sentences


def process(thing: Item):
    paragraph = f"Status Report for {thing.boatName}\n\n"
    warnings = addWarnings(thing.tanks)
    if warnings:
        paragraph += "\n".join(warnings) + "\n"
    paragraph += f"\nBattery = {thing.batterySOC}\n"
    paragraph += "\n".join(processTanks(thing.tanks))
    return paragraph
