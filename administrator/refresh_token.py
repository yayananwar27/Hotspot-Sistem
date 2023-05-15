from marshmallow import Schema, fields
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask_restful import Resource
from flask import jsonify, request

from .models import admin_token, administrator, db_admin
from config import redis_conn
from auth_token import create_token2, create_token_jwt
from .logging import authentication_logging_refreshtoken

import ast

redcon = redis_conn()

def regenerate_token():
    token = str(create_token2(256))
    i = False
    while i == False:
        token_exsists = admin_token.query.filter_by(token_value=token).first()
        if token_exsists is None:
            i = True
        else:
            i = False
            token = str(create_token2(256))
    return token


#Bagian Mekanisme Refresh Access token
class AdministratorSchemaRefreshToken(Schema):
    refresh_token = fields.String(required=True, metadata={"description":"Refresh token"})
    #device = fields.String(metadata={"description":"Device Detect Description From Front End"})

class RespAdministratorRefreshToken(Schema):
    access_token = fields.String(metadata={"description":"access token"})
    expired_access = fields.DateTime(metadata={"description":"Token Access Expired"})


class AdministratorRefreshToken(MethodResource, Resource):
    @doc(description='Refresh Token Administrator', tags=['Administrator Authorization'])
    @use_kwargs(AdministratorSchemaRefreshToken, location=('json'))
    @marshal_with(RespAdministratorRefreshToken)
    def post(self, **kwargs):
        try:
            from helper import get_datetime
            refresh_token = kwargs['refresh_token']
            #device = kwargs['device']
            device = request.headers.get('User-Agent')

            #verifikasi refresh token
            authorization = 'admin_refresh_token:'+refresh_token
            
            try:
                data = redcon.get(authorization).decode('utf-8')
            except:
                data = None
            if data == None:
                return jsonify({"message": "Unauthorized"}), 401
            
            result = ast.literal_eval(data)
            if result['device'] != device:
                return jsonify({"message": "Forbidden"}), 403
            request_id = admin_token.query.filter_by(token_value=refresh_token).first()
            result['request_id'] = request_id.request_id
            administrator_exists = administrator.query.filter_by(id=result['admin_id']).first()
            #ambil datetime dan generete tokennya
            dt_now = get_datetime()
            _expaccess = int(dt_now.unix()+(60*5))
            access_payload = {'admin_id' : result['admin_id'], 'name': administrator_exists.email, 'type':'access_token', 'expired':_expaccess, 'device':device}
            #access_token = regenerate_token()
            access_token = create_token_jwt(access_payload)
            access_token = access_token.get_token()

            #Memasukkan access_token ke redis dan DB token
            redcon.set(str('admin_access_token:'+access_token), str(access_payload))
            new_token = admin_token(result['admin_id'], 'access_token', access_token, _expaccess, device)
            db_admin.session.add(new_token)
            db_admin.session.commit()
            #Memasukkan access token ke Log Admin
            new_token_data = new_token.get_data()
            accessed = {'ip':request.remote_addr, 'device':device}
            new_log = authentication_logging_refreshtoken(str(accessed), str(access_payload), new_token_data['request_id'], result['admin_id'])
            if new_log == False:
                print("Logging Failed")

            data = {
                'access_token' : access_token,
                'expired_access' : dt_now.unix_to_datetime(_expaccess),
            }
            return jsonify(data)

        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        finally:
            db_admin.session.expire_all()