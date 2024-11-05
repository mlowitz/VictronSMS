import configparser
import os
import sys
from bson.json_util import dumps
from bson.json_util import loads
import pymongo
import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import app.VictronProcessors.userManagement as userManagement

# Read configuration from a file
config = configparser.ConfigParser()
config_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "config.ini"
)


config.read(config_path)
# Ensure the config file has the necessary sections and keys
if "mongodb" not in config or "connection_string" not in config["mongodb"]:
    raise ValueError("Config file is missing required Twilio configuration")
connection_string = config["mongodb"]["connection_string"]


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


def addSubscriber(subscriber: userManagement.SubscribedUser):
    subscriber_dict = subscriber.__dict__
    subscribers_collection.insert_one(dumps(subscriber))
    pass


def getAllSubscriptions() -> list[userManagement.SubscribedUser]:
    raw = list(subscribers_collection.find({}))
    subscriptions: list[userManagement.SubscribedUser] = [
        userManagement.from_json(dumps(doc)) for doc in raw
    ]
    return subscriptions
    pass