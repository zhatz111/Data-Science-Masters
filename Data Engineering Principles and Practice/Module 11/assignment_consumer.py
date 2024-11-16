from kafka import KafkaConsumer
import json
import pymongo

# Configure MongoDB connection
try:
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    if client:
        print("Connected to MongoDB server")
        client.server_info() # ping the server to verify the connection
except pymongo.errors.ConnectionFailure as e:
    print(f"Failed to connect to MongoDB server: {e}")

db = client['kafka']
test_mongo = db['test_mongo']

consumer = KafkaConsumer(
    "posts",
    bootstrap_servers='localhost:9093',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

if __name__ == "__main__":
    for message in consumer:
        message_value = message.value
        # Insert the message into the MongoDB collection
        #TODO
        db.test_mongo.insert_one(message_value)

        print("Message inserted into MongoDB:", message_value)
