from twilio.rest import Client
import os
from fastapi import FastAPI
import configparser

# Read configuration from a file
config = configparser.ConfigParser()
config.read('config.ini')

account_sid = config['twilio']['account_sid']
auth_token = config['twilio']['auth_token']

client = Client(account_sid, auth_token)

def sendMessage(content): 
    message = client.messages.create(
        body=content,
        from_="+14846794226",
        to="+16109967105",
    )
    return message.body
