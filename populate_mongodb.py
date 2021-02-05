from kafka import KafkaConsumer
import json
from pymongo import MongoClient
import xml.etree.ElementTree as ET
from bson import ObjectId
import sys

## Params
# Set to your 529
USER529 = "asherlk1"
# Print all the records in the database
SHOWDB = False


# Number of messages to retrieve, set to 0 to poll indefinitely
if len(sys.argv) > 1:
    NUM_MESSAGES_TO_RETRIEVE = int(sys.argv[1])
else:
    NUM_MESSAGES_TO_RETRIEVE = 1
# Restart flag will drop records collection and repopulate it
if len(sys.argv) > 2 and "restart" in sys.argv[2]:
    RESTARTDB = True
else:
    RESTARTDB = False

## Define mongo client
client = MongoClient()
db = client["arxiv"]
records = db["records"]

## Convenience and helper functions
dbg_prefix = "\n*******"


def parseXML(xmlbytes):
    tree = ET.ElementTree(ET.fromstring(xmlbytes.decode("utf-8")))
    find = tree.findall(
        ".//{*}GetRecord/{*}record/{*}metadata/{http://www.openarchives.org/OAI/2.0/oai_dc/}dc/"
    )
    data_dict = {}
    for item in find:
        data_dict[item.tag.split("}")[1]] = item.text
    return data_dict


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


def addRecordToDB(record_dict):
    for key in record_dict.keys():
        record_dict[key] = record_dict[key].lower()

    if "arxiv" not in client.list_database_names():
        print(f"{dbg_prefix} Creating new arxiv database...")

    if RESTARTDB and "arxiv" in client.list_database_names():
        print(f"{dbg_prefix} Dropping the records collection from arxiv database...\n")
        records.drop()
        return []

    if RESTARTDB and not "arxiv" in client.list_database_names():
        print(f"{dbg_prefix} Inserting first record {record_dict}")
        records.insert_one(record_dict)

    ## Check if record exists first
    if records.find_one({"identifier": record_dict["identifier"]}) is None:
        SHOWDB and print(f"{dbg_prefix} Record inserted {record_dict}")
        records.insert_one(record_dict)

    return records


def showDB(records, num):
    i = 0
    if records == []:
        print(f"{dbg_prefix} Database is empty\n")
        return
    cursor = records.find({})
    if SHOWDB:
        print(
            "\n********************* Whole record collection so far *********************"
        )
        for document in cursor:
            if num == "all" or i < num:
                encoded_reponse = JSONEncoder().encode(document)
                print(json.dumps(json.loads(encoded_reponse), indent=4))
                print("------------------------------------")
                i = i + 1
    print(f"{dbg_prefix} Number of records in db {records.count_documents({})}\n")


## Kafka parameters
KAFKA_TOPIC = "pai.arxiv"
GROUP_ID = f"QAS_IG_{USER529.upper()}"
BOOTSTRAP_SERVER = "aplkafka-01p.datalake.jhuapl.edu:9092"

## Create consumer
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    group_id=GROUP_ID,
    bootstrap_servers=[BOOTSTRAP_SERVER],
)
numMessagesLeft = NUM_MESSAGES_TO_RETRIEVE

while NUM_MESSAGES_TO_RETRIEVE == 0 or numMessagesLeft != 0:
    numMessagesLeft -= 1
    # print('\nAbout to make Kafkfa call...') #leaving this here, because sometimes Kafkfa stalls
    msg = next(consumer).value
    record_dict = parseXML(msg)

    ## Add new records to database
    records = addRecordToDB(record_dict)
    if records == []:
        break

showDB(records, "all")