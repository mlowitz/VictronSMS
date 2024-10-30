import requests
import json
from typing import Union
import json
from fastapi import FastAPI
from pydantic import BaseModel
import os
from twilio.rest import Client
from fastapi import Request, FastAPI

class installationInfo(BaseModel):
    token : str = None
    user_ID : int = None
    installationID : int = None

    

#VictonURLs 
login_url = 'https://vrmapi.victronenergy.com/v2/auth/login'
batterysummary_url = "https://vrmapi.victronenergy.com/v2/installations/{installation_ID}/widgets/BatterySummary"

#use your own victron installation id instead of "93772"



#use the name and password you log in to VRM with





def getToken(request: Request):
    
    response = requests.post(login_url ,request)
    raw = json.loads(response.text)
    token = raw["token"]
    info = installationInfo()
    info.token = token
    idUser = raw["idUser"]
    info.user_ID = idUser
    #get installation id 
    url =f"https://vrmapi.victronenergy.com/v2/users/{idUser}/installations"
    headers = {
    "Content-Type": "application/json",
    "x-authorization": "Bearer " + token
    }
    response = requests.request("GET", url, headers=headers)
    
    raw = json.loads(response.text)
    installationID = raw["records"][2]["idSite"]
    info.installationID = installationID
    
    return info   

def getValues(info: installationInfo):
    batterysummary_url = f"https://vrmapi.victronenergy.com/v2/installations/{info.installationID}/widgets/BatterySummary"
    return "yay"
