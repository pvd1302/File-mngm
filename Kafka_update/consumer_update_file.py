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

topic_name = 'update_file'
consumer.subscribe([topic_name])


def update_file():
    while True:
        msgs = consumer.consume(1)

        if not msgs:
            # Nếu danh sách rỗng, không có tin nhắn nào được nhận được
            continue

        msg = msgs[0]  # Lấy tin nhắn đầu tiên từ danh sách

        data_receive = msg.value().decode()
        print(f'Received message: {data_receive}')
        try:
            data = json.loads(data_receive)
            id_file = data.get("id_file")

            file_collection.update_one(
                {"id_file": id_file},
                {"$set": data},
            )
            print(f"Updated file with id {id_file}")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")


if __name__ == '__main__':
    update_file()
