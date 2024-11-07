import json
import os
import re
from typing import Union

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel


with open(
    os.path.join(os.path.dirname(__file__), "configs/config.json")
) as config_file:
    config = json.load(config_file)
    for key, value in config.items():
        os.environ[key] = str(value)

import src.VictronProcessors.processor as processor
import src.SMSUtility.sender as sender
import src.VictronProcessors.victronHelper as victronHelper
import src.VictronProcessors.userManagement as userManagement
import src.Utilities.databaseManager as databaseManager


class onboardBody(BaseModel):
    username: str = None
    password: str = None
    supplied_name: str = None
    phone_number: str = None
    time: str = None


app = FastAPI(openapi_url="/api/v1/openapi.json")
userToken = ""


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/json")
async def read_root():
    with open(os.environ["SECRET_PATH"]) as config_file:
        config = json.load(config_file)
        return config


@app.post("/vrm/")
async def get_victron(request: Request):
    user_info = victronHelper.getToken(await request.json())
    return user_info


@app.get("/vrm/run")
async def getValues():
    user_info = databaseManager.getAllSubscriptions()
    if not user_info:
        return {"run": "No users to run"}
    for user in user_info:
        stuff = victronHelper.getValues(user)
        message = processor.process(stuff)
        result = sender.sendMessage(message, user)
    return {"run": "done"}


@app.get("/vrm/runTime")
async def getValues():
    user_info = databaseManager.getAllSubscriptionsForTime()
    if not user_info:
        return {"run": "No users to run"}
    for user in user_info:
        stuff = victronHelper.getValues(user)
        message = processor.process(stuff)
        result = sender.sendMessage(message, user)
    return {"run": f"Run for {user_info.count()} users"}


@app.get("/vrm/getValues")
async def getValues(request: Request):
    user_info = userManagement.getToken(await request.json())
    stuff = victronHelper.getValues(user_info)
    message = processor.process(stuff)
    result = sender.sendMessage(message, user_info)
    return result.stat


@app.post("/vrm/onboard")
async def onBoard(request: userManagement.onboardingRequest):
    c = userManagement.onboardingDetails.from_onboarding_request(request)
    user_info = userManagement.onBoarding(
        userManagement.onboardingDetails.from_onboarding_request(request)
    )
    databaseManager.addSubscriber(user_info)
    return {"status": "done"}


@app.post("/status/")
async def status_Message(item: processor.Item):
    body = processor.process(item)
    result = sender.sendMessage(body)
    return result
