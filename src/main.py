import json
import os
import re
from typing import Union

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from google.cloud import secretmanager


# Create the Secret Manager client.
client = secretmanager.SecretManagerServiceClient()
name = client.secret_path("777217683107", "configfile/versions/latest")
response = client.access_secret_version(request={"name": name})
config = json.loads(response.payload.data.decode("UTF-8"))
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
    name = client.secret_path("777217683107", "configfile/versions/latest")
    response = client.access_secret_version(request={"name": name})
    config = json.loads(response.payload.data.decode("UTF-8"))
    return config


@app.post("/vrm/")
async def get_victron(request: Request):
    user_info = victronHelper.getToken(await request.json())
    return user_info


@app.get(
    """
    Endpoint to run for all subscribed users.

    This endpoint retrieves values for all subscribed users and sends messages.

    Returns:
        dict: A dictionary indicating the run status.

    Raises:
        HTTPException: If there is an error in retrieving user subscriptions or sending messages.

    """
    "/vrm/run",
    summary="Run for All Users",
    description="Retrieve values for all subscribed users and send messages.",
)
async def getAllSubscriptions():
    user_info = databaseManager.getAllSubscriptions()
    if not user_info:
        return {"run": "No users to run"}
    for user in user_info:
        stuff = victronHelper.getValues(user)
        message = processor.process(stuff)
        result = sender.sendMessage(message, user)
    return {"run": "done"}


@app.get(
    """
    Retrieve values for subscribed users based on current time and send messages.

    This endpoint fetches all subscriptions for the current time from the database,
    retrieves relevant values for each user, processes the data, and sends messages
    to the users.

    Returns:
        dict: A dictionary indicating the result of the operation. If no users are
        found, returns {"run": "No users to run"}. Otherwise, returns the number
        of users processed in the format {"run": f"Run for {user_info.count()} users"}.
    """
    "/vrm/runTime",
    summary="Run for Users Based on Time",
    description="Retrieve values for subscribed users based on current time and send messages.",
)
async def getSubscriptionsForTime():
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


@app.post(
    """
    Handles the onboarding of a new subscriber.

    Endpoint:
        POST /vrm/onboard

    Summary:
        Onboard a new subscriber.

    Description:
        Creates a new subscriber in the database.

    Args:
        request (userManagement.onboardingRequest): The request object containing the onboarding details.

    Returns:
        dict: A dictionary with the status of the operation.
    """
    "/vrm/onboard",
    summary="onboard a new subscriber",
    description="creates a new subscriber in the database",
)
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
