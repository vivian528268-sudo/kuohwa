#邏輯

from base_api import MySQLAccess
import json # 因為要處理 role 的 JSON 轉換

def forget(request, user_id: str):
    # 驗證輸入
    if not user_id:
        return {
            "result": 1,
            "message": "invalid user id"
        }

    try:
        # 建立連接
        conn = MySQLAccess.get_connection()
        cursor = conn.cursor()

        # 確認帳號存在（目前 account_list 沒有密碼欄位，寄信重設尚未實作）
        cursor.execute("SELECT user_id FROM account_list WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()

        if not result:
            return {
                "result": 1,
                "message": "user id 不存在"
            }

        return {
            "result": 0,
            "message": ""
        }

    except Exception as e:
        return {
            "result": 1,
            "message": str(e)
        }

def add_account_list(request, user_id: str, role: list, email: str):
    # 驗證輸入
    if not user_id or not isinstance(role, list):
        return {
            "result": 1,
            "message": "user_id 不能為空，role 必須是列表"
        }

    try:
        # 建立連接
        conn = MySQLAccess.get_connection()
        cursor = conn.cursor()

        # 新增帳號（role 轉成 JSON 字串存入）
        query = "INSERT INTO account_list (user_id, role, email) VALUES (%s, %s, %s)"
        cursor.execute(query, (user_id, json.dumps(role), email))

        # 提交
        conn.commit()
        cursor.close()

        return {
            "result": 0,
            "message": ""
        }

    except Exception as e:
        # user_id 重複時 MySQL 會丟出 IntegrityError，訊息會直接回傳
        return {
            "result": 1,
            "message": str(e)
        }

def get_account_list(request):
    try:
        conn = MySQLAccess.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM account_list"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

         # 處理 role 欄位 - 從 JSON 字符串轉換回 list
        for item in data:
            if isinstance(item['role'], str):
                import json
                item['role'] = json.loads(item['role'])

        return {
            "result": 0,
            "message": "",
            "data": data if data else []
        }
    except Exception as e:
        return {
            "result": 1,
            "message": str(e),
            "data": []
        }

def delete_account_list(request, user_id: str):
    try:
        conn = MySQLAccess.get_connection()
        cursor = conn.cursor()

        # 執行刪除
        query = "DELETE FROM account_list WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        cursor.close()

        return {
            "result": 0,
            "message": ""
        }
    except Exception as e:
        return {
            "result": 1,
            "message": str(e)
        }

def update_account_list(request, old_user_id: str, data: dict):
    # 步驟2：驗證輸入
    if not old_user_id or not data:
        return {
            "result": 1,
            "message": "old_user_id 或 data 不能為空"
        }

    # 步驟3：處理 role
    new_role = data.get('new_role')
    if isinstance(new_role, list):
        new_role = json.dumps(new_role)

    try:
        # 步驟4：建立連接
        conn = MySQLAccess.get_connection()
        cursor = conn.cursor()

        # 步驟5
        query = "UPDATE account_list SET user_id = %s, role = %s, email = %s WHERE user_id = %s"
        cursor.execute(query, (
            data.get('new_user_id'),
            new_role,
            data.get('new_email'),
            old_user_id
        ))

        # 步驟7：提交
        conn.commit()
        cursor.close()
        conn.close()

        # 步驟8：回傳成功
        return {
            "result": 0,
            "message": ""
        }

    except Exception as e:
        # 步驟9：異常處理
        return {
            "result": 1,
            "message": str(e)
        }

def autosave_detect_table(request, uuid: str, data: dict):
    # 驗證輸入
    if not uuid or not isinstance(data, dict):
        return {
            "result": 1,
            "message": "uuid 不能為空，data 必須是字典"
        }

    # 驗證結構：data -> page_number -> table_id -> {座標..., cells: [...]}
    for tables in data.values():
        if not isinstance(tables, dict):
            return {
                "result": 1,
                "message": "data 的 page 內容必須是字典"
            }
        for table in tables.values():
            if not isinstance(table, dict) or not isinstance(table.get('cells', []), list):
                return {
                    "result": 1,
                    "message": "table 內容必須是字典，且 cells 必須是列表"
                }

    conn = None
    try:
        # 建立連接
        conn = MySQLAccess.get_connection()
        cursor = conn.cursor()

        # 開始交易
        conn.start_transaction()

        # 先刪除此 uuid 的舊資料（cell 要先刪，雖然沒有外鍵，順序仍保持一致）
        cursor.execute("DELETE FROM detect_cell WHERE uuid = %s", (uuid,))
        cursor.execute("DELETE FROM detect_table WHERE uuid = %s", (uuid,))

        # 再插入新資料
        table_query = """
            INSERT INTO detect_table
                (uuid, page_number, table_id, upper_left, upper_right, lower_right, lower_left)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cell_query = """
            INSERT INTO detect_cell
                (uuid, page_number, table_id, name, upper_left, upper_right, lower_right, lower_left,
                 start_row, end_row, start_col, end_col, content)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        for page_number, tables in data.items():
            for table_id, table in tables.items():
                cursor.execute(table_query, (
                    uuid, page_number, table_id,
                    table.get('upper_left'), table.get('upper_right'),
                    table.get('lower_right'), table.get('lower_left')
                ))

                for cell in table.get('cells', []):
                    cursor.execute(cell_query, (
                        uuid, page_number, table_id,
                        cell.get('name'),
                        cell.get('upper_left'), cell.get('upper_right'),
                        cell.get('lower_right'), cell.get('lower_left'),
                        cell.get('start_row'), cell.get('end_row'),
                        cell.get('start_col'), cell.get('end_col'),
                        cell.get('content')
                    ))

        # 提交
        conn.commit()
        cursor.close()

        # 返回成功
        return {
            "result": 0,
            "message": ""
        }

    except Exception as e:
        # 失敗時回滾，避免只寫了一半
        if conn is not None:
            conn.rollback()
        return {
            "result": 1,
            "message": str(e)
        }

def get_detect_table(request, uuid: str):
    # 驗證輸入
    if not uuid:
        return {
            "result": 1,
            "message": "uuid 不能為空"
        }

    try:
        # 建立連接
        conn = MySQLAccess.get_connection()
        cursor = conn.cursor(dictionary=True)

        # 查詢 table 與 cell（依 id 排序，還原寫入的順序）
        cursor.execute(
            "SELECT page_number, table_id, upper_left, upper_right, lower_right, lower_left "
            "FROM detect_table WHERE uuid = %s ORDER BY id",
            (uuid,)
        )
        tables = cursor.fetchall()

        cursor.execute(
            "SELECT page_number, table_id, name, upper_left, upper_right, lower_right, lower_left, "
            "start_row, end_row, start_col, end_col, content "
            "FROM detect_cell WHERE uuid = %s ORDER BY id",
            (uuid,)
        )
        cells = cursor.fetchall()
        cursor.close()

        # 檢查結果是否存在
        if not tables:
            return {
                "result": 1,
                "message": "uuid 不存在"
            }

        # 組成 page -> table_id -> {座標..., cells: [...]} 的巢狀字典
        data = {}
        for t in tables:
            page = data.setdefault(t['page_number'], {})
            page[t['table_id']] = {
                "upper_left": t['upper_left'],
                "upper_right": t['upper_right'],
                "lower_right": t['lower_right'],
                "lower_left": t['lower_left'],
                "cells": []
            }

        # 把 cell 放進對應的 table
        for c in cells:
            table = data.get(c['page_number'], {}).get(c['table_id'])
            if table is None:
                continue  # 沒有對應 table 的 cell 略過
            table["cells"].append({
                "name": c['name'],
                "upper_left": c['upper_left'],
                "upper_right": c['upper_right'],
                "lower_right": c['lower_right'],
                "lower_left": c['lower_left'],
                "start_row": c['start_row'],
                "end_row": c['end_row'],
                "start_col": c['start_col'],
                "end_col": c['end_col'],
                "content": c['content']
            })

        # 返回結果
        return {
            "result": 0,
            "message": "",
            "data": data
        }

    except Exception as e:
        return {
            "result": 1,
            "message": str(e)
        }

def get_image_path(request, uuid: str):
    # 驗證
    if not uuid:
        return {
            "result": 1,
            "message": "uuid 不能為空"
        }

    try:
        # 連接資料庫
        conn = MySQLAccess.get_connection()
        cursor = conn.cursor(dictionary=True)

        # 查詢
        query = "SELECT uuid, front_path, back_path FROM image_path WHERE uuid = %s"
        cursor.execute(query, (uuid,))
        result = cursor.fetchone()  # 用 fetchone，不是 fetchall
        cursor.close()

        # 檢查結果是否存在
        if not result:
            return {
                "result": 1,
                "message": "uuid 不存在"
            }

        # 返回
        return {
            "result": 0,
            "message": "",
            "data": result  # result 已經是字典了
        }

    except Exception as e:
        return {
            "result": 1,
            "message": str(e)
        }

def autosave_image_path(request, uuid: str, front_path: str, back_path: str):
    # 驗證輸入
    if not uuid or not front_path or not back_path:
        return {
            "result": 1,
            "message": "uuid、front_path、back_path 都不能為空"
        }

    conn = None
    try:
        # 建立連接
        conn = MySQLAccess.get_connection()
        cursor = conn.cursor()

        # 開始交易（連線是 autocommit=True，需手動開啟，刪除與插入才會一起成功或一起回滾）
        conn.start_transaction()

        # 先刪除舊資料
        delete_query = "DELETE FROM image_path WHERE uuid = %s"
        cursor.execute(delete_query, (uuid,))

        # 再插入新資料
        insert_query = "INSERT INTO image_path (uuid, front_path, back_path) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (uuid, front_path, back_path))

        # 提交
        conn.commit()
        cursor.close()

        # 返回成功
        return {
            "result": 0,
            "message": ""
        }

    except Exception as e:
        # 失敗時回滾，避免只刪了舊資料卻沒寫入新資料
        if conn is not None:
            conn.rollback()
        return {
            "result": 1,
            "message": str(e)
        }

def get_key_value_mapping(request, vendor: str, file_type: str):
    # 驗證輸入
    if not vendor or not file_type:
        return {
            "result": 1,
            "message": "vendor 和 file_type 都不能為空"
        }

    try:
        # 建立連接
        conn = MySQLAccess.get_connection()
        cursor = conn.cursor(dictionary=True)

        # 查詢資料
        query = "SELECT field_name, field_value FROM key_value_mapping WHERE vendor = %s AND file_type = %s"
        cursor.execute(query, (vendor, file_type))
        results = cursor.fetchall()
        cursor.close()

        # 處理結果 - 將平鋪的結果轉換為分組的字典
        data = {}
        for row in results:
            field_name = row['field_name']
            field_value = row['field_value']

            # 如果這個 key 還沒有，就建立一個新列表
            if field_name not in data:
                data[field_name] = []

            # 添加值到列表中
            data[field_name].append(field_value)

        # 返回結果
        return {
            "result": 0,
            "message": "",
            "data": data
        }

    except Exception as e:
        return {
            "result": 1,
            "message": str(e)
        }

def autosave_key_value_mapping(request, data: list):
    # 驗證輸入
    if not data or not isinstance(data, list):
        return {
            "result": 1,
            "message": "data 必須是一個列表"
        }

    # 先驗證所有項目，全部通過才開始寫入，避免寫到一半才發現資料有誤
    for item in data:
        if not isinstance(item, dict) or not item.get('field') or not item.get('fieldvalue') or not item.get('vendor') or not item.get('file_type'):
            return {
                "result": 1,
                "message": "field、fieldvalue、vendor、file_type 都不能為空"
            }

    conn = None
    try:
        # 建立連接
        conn = MySQLAccess.get_connection()
        cursor = conn.cursor()

        # 開始交易，所有項目要嘛全部寫入，要嘛全部不寫
        conn.start_transaction()

        # 處理每個項目
        for item in data:
            field = item.get('field')
            fieldvalue = item.get('fieldvalue')
            vendor = item.get('vendor')
            file_type = item.get('file_type')

            # 先刪除舊資料 (同一個 vendor、file_type、field 的所有值)
            delete_query = "DELETE FROM key_value_mapping WHERE vendor = %s AND file_type = %s AND field_name = %s"
            cursor.execute(delete_query, (vendor, file_type, field))

            # 再插入新資料 (fieldvalue 是一個列表)
            for value in fieldvalue:
                insert_query = "INSERT INTO key_value_mapping (vendor, file_type, field_name, field_value) VALUES (%s, %s, %s, %s)"
                cursor.execute(insert_query, (vendor, file_type, field, value))

        # 提交
        conn.commit()
        cursor.close()

        # 返回成功
        return {
            "result": 0,
            "message": ""
        }

    except Exception as e:
        # 任何一步失敗都回滾，不留半套資料
        if conn is not None:
            conn.rollback()
        return {
            "result": 1,
            "message": str(e)
        }
