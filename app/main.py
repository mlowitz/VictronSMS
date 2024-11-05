import json
import os
from typing import Union

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from twilio.rest import Client

import app.VictronProcessors.processor as processor
import app.SMSUtility.sender as sender
import app.VictronProcessors.victronHelper as victronHelper
import app.VictronProcessors.userManagement as userManagement
import app.Utilities.databaseManager as databaseManager

app = FastAPI(openapi_url="/api/v1/openapi.json")
userToken = ""


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/vrm/")
async def get_victron(request: Request):
    user_info = victronHelper.getToken(await request.json())
    return user_info


@app.get("/vrm/run")
async def getValues():
    user_info = databaseManager.getAllSubscriptions()
    for user in user_info:
        stuff = victronHelper.getValues(user)
        message = processor.process(stuff)
        result = sender.sendMessage(message, user)
    return result


@app.get("/vrm/getValues")
async def getValues(request: Request):
    user_info = userManagement.getToken(await request.json())
    stuff = victronHelper.getValues(user_info)
    message = processor.process(stuff)
    result = sender.sendMessage(message, user_info)
    return result.stat


@app.post("/vrm/onboard")
async def onBoard(request: userManagement.onboardingRequest):
    user_info = userManagement.onBoarding(request)
    # TODO - Add the user to the database
    databaseManager.addSubscriber(user_info)
    stuff = victronHelper.getValues(user_info)
    message = processor.process(stuff)
    result = sender.sendMessage(message, user_info)
    return result.stat


@app.post("/status/")
async def status_Message(item: processor.Item):
    body = processor.process(item)
    result = sender.sendMessage(body)
    return result
