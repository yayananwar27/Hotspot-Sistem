from marshmallow import Schema, fields
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, request, make_response
from flask_apispec.views import MethodResource
from flask_restful import Resource
from functools import wraps
from config import redis_conn
from .models import admin_token, administrator

redcon = redis_conn()

from .logging import authentication_logging_logout
from helper import get_datetime

def check_header(f):
    @wraps(f)
    def check_authorization(*args,**kwargs):
        try:
            authorization = 'admin_access_token:'+str(request.headers['Authorization'])
            redcon.get(authorization).decode('utf-8')
            if redcon == None:
                return jsonify({"message": "Unauthorized"}), 401
        except:
            return jsonify({"message": "Unauthorized"}), 401
        resp = make_response(f(*args, **kwargs))
        return resp
    return check_authorization

class AdministratorSchemaLogout(Schema):
    refresh_token = fields.String(required=True, metadata={"description":"Refresh Token to Delete"})
    device = fields.String(metadata={"description":"Device Detect Description From Front End"})

class RespAdministratorLogot(Schema):
    messages = fields.Boolean(metadata={"description":"administrator access True/False"})

class LogoutOperatorsAPI(MethodResource, Resource):
    @doc(description='Logout Administrator', tags=['Administrator Authorization'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(AdministratorSchemaLogout, location=('json'))
    @marshal_with(RespAdministratorLogot)
    @check_header
    def post(self, **kwargs):
        try:
            access_token = request.headers['access_token']
            refresh_token = kwargs['refresh_token']
            device = 'Null'
            try:
                device = kwargs['device']
            except:
                device = 'Null'

            dt_now = get_datetime()

            acc_admin_id_exists = admin_token.query.filter_by(token_value=access_token).first()
            ref_admin_id_exists = admin_token.query.filter_by(token_value=refresh_token).first()

            if acc_admin_id_exists.admin_id != ref_admin_id_exists.admin_id:
                return jsonify({"message": "Unauthorized"}), 401
            
            redcon.delete('admin_access_token:'+access_token)
            redcon.delete('admin_refresh_token:'+refresh_token)

            accessed = {'ip':request.remote_addr, 'device':device}
            administrator_exists = administrator.query.filter_by(id=acc_admin_id_exists.admin_id).first()
            payload = 'Logout Administartor : '+administrator_exists.email+':'+administrator_exists.fullname+'/'+acc_admin_id_exists.token_value+':'+ref_admin_id_exists.token_value
            token_data = {'access_token':acc_admin_id_exists.request_id, 'refresh_token':ref_admin_id_exists.request_id}
            new_log = authentication_logging_logout(str(accessed), payload, str(token_data), administrator_exists.id)
            if new_log == False:
                print("Logging Failed")
            
            data = {'message':'success'}

            return jsonify(data)

        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone