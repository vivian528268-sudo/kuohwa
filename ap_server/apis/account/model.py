from flask_restplus import Namespace, Resource, fields, model

api = Namespace("account", description=u"帳號及權限管理")


base_input_payload = api.model(u'基礎輸入參數定義', {
    'result': fields.Integer(required=True, default=0),
    'message': fields.String(required=True, default=""),
})


account_input_payload = api.model(u'帳號input', {
    'username': fields.String(required=True, example="tami"),
    'passwd': fields.String(required=True, example="tami")
})

account_output_payload = api.clone(u'帳號output', base_input_payload, {
    'data': fields.String(required=True),
    "test": fields.String(required=True)
})

