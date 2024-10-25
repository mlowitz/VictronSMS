import requests
import json
from typing import Union
import json
from fastapi import FastAPI
from pydantic import BaseModel
import os
from twilio.rest import Client
from fastapi import Request, FastAPI

class Cred(BaseModel):
    username: str
    password: str 

    

#VictonURLs 
login_url = 'https://vrmapi.victronenergy.com/v2/auth/login'
batterysummary_url = "https://vrmapi.victronenergy.com/v2/installations/{installation_ID}/widgets/BatterySummary"

#use your own victron installation id instead of "93772"



#use the name and password you log in to VRM with
token = ""



#headers = {'X-Authorization': "Bearer " + token }




def getToken(request: Request):
    response = requests.post(login_url ,request)
    token = json.loads(response.text)["token"]
        



