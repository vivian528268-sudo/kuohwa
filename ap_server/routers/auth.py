from flask import Blueprint, request

from services.auth_service import forget as forget_service
from services.auth_service import add_account_list as add_account_list_service
from services.auth_service import get_account_list as get_account_list_service
from services.auth_service import delete_account_list as delete_account_list_service

bp = Blueprint('auth', __name__)

#忘記密碼
@bp.route("/forget", methods=['POST'])
def forget():
    data = request.get_json(force=True)
    return forget_service(request, data.get('user_id'))
#新增
@bp.route("/add_account_list", methods=['POST'])
def add_account_list():
    data = request.get_json(force=True)
    return add_account_list_service(request, data.get('user_id'), data.get('role'), data.get('email'))
#查詢
@bp.route("/get_account_list", methods=['GET'])
def get_account_list():
    return get_account_list_service(request)
#刪除
@bp.route("/delete_account_list/<user_id>", methods=['DELETE'])
def delete_account_list(user_id):
    return delete_account_list_service(request, user_id)