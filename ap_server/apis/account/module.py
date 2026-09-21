
from utils.orcl_utils import OracleAccess

class Account(object):
    @staticmethod
    def login(username, passwd):
        # TODO
        raw = OracleAccess.query("select * from test")
        return {
            "data": "登入成功",
            "test": raw[0][0]
        }