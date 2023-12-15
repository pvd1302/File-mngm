from flask import request, jsonify
from db.model import user_collection
from flask_jwt_extended import *


def login_service():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = user_collection.find_one({"username": username, "password": password})
    if user:
        access_token = create_access_token(identity={
            'username': username
        })
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401
