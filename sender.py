from twilio.rest import Client
import os
from fastapi import FastAPI

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = "AC81a2da88f4c9b633f64f8d3c20d999f6"
auth_token = "ccd593a8fa886e93481f6a44dad2dcf1"
client = Client(account_sid, auth_token)


def sendMessage(content): 
    message = client.messages.create(
    body=content,
    from_="+14846794226",
    to="+16109967105",
    )
    return(message.body)
