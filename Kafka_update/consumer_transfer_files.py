import json

import redis
from confluent_kafka import Consumer

from db.model import *


r = redis.StrictRedis(host='localhost', port=6379, db=0)

# Cấu hình consumer
config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'consumer_update_team',
    'auto.offset.reset': 'earliest'
}

# Khởi tạo consumer
consumer = Consumer(config)

topic_name = 'transfer_files'
consumer.subscribe([topic_name])


def update_folder():
    while True:
        msgs = consumer.consume(1)

        if not msgs:
            continue

        msg = msgs[0]

        data_receive = msg.value().decode()
        print(f'Received message: {data_receive}')
        try:
            data = json.loads(data_receive)
            id_folder = data.get("id_folder")
            list_files = data.get("list_files")

            update_query = {"$set": {"id_folder": id_folder}}
            file_collection.update_many(list_files, update_query)

            print(f"Updated files")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")


if __name__ == '__main__':
    update_folder()
