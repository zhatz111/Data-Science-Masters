import json
import time
from datetime import datetime
from faker import Faker
from kafka import KafkaProducer

fake = Faker()

producer = KafkaProducer(
    bootstrap_servers=['localhost:9093'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_message():
    return {
        "timestamp": int(time.time()),
        "phrase": fake.sentence()
    }

if __name__ == "__main__":
    for _ in range(20):
        #TODO
        message = generate_message()
        producer.send(topic="posts", value=message)
        print(f"Sent Message: {message}")
        time.sleep(10)

    producer.flush()
