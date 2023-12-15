from flask import request
from flask_jwt_extended import get_jwt_identity


class File:
    def __init__(self):
        current_user = get_jwt_identity()
        self.username = current_user['username']

        if 'file_name' in request.form:
            self.file_name = request.form.get('file_name')
        elif 'file_name' in request.args:
            self.file_name = request.args.get('file_name')
        else:
            self.file_name = None

        if 'id_folder' in request.form:
            self.id_folder = request.form.get('id_folder')
        elif 'id_folder' in request.args:
            self.id_folder = request.args.get('id_folder')
        else:
            self.id_folder = None



