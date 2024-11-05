import configparser
import os

import requests
from fastapi import FastAPI
from twilio.rest import Client


# Read configuration from a file
config = configparser.ConfigParser()
config_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "config.ini"
)
config.read(config_path)
# Ensure the config file has the necessary sections and keys
if "openphone" not in config or "key" not in config["openphone"]:
    raise ValueError("Config file is missing required openphone configuration")
key = config["openphone"]["key"]
auth_token = config["twilio"]["auth_token"]
sender_phone_number = config["openphone"]["sender_phone_number"]


def sendMessage(content, user_info):

    url = "https://api.openphone.com/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "Authorization": key,
    }
    data = {
        "content": content,
        "from": sender_phone_number,
        "to": [f"{user_info.phone_number}"],
    }
    response = requests.post(url, headers=headers, json=data)

    return response
