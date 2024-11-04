import json
import re
from email import header
from http import request
from mmap import ACCESS_COPY
from typing import Literal, Union

import requests
from fastapi import HTTPException, Request
from pydantic import BaseModel

import app.VictronProcessors.processor as processor
import app.VictronProcessors.victronHelper as victronHelper
from app.VictronProcessors.processor import TankValue


class onboardingRequest(BaseModel):
    username: str = None
    password: str = None
    supplied_name: str = None
    phone_number: str = None
    time: str = None
    supplied_name: str = None
    bearer_token: str = None
    user_ID: int = None
    access_token: str = None


login_url = "https://vrmapi.victronenergy.com/v2/auth/login"
access_token_url = (
    "https://vrmapi.victronenergy.com/v2/users/{}/accesstokens/create"
)
all_access_tokens_url = (
    "https://vrmapi.victronenergy.com/v2/users/{}/accesstokens/list"
)

access_token_expected_error = (
    "The given name for the accesstoken is not unique"
)


name = ""
access_token_name = "SMSNotifier"


def getBearerToken(request: onboardingRequest):
    request_data = {
        "name": request.username,
        "password": request.password,
    }
    headers = {
        "Content-Type": "application/json",
    }
    response = requests.post(login_url, json=request_data, headers=headers)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Failed to get access token",
        )
    raw = response.json()
    request.bearer_token = raw["token"]
    request.user_ID = raw["idUser"]


def onBoarding(request: onboardingRequest):

    getBearerToken(request)
    getAccessToken(request)
    getInstallationInfo(request)
    return request


def getAccessToken(onboardingInfo: onboardingRequest):
    request_data = {
        "name": access_token_name,
        "password": onboardingInfo.password,
    }
    headers = {
        "Content-Type": "application/json",
        "x-authorization": "Bearer " + onboardingInfo.bearer_token,
    }
    response = requests.post(
        access_token_url.format(onboardingInfo.user_ID),
        json=request_data,
        headers=headers,
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Failed to get access token",
        )
    request_json = json.dumps(request_data)

    raw = response.json()
    if raw["success"] == True:
        # return access token
        onboardingInfo.access_token = raw["token"]
    else:  # delete token and recreate it
        if raw["errors"] and raw["errors"][0].get("name"):
            revokeAccessToken(onboardingInfo)
            getAccessToken(onboardingInfo)

    # todo get access token if it exists


# else:
# TODO get token info delete it and then recreate it
def revokeAccessToken(onboardingInfo: onboardingRequest):
    # delete access token with name SMS Notifier
    headers = {
        "Content-Type": "application/json",
        "x-authorization": "Token " + onboardingInfo.access_token,
    }
    tokens_for_use = requestHelper(
        headers,
        f"https://vrmapi.victronenergy.com/v2/users/{onboardingInfo.user_ID}/accesstokens/list",
    )
    tokens = tokens_for_use.get("tokens", [])
    for token in tokens:
        if token.get("name") == access_token_name:
            idAccessToken = token.get("idAccessToken")
            victronHelper.requestHelper(
                headers,
                f"https://vrmapi.victronenergy.com/v2/users/{onboardingInfo.user_ID}/accesstokens/{idAccessToken}/revoke",
            )
    pass


def getInstallationInfo(onboardingInfo: onboardingRequest):

    url = f"https://vrmapi.victronenergy.com/v2/users/{onboardingInfo.user_ID}/installations"
    headers = {
        "Content-Type": "application/json",
        "x-authorization": "Token " + onboardingInfo.access_token,
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Failed to get access token",
        )
    raw = response.json()
    # if user does not supply installation name
    if onboardingInfo.supplied_name == None:
        onboardingInfo.installationID = raw["records"][0]["idSite"]
        onboardingInfo.installation_Name = raw["records"][0]["name"]

    else:
        records = raw.get("records", [])
        for item in records:
            # Ensure we're dealing with a dictionary containing the "code" field
            if (
                isinstance(item, dict)
                and onboardingInfo.supplied_name.lower()
                in item.get("name", "").lower()
            ):
                onboardingInfo.installation_Name = item.get("name")
                onboardingInfo.installationID = item.get("idSite")
                break


def requestHelper(headers, url):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Failed to get access token",
        )
    return response.json()
