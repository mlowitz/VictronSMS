import json
import re
from typing import Literal, Union

import requests
from fastapi import HTTPException, Request
from pydantic import BaseModel, Field

from pydantic.json_schema import SkipJsonSchema
from typing import ClassVar
import src.VictronProcessors.processor as processor
import src.VictronProcessors.victronHelper as victronHelper
from src.VictronProcessors.processor import TankValue
from typing_extensions import Annotated


class onboardingRequest(BaseModel):
    username: str = None
    password: str = None
    supplied_name: str = None
    phone_number: str = None
    time: str | None = None


class onboardingDetails(onboardingRequest):
    user_ID: int = None
    bearer_token: str = None
    access_token: str = None
    installationID: int = None
    installation_Name: str = None

    @classmethod
    def from_onboarding_request(cls, request: onboardingRequest):
        return cls(
            username=request.username,
            password=request.password,
            supplied_name=request.supplied_name,
            phone_number=request.phone_number,
            time=request.time,
        )


class SubscribedUser(BaseModel):
    user_ID: int = None
    phone_number: str = None
    installationID: int = None
    installation_Name: str = None
    access_token: str = None
    time: str = None
    phone_number: str = None


def from_json(json_str: str) -> SubscribedUser:
    data = json.loads(json_str)
    user = SubscribedUser()
    user.user_ID = data.get("user_ID")
    user.phone_number = data.get("phone_number")
    user.installationID = data.get("installationID")
    user.installation_Name = data.get("installation_Name")
    user.access_token = data.get("access_token")
    user.time = data.get("time")
    return user


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


def map_onboarding_to_subscribed(
    onboarding: onboardingDetails,
) -> SubscribedUser:
    user = SubscribedUser()
    user.user_ID = onboarding.user_ID
    user.phone_number = onboarding.phone_number
    user.installationID = onboarding.installationID
    user.installation_Name = onboarding.installation_Name
    user.access_token = onboarding.access_token
    user.time = onboarding.time
    return user


def getBearerToken(request: onboardingDetails):
    request_data = {
        "username": request.username,
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


def onBoarding(request: onboardingDetails):

    getBearerToken(request)
    getAccessToken(request)
    getInstallationInfo(request)
    user = map_onboarding_to_subscribed(request)
    return user


def getAccessToken(onboardingInfo: onboardingDetails):
    request_data = {"name": access_token_name}
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
        if (
            raw["errors"]
            and raw["errors"].get("name") == access_token_expected_error
        ):
            revokeAccessToken(onboardingInfo)
            getAccessToken(onboardingInfo)

    # todo get access token if it exists


# else:
# TODO get token info delete it and then recreate it
def revokeAccessToken(onboardingInfo: onboardingDetails):
    # delete access token with name SMS Notifier
    headers = {
        "Content-Type": "application/json",
        "x-authorization": "Bearer " + onboardingInfo.bearer_token,
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


def getInstallationInfo(onboardingInfo: onboardingDetails):

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
