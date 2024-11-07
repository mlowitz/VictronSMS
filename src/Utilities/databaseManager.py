import configparser
import datetime
import json
import os
import sys
from datetime import datetime
import zoneinfo

import pymongo
from bson.json_util import dumps, loads
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

import src.VictronProcessors.userManagement as userManagement

# Read configuration from environment variables
connection_string = os.getenv("MONGODB_CONNECTION_STRING")

if not connection_string:
    raise ValueError(
        "Environment variable MONGODB_CONNECTION_STRING is missing"
    )

# Read configuration from a file

try:
    client = MongoClient(connection_string)

# return a friendly error if a URI error is thrown
except pymongo.errors.ConfigurationError:
    print(
        "An Invalid URI host error was received. Is your Atlas host name correct in your connection string?"
    )
    sys.exit(1)

# use a database named "myDatabase"
db = client.VrmNotificationSubscriptions

subscribers_collection = db["test"]

# Send a ping to confirm a successful connection
try:
    with pymongo.timeout(10):
        client.admin.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# TODO - check for unique subscriber before adding


def addSubscriber(subscriber: userManagement.SubscribedUser):
    subscriber_dict = subscriber.__dict__
    try:
        key = {"user_ID": subscriber.user_ID}
        subscribers_collection.update_one(
            key,
            {"$set": subscriber_dict},
            upsert=True,
        )
    except Exception as e:
        print(e)
    pass


def getAllSubscriptions() -> list[userManagement.SubscribedUser]:
    raw = list(subscribers_collection.find({}))
    subscriptions: list[userManagement.SubscribedUser] = [
        userManagement.from_json(dumps(doc)) for doc in raw
    ]
    return subscriptions
    pass


def getAllSubscriptionsForTime() -> list[userManagement.SubscribedUser]:
    current_hour = str(
        datetime.now(zoneinfo.ZoneInfo("America/Los_Angeles")).hour
    )
    search = {"time": current_hour}
    raw = list(subscribers_collection.find(search))
    subscriptions: list[userManagement.SubscribedUser] = [
        userManagement.from_json(dumps(doc)) for doc in raw
    ]
    return subscriptions
    pass
