from flask import request
from flask_jwt_extended import get_jwt_identity


class Folder:
    def __init__(self):
        current_user = get_jwt_identity()
        self.username = current_user['username']

        if 'name_folder' in request.form:
            self.name_folder = request.form.get('name_folder')
        elif 'name_folder' in request.args:
            self.name_folder = request.args.get('name_folder')
        else:
            self.name_folder = None


