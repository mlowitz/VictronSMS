from twilio.rest import Client
import os
from fastapi import FastAPI
import configparser
import requests
import victronHelper


# Read configuration from a file
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "config.ini"))
# Ensure the config file has the necessary sections and keys
if (
    "twilio" not in config
    or "account_sid" not in config["twilio"]
    or "auth_token" not in config["twilio"]
):
    raise ValueError("Config file is missing required Twilio configuration")
account_sid = config["twilio"]["account_sid"]
auth_token = config["twilio"]["auth_token"]
sender_phone_number = config["twilio"]["sender_phone_number"]
client = Client(account_sid, auth_token)


def sendMessage(content, user_info):

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=content,
        from_=sender_phone_number,
        to=user_info.phone_number,
    )

    url = "https://hooks.zapier.com/hooks/catch/16093259/290qnju/"
    headers = {"Content-Type": "application/json"}
    data = {"message": content}
    response = requests.post(url, headers=headers, json=data)

    return message
