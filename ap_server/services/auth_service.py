from base_api import MySQLAccess

def forget(request, user_id: str):
    if user_id:
        return {
            "result": 0,
            "message": ""
        }
    return {
        "result": 1,
        "message": "invalid user id"
    }

def add_account_list(request, user_id: str, role: list, email: str):
    return {
        "result": 0,
        "message": ""
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
