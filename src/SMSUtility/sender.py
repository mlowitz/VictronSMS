import configparser
import os

import requests
from fastapi import FastAPI
from twilio.rest import Client


key = os.getenv("OPENPHONE_KEY")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
sender_phone_number = os.getenv("OPENPHONE_SENDER_PHONE_NUMBER")
twilio_sender_phone_number = os.getenv("TWILIO_SENDER_PHONE_NUMBER")
twilio_SID = os.getenv("TWILIO_SID")
if not key or not auth_token or not sender_phone_number:
    raise ValueError(
        "Environment variables for API keys and phone numbers are not set"
    )


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
