from kafka import KafkaConsumer
import json

# parameters
KAFKA_TOPIC = "sc-access-point-bldg"
# KAFKA_TOPIC = "sc-access-point-room"
GROUP_ID = None
BOOTSTRAP_SERVER = "lc-spacebee-1:9092"
# number of messages to retrieve, set to 0 to poll indefinitely
NUM_MESSAGES_TO_RETRIEVE = 0

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    group_id=GROUP_ID,
    bootstrap_servers=[BOOTSTRAP_SERVER],
)

# numMessagesLeft = NUM_MESSAGES_TO_RETRIEVE
# for msg in consumer:
#     print(msg)
# while NUM_MESSAGES_TO_RETRIEVE == 0 or numMessagesLeft != 0:
# 	numMessagesLeft -= 1
# 	print('New message: ', next(consumer).value, '\n')

numMessagesLeft = NUM_MESSAGES_TO_RETRIEVE
while NUM_MESSAGES_TO_RETRIEVE == 0 or numMessagesLeft != 0:
    numMessagesLeft -= 1
    print(numMessagesLeft)
    print(consumer)
    msg = next(consumer).value
    print(msg)