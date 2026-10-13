from flask import Blueprint, request

from services.auth_service import forget as forget_service
from services.auth_service import add_account_list as add_account_list_service
from services.auth_service import get_account_list as get_account_list_service
from services.auth_service import delete_account_list as delete_account_list_service
from services.auth_service import update_account_list as update_account_list_service
from services.auth_service import get_image_path as get_image_path_service
from services.auth_service import autosave_image_path as autosave_image_path_service
from services.auth_service import get_key_value_mapping as get_key_value_mapping_service
from services.auth_service import autosave_key_value_mapping as autosave_key_value_mapping_service
from services.auth_service import autosave_detect_table as autosave_detect_table_service
from services.auth_service import get_detect_table as get_detect_table_service

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
#更新
@bp.route("/update_account_list", methods=['POST'])
def update_account_list():
    data = request.get_json(force=True)
    return update_account_list_service(
        request,
        data.get('old_user_id'),
        data.get('data')  # 這是一個包含 new_user_id, new_role, new_email 的字典
    )
#圖片
@bp.route("/get_image_path", methods=['POST'])
def get_image_path():
    data = request.get_json(force=True)
    return get_image_path_service(request, data.get('uuid'))

@bp.route("/autosave_image_path", methods=['POST'])
def autosave_image_path():
    data = request.get_json(force=True)
    return autosave_image_path_service(
        request,
        data.get('uuid'),
        data.get('front_path'),
        data.get('back_path')
    )

@bp.route("/get_key_value_mapping", methods=['POST'])
def get_key_value_mapping():
    data = request.get_json(force=True)
    return get_key_value_mapping_service(
        request,
        data.get('vendor'),
        data.get('file_type')
    )

@bp.route("/autosave_key_value_mapping", methods=['POST'])
def autosave_key_value_mapping():
    data = request.get_json(force=True)
    return autosave_key_value_mapping_service(
        request,
        data.get('data')
    )

#表格偵測
@bp.route("/autosave_detect_table", methods=['POST'])
def autosave_detect_table():
    data = request.get_json(force=True)
    return autosave_detect_table_service(
        request,
        data.get('uuid'),
        data.get('data')
    )

@bp.route("/get_detect_table", methods=['POST'])
def get_detect_table():
    data = request.get_json(force=True)
    return get_detect_table_service(request, data.get('uuid'))