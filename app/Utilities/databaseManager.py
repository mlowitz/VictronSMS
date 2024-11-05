import pymongo
import sys


# Read configuration from a file
config = configparser.ConfigParser()
config_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "config.ini"
)
config.read(config_path)
# Ensure the config file has the necessary sections and keys
if "aws" not in config or "connection_string" not in config["twilio"]:
    raise ValueError("Config file is missing required Twilio configuration")
connection_string = config["twilio"]["connection_string"]

##Create a MongoDB client, open a connection to Amazon DocumentDB as a replica set and specify the read preference as secondary preferred
client = pymongo.MongoClient(connection_string)

##Specify the database to be used
db = client.sample_database

##Specify the collection to be used
col = db.sample_collection

##Insert a single document
col.insert_one({"hello": "Amazon DocumentDB"})

##Find the document that was previously written
x = col.find_one({"hello": "Amazon DocumentDB"})

##Print the result to the screen
print(x)

##Close the connection
client.close()
