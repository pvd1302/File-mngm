from flask import Blueprint
from File_mgmt.controller import *

files = Blueprint("files", __name__)


@files.route("/files-management/files", methods=['POST'])
@jwt_required()
def upload_file():
    return File_mgmt().upload_Files()


@files.route("/files-management/files", methods=['GET'])
@jwt_required()
def get_Files():
    return File_mgmt().get_files()


@files.route("/files-management/files/<string:id>", methods=['GET'])
@jwt_required()
def get_File_byID(id: str):
    return File_mgmt().get_file_by_id(id)


@files.route("/files-management/files/<string:id>", methods=['PUT'])
@jwt_required()
def update_file_byID(id: str):
    return File_mgmt().update_file_by_id(id)


@files.route("/files-management/files/transfer", methods=['POST'])
@jwt_required()
def transfer_files():
    return File_mgmt().transfer_files()


@files.route("/files-management/files/<string:id>", methods=['DELETE'])
@jwt_required()
def Delete_file(id: str):

    return File_mgmt().delete_file_by_id(id)


@files.route("/files/<filename>", methods=['GET'])
@jwt_required()
def file_from_local(filename):
    return File_mgmt().get_file_from_local(filename)
