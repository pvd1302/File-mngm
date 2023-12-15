from flask import Blueprint
from Auth.controller import *

authens = Blueprint("authens", __name__)


@authens.route("/files-management/login", methods=['POST'])
def login():
    return login_service()
