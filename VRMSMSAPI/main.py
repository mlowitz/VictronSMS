import json
import os
from typing import Union

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from twilio.rest import Client

import VictronProcessors.processor as processor
from . import sender
import VictronProcessors.victronHelper as victronHelper

app = FastAPI(openapi_url="/api/v1/openapi.json")
userToken = ""


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/vrm/")
async def get_victron(request: Request):
    user_info = victronHelper.getToken(await request.json())
    return user_info


@app.get("/vrm/getValues")
async def getValues(request: Request):
    user_info = victronHelper.getToken(await request.json())
    stuff = victronHelper.getValues(user_info)
    message = processor.process(stuff)
    result = sender.sendMessage(message, user_info)
    return result.stat


@app.post("/status/")
async def status_Message(item: processor.Item):
    body = processor.process(item)
    result = sender.sendMessage(body)
    return result
