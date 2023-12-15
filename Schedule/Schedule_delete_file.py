import schedule
import time
from pymongo import MongoClient
import os
from datetime import datetime


def cleanup():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['File-management']
    collection = db['File']

    # Lấy thời điểm hiện tại
    current_time = datetime.utcnow()

    # Lấy các bản ghi có 'life_time' quá thời gian hiện tại
    expired_records = collection.find({'life_time': {'$lt': current_time}})

    for record in expired_records:
        file_name_save = record.get('file_name_save')
        path = record.get("file_path")
        full_path = path + r'\\' + file_name_save
        print(f"Full path: {full_path}")

        if os.path.exists(full_path):
            os.remove(full_path)
            print(f"Đã xóa file {file_name_save}")

        # Xóa bản ghi trong database
        collection.delete_one({'id_file': record['id_file']})
        print(f"Đã xóa bản ghi có id_file = {record['id_file']}")


# Lên lịch cho hàm cleanup chạy sau mỗi 5 phút
schedule.every(5).minutes.do(cleanup)

while True:
    cleanup()
    schedule.run_pending()
    time.sleep(1)
