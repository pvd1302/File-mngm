import datetime
import re

import unidecode
from bson import ObjectId
from flask import jsonify
from flask_jwt_extended import jwt_required

from Entity.Folder_entity import *
from Kafka_update.producer import *
from Library.delete_redis import *
from Library.paging import *
from db.mash import *
from db.model import *

r = redis.StrictRedis(host='localhost', port=6379, db=0)

producer_config = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'client_users'
}


@jwt_required()
class Folder_mgmt(Folder):
    def __init__(self):
        super().__init__()
        self.id_folder = ObjectId()

    def create_Folder(self):
        data = request.get_json()

        name_folder = data['name_folder']
        existing_folder = folder_collection.find_one({'name_folder': name_folder, 'created_by': self.username})
        if existing_folder is None:
            data_insert = {
                "id_folder": str(self.id_folder),
                "name_folder": name_folder,
                "created_by": self.username,
                "created_at": datetime.utcnow(),
                "updated_by": self.username,
                "updated_at": datetime.utcnow(),
            }

            folder_collection.insert_one(data_insert)
            Delete_redis_keys_with_prefix(f"folders_{self.username}")
            return jsonify({"message": "Folder created successfully"}), 201

        else:
            return jsonify({"message": "Folder exist"}), 404

    def get_Folders(self):

        page = int(request.args.get('page', 1))
        if page < 1:
            return jsonify({'message': 'Invalid pagination parameters. Page must be greater than or equal to 1'})
        per_page = int(request.args.get('per_page', 20))

        # Lấy dữ liệu từ redis

        conditions = [f"folders_{self.username}_{page}_{per_page}"]

        if self.name_folder:
            conditions.append(str(self.name_folder))

        key_list_folders = "_".join(conditions)
        cached_data = r.get(key_list_folders)
        if cached_data:
            return jsonify(json.loads(cached_data))

        query = {'created_by': self.username}

        if self.name_folder:
            query['name_folder'] = {'$regex': re.compile(self.name_folder)}
            print(unidecode.unidecode(self.name_folder))

        folder_query = folder_collection.find(query)
        total_count = folder_collection.count_documents(query)
        folders = folder_query.limit(per_page).skip(per_page * (page - 1))

        folders_schema = FolderSchema(many=True)  # Đặt many=True nếu users là danh sách
        folders_json = folders_schema.dump(folders)

        pagination_info = calculate_pagination(total_count, page, per_page)

        if folders:
            data = {
                'data': folders_json,
                'current_record': len(folders_json),
                'current_page': page,
                'total_users': total_count,
                **pagination_info,
            }
            r.set(key_list_folders, json.dumps(data))

            return data

        else:
            return jsonify({"message": "Invalid pagination parameters!"}), 404

    def get_folder_by_id(self, id_folder):

        check_permission = folder_collection.find_one({"created_by": self.username, "id_folder": id_folder})
        if check_permission is None:
            return jsonify({"message": "You don't have enough permission !"}), 404

        cache_key = f"folder_{id_folder}_{self.username}"
        cached_data = r.get(cache_key)
        if cached_data:
            return jsonify(json.loads(cached_data))

        folder_data = folder_collection.find_one({'id_folder': id_folder, 'created_by': self.username})

        folder_schema = FolderSchema()  # Đặt many=True nếu users là danh sách
        folder_json = folder_schema.dump(folder_data)
        if folder_data:
            data = {
                'data': folder_json,
            }
            r.set(cache_key, json.dumps(data))

            return data

    def update_folder_by_id(self, id_folder):
        data = request.get_json()

        # name_folder = data.get("name_folder")
        check_permission = folder_collection.find_one({
            "created_by": self.username,
            "id_folder": id_folder,
        })
        if check_permission is None:
            return jsonify({"message": "You don't have enough permission !"}), 404

        data = request.get_json()
        if any(key in data for key in ['_id', 'id_folder', 'created_by', 'created_at', 'updated_by', 'updated_at']):
            return jsonify({'error': 'Cannot update some filed, pls check !!'}), 400

        if self.name_folder:
            duplicate_folder = folder_collection.find_one({
                "id_folder": {"$ne": id_folder},
                "name_folder": self.name_folder
            })
            if duplicate_folder:
                return jsonify({'error': 'Folder exist !!'}), 400

        data_update = {"id_folder": id_folder,
                       "updated_by": self.username
                       }

        data_update.update(data)

        KafkaProducer().send_message("update_folder", data_update)
        Delete_redis_keys_with_prefix(f'folder_{self.username}_{id_folder}')
        return jsonify({'message': 'Folder Updated !'})

    def delete_folder_by_id(self, id_folder):
        folder_requested = folder_collection.find_one({"created_by": self.username, "id_folder": id_folder})
        if folder_requested:
            folder_collection.delete_one({'created_by': self.username, 'id_folder': id_folder})
            return jsonify({'message': 'Folder Deleted !'})
        else:
            return jsonify({"message": "You don't have enough permission !"}), 404
