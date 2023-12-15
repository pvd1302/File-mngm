import datetime
import os

import redis
import unidecode
from PIL import Image
from bson import ObjectId
from flask_jwt_extended import jwt_required

from flask import jsonify, send_from_directory
from Entity.FIle_entity import *
from Kafka_update.producer import *
from Library.check_file import *
from Library.convert_time import *
from Library.delete_redis import Delete_redis_keys_with_prefix
from Library.paging import *
from db.mash import *
from db.model import *

r = redis.StrictRedis(host='localhost', port=6379, db=0)

producer_config = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'client_users'
}
app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'docx', 'xlsx'}

app.config['UPLOAD_FOLDER'] = r'D:\python flask API\File-mngm\data'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file_extension(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@jwt_required()
class File_mgmt(File):
    def __init__(self):
        super().__init__()
        self.id_file = ObjectId()

    def upload_Files(self):
        file = request.files['file']
        life_time = request.form.get('life_time')

        check_creator = folder_collection.find_one({"created_by": self.username, "id_folder": self.id_folder})
        if check_creator is None:
            return jsonify({"message": "You don't have enough permission !"}), 404

        if file and self.file_name and self.id_folder and life_time is None:
            return jsonify({"error": "Missing required fields"}), 400

        filename = file.filename

        # Kiểm tra xem có file nào được chọn không
        if filename == '':
            return jsonify({"error": "No selected file"}), 400

        result_resolution, result_real_format = infor_file(file)

        file.seek(0)
        file_size = len(file.read())
        size_in_mb = round(file_size / (1024 ** 2), 2)
        if not allowed_file_size(file_size):
            return 'File size exceeds the allowed limit'
        # đọc lại file, lưu vào bộ nhớ
        file.seek(0)
        # folder = username

        filename_save = str(self.id_file) + "." + str(result_real_format)
        # Tạo đường dẫn đến thư mục của người dùng
        user_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], self.username)

        # Tạo thư mục nếu nó chưa tồn tại
        if not os.path.exists(user_folder_path):
            os.makedirs(user_folder_path)

        # Đường dẫn đầy đủ đến tệp cần lưu
        file_path = os.path.join(user_folder_path, filename_save)

        # Lưu tệp vào đường dẫn đã chọn
        file.save(file_path)
        life_time_converted = convert_to_datetime(life_time)
        data_insert = {
            "id_file": str(self.id_file),
            "file_path": user_folder_path,
            "file_name": self.file_name,
            "file_name_save": filename_save,
            "id_folder": self.id_folder,
            "format": result_real_format,
            "resolution": result_resolution,
            "size": f"{size_in_mb} MB",
            "life_time": life_time_converted,
            "key_word": unidecode.unidecode(self.file_name),
            "created_by": self.username,
            "created_at": datetime.utcnow(),
            "updated_by": self.username,
            "updated_at": datetime.utcnow(),
        }
        file_collection.insert_one(data_insert)
        Delete_redis_keys_with_prefix(f'files_{self.username}')

        return jsonify({"message": "File created successfully"}), 201

    def get_files(self):

        per_page = int(request.args.get('per_page', 20))
        page = int(request.args.get('page', 1))

        if 'folder' in request.args:
            check_permission = folder_collection.find_one({"created_by": self.username, "id_folder": self.id_folder})
            if check_permission is None:
                return jsonify({"message": "You don't have enough permission !"}), 404

        # Lấy dữ liệu từ redis
        conditions = [f"files_{self.username}_{page}_{per_page}"]

        if self.file_name:
            conditions.append(str(self.file_name))
        if self.id_folder:
            conditions.append(str(self.id_folder))

        key_list_files = "_".join(conditions)

        cached_data = r.get(key_list_files)
        if cached_data:
            return jsonify(json.loads(cached_data))

        query = {"created_by": self.username}
        if self.file_name:
            query["key_word"] = {'$regex': unidecode.unidecode(self.file_name), "$options": "i"}

        if self.id_folder:
            query["id_folder"] = self.id_folder
        total_count = file_collection.count_documents(query)
        files_query = (file_collection.find(query).
                       limit(per_page).skip(per_page * (page - 1)))

        # files = files_query

        files_schema = FileSchema(many=True)
        files_json = files_schema.dump(files_query)

        pagination_info = calculate_pagination(total_count, page, per_page)
        if files_query:
            data = {
                'data': files_json,
                'current_record': len(files_json),
                'current_page': page,
                'total_file': total_count,
                **pagination_info,
            }
            r.set(key_list_files, json.dumps(data))
            return data

        else:
            return jsonify({"message": "Invalid pagination parameters!"}), 404

    def get_file_by_id(self, id_file):

        cache_key = f"file_{id_file}_{self.username}"
        cached_data = r.get(cache_key)
        if cached_data:
            return jsonify(json.loads(cached_data))

        file_data = file_collection.find_one({"created_by": self.username, "id_file": id_file})
        if file_data is None:
            return jsonify({"message": "You don't have enough permission !"}), 404
        elif file_data:

            file_schema = FileSchema()  # Đặt many=True nếu users là danh sách
            file_json = file_schema.dump(file_data)

            data = {
                'data': file_json,
            }
            r.set(cache_key, json.dumps(data))
            return data

    def update_file_by_id(self, id_file):
        data = request.form.to_dict()
        file = request.files.get('file')

        check_permission = file_collection.find_one({"created_by": self.username, "id_file": id_file})
        if check_permission is None:
            return jsonify({"message": "You don't have enough permission !"}), 404
        data = request.form.to_dict()

        for key in data.keys():
            if key not in ['file', 'file_name']:
                return jsonify({'error': f'Cannot update the field {key}, please check !!'}), 400

            # if  (key in data for key in ['_id', 'id_file', 'created_by', 'created_at', 'updated_by', 'updated_at']):
            # return jsonify({'error': 'Cannot update some filed, pls check !!'}), 400

        original_name = check_permission.get("file_name_save")
        if file:
            result_resolution, result_real_format = infor_file(file)

            file.seek(0)
            file_size = len(file.read())
            size_in_mb = round(file_size / (1024 ** 2), 2)
            if not allowed_file_size(file_size):
                return 'File size exceeds the allowed limit'

            file.seek(0)

            file_name_save = str(id_file) + "." + str(result_real_format)

            data_update = {"id_file": id_file,
                           "updated_by": self.username,
                           "resolution": result_resolution,
                           "file_name_save": file_name_save,
                           "size": f"{size_in_mb} MB",
                           "format": result_real_format
                           }

            # Đường dẫn đầy đủ đến tệp cần lưu
            # file_path = os.path.join(user_folder_path, file_name_save)
            file_path_old = os.path.join(app.config['UPLOAD_FOLDER'], self.username, original_name)
            if os.path.exists(file_path_old):
                os.remove(file_path_old)
            file_path_new = os.path.join(app.config['UPLOAD_FOLDER'], self.username, file_name_save)
            file.save(file_path_new)
        else:
            data_update = {"id_file": id_file,
                           "updated_by": self.username,
                           }

        data_update.update(data)
        KafkaProducer().send_message("update_file", data_update)
        Delete_redis_keys_with_prefix(f'file_{id_file}')

        return jsonify({'message': 'File Updated !'})

    def transfer_files(self):

        data = request.get_json()
        list_id_files = data['list_id_files']

        id_folder = data['id_folder']
        check_permission = folder_collection.find_one({"created_by": self.username, "id_folder": id_folder})
        if check_permission is None:
            return jsonify({"message": "You don't have enough permission !"}), 404

        filer_files = {
            "id_file": {"$in": list_id_files},
            "created_by": self.username
        }

        data_update = {"list_files": filer_files,
                       "id_folder": id_folder
                       }

        KafkaProducer().send_message("transfer_files", data_update)
        Delete_redis_keys_with_prefix('file')

        return jsonify({'message': 'Files Updated !'})

    def delete_file_by_id(self, id_file):

        file_requested = file_collection.find_one({"created_by": self.username, "id_file": id_file})
        if file_requested:
            file_collection.delete_one({'created_by': self.username, 'id_file': id_file})
            Delete_redis_keys_with_prefix(f'file_{id_file}')

            return jsonify({'message': 'File Deleted !'})
        else:
            return jsonify({"message": "You don't have enough permission !"}), 404

    def get_file_from_local(self, filename):

        # Tạo đường dẫn đầy đủ đến file trong thư mục lưu trữ
        path = os.path.join(app.config['UPLOAD_FOLDER'], self.username)

        # Trả về file cho client
        return send_from_directory(path, filename)
