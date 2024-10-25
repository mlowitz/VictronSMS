from twilio.rest import Client
import os
from fastapi import FastAPI

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure

client = Client(account_sid, auth_token)


def sendMessage(content): 
    message = client.messages.create(
    body=content,
    from_="+14846794226",
    to="+16109967105",
    )
    return(message.body)
