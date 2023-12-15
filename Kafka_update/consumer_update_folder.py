import json

import redis
from confluent_kafka import Consumer, KafkaException
from db.model import *

# from library.delete_redis import Delete_redis_keys_with_prefix

r = redis.StrictRedis(host='localhost', port=6379, db=0)

# Cấu hình consumer
config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'consumer_update_team',
    'auto.offset.reset': 'earliest'
}

# Khởi tạo consumer
consumer = Consumer(config)

topic_name = 'update_folder'
consumer.subscribe([topic_name])


def update_folder():
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
            id_folder = data.get("id_folder")

            folder_collection.update_one(
                {"id_folder": id_folder},
                {"$set": data},
            )
            print(f"Updated folder with id {id_folder}")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")


if __name__ == '__main__':
    update_folder()
