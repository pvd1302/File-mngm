from datetime import timedelta

from flask import Flask
from flask_jwt_extended import JWTManager

from Auth.services import authens
from Folder_mgmt.services import folders
from File_mgmt.services import files


def create_app():
    app = Flask(__name__)
    app.register_blueprint(authens)
    app.register_blueprint(folders)
    app.register_blueprint(files)

    app.json_sort_keys = False  # Để đảm bảo rằng khóa JSON không được sắp xếp
    app.config['JWT_SECRET_KEY'] = 'dlwlrma'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=900)  # Thời gian tồn tại của access token, ví dụ 30 phút
    JWTManager(app)  # Khởi tạo JWTManager sau khi tạo app

    return app


if __name__ == "__main__":
    program = create_app()
    program.run(debug=True)
