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

    
@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/vrm/")
async def get_victron(request: Request):
    t = victronHelper.getToken(await request.body())
    return t
#post 
@app.post("/status/")
async def status_Message(item : processor.Item):
    body =  processor.process(item)
    result =   sender.sendMessage(body)
    return result




