from flask import Blueprint
from Folder_mgmt.controller import *

folders = Blueprint("folders", __name__)


@folders.route("/files-management/folders", methods=['POST'])
@jwt_required()
def create_folder():
    return Folder_mgmt().create_Folder()


@folders.route("/files-management/folders", methods=['GET'])
@jwt_required()
def get_Folder():
    return Folder_mgmt().get_Folders()


@folders.route("/files-management/folders/<string:id>", methods=['GET'])
@jwt_required()
def get_folder_byID(id: str):
    return Folder_mgmt().get_folder_by_id(id)


@folders.route("/files-management/folders/<string:id>", methods=['PUT'])
@jwt_required()
def update_folder_byID(id: str):
    return Folder_mgmt().update_folder_by_id(id)


@folders.route("/files-management/folders/<string:id>", methods=['DELETE'])
@jwt_required()
def delete_folder_byID(id: str):
    return Folder_mgmt().delete_folder_by_id(id)
