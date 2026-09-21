from apis.account.model import *
from apis.account.module import *
from flask import session
from base_api import CustomResource

ROLE_ADMIN = "Admin"


@api.route("/test")
class Login2(CustomResource):
    allow_roles = [ROLE_ADMIN]
    def post(self):
        print(api.payload)
        return "OK"


@api.route("/login")
class Login(CustomResource):
    @api.expect(account_input_payload)
    @api.marshal_with(account_output_payload)
    def post(self):
        session["roles"] = [ROLE_ADMIN]
        data = api.payload
        return Account.login(username=data["username"], passwd=data["passwd"])