from typing import Union
import json
from fastapi import FastAPI
from pydantic import BaseModel
import processor
import sender
from twilio.rest import Client
import os
import victronHelper
from fastapi import Request, FastAPI


app = FastAPI()
userToken = ""
    
@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/vrm/")
async def get_victron(request: Request):
    userinfo = victronHelper.getToken(await request.body())
    return  userinfo

@app.get("/vrm/getValues")
async def getValues(info : victronHelper.installationInfo):
    stuff = victronHelper.getValues(info)
    return info

#post 
@app.post("/status/")
async def status_Message(item : processor.Item):
    body =  processor.process(item)
    result =   sender.sendMessage(body)
    return result




