from pymongo import MongoClient
from datetime import datetime

# Kết nối đến MongoDB
client = MongoClient("mongodb://localhost:27017/")

db = client["File-management"]

folder_collection = db["Folder"]
file_collection = db["File"]
user_collection = db["User"]






