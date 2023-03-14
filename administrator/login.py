from marshmallow import Schema, fields
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, request
from flask_apispec.views import MethodResource
from flask_restful import Resource
from werkzeug.security import check_password_hash, generate_password_hash

from .models import db_admin, administrator, admin_token
from auth_token import create_token
from helper import get_datetime
from config import redis_conn

from .logging import authentication_logging_login, authentication_logging_login_ref

redcon = redis_conn()

#Bagian Mekanisme Login
class AdministratorSchemaLogin(Schema):
    email = fields.String(required=True, metadata={"description":"E-mail Administrator"})
    password = fields.String(required=True, metadata={"description":"Password Administrator"})
    remember = fields.Boolean(metadata={"description":"administrator access True/False"})
    #device = fields.String(metadata={"description":"Device Detect Description From Front End"})

class RespAdministratorLogin(Schema):
    id = fields.String(required=True, metadata={"description":"Unique ID Username"})
    email = fields.String(metadata={"description":"E-mail untuk Username"})
    fullname = fields.String(metadata={"description":"Fullname Administrator"})
    active = fields.Boolean(metadata={"description":"administrator access True/False"})
    access_token = fields.String(metadata={"description":"access token"})
    expired_access = fields.DateTime(metadata={"description":"Token Access Expired"})
    refresh_token = fields.String(metadata={"description":"refresh token"})
    expired_refresh = fields.DateTime(metadata={"description":"Token Refresh Expired"})

class LoginOperatorsAPI(MethodResource, Resource):
    @doc(description='Login Administrator', tags=['Administrator Authorization'])
    @use_kwargs(AdministratorSchemaLogin, location=('json'))
    @marshal_with(RespAdministratorLogin)
    def post(self, **kwargs):
        try:
            #ambil kwargs
            email = kwargs['email']
            password = kwargs['password']
            device = request.headers.get('User-Agent')

            #try:
            #    device = kwargs['device']
            #except:
            #    device = 'Null'

            remember = False
            try:
                remember = kwargs['remember']
            except:
                remember = False
        
            #check dari db
            administrator_exists = administrator.query.filter_by(email=email).first()

            if administrator_exists is None:
                print("Administrator Not Exists")
                return jsonify({"message": "Unauthorized"}), 401
            
            if not check_password_hash(administrator_exists.password, password):
                print("Administrator {} Login Wrong password".format(email))
                return jsonify({"message": "Unauthorized"}), 401
            
            if administrator_exists.active == False:
                print("Administrator {} is Disable".format(email))
                return jsonify({"message": "Unauthorized"}), 401
            
            #ambil datetime dan generete tokennya
            dt_now = get_datetime()
            #_expaccess = int(dt_now.unix()+(60*60))
            _expaccess = int(dt_now.unix()+(60*5))
            access_payload = {'admin_id' : administrator_exists.id, 'type':'access_token', 'expired':_expaccess, 'device':device}
            access_token = create_token(access_payload)
            access_token = access_token.get_token()
            
            if remember == True:
                _exprefresh = int(dt_now.unix()+(60*60*24*30))
                refresh_payload = {'admin_id' : administrator_exists.id, 'type':'refresh_token', 'expired':_exprefresh, 'device':device}
                refresh_token = create_token(refresh_payload)
                refresh_token = refresh_token.get_token()
            else:
                #_exprefresh = int(dt_now.unix()+(60*60*24))
                _exprefresh = int(dt_now.unix()+(60*10))
                refresh_payload = {'admin_id' : administrator_exists.id, 'type':'refresh_token', 'expired':_exprefresh, 'device':device}
                refresh_token = create_token(refresh_payload)
                refresh_token = refresh_token.get_token()

            #Memasukkan access_token ke redis dan DB token
            redcon.set(str('admin_access_token:'+access_token), str(access_payload))
            new_token = admin_token(administrator_exists.id, 'access_token', access_token, _expaccess, device)
            db_admin.session.add(new_token)
            db_admin.session.commit()
            #Memasukkan access token ke Log Admin
            new_token_data = new_token.get_data()
            accessed = {'ip':request.remote_addr, 'device':device}
            new_log = authentication_logging_login(str(accessed), str(access_payload), new_token_data['request_id'], administrator_exists.id)
            if new_log == False:
                print("Logging Failed")

            #Memasukkan refresh_token ke redis dan DB token
            redcon.set(str('admin_refresh_token:'+access_token), str(refresh_payload))
            new_token_ref = admin_token(administrator_exists.id, 'refresh_token', refresh_token, _exprefresh, device)
            db_admin.session.add(new_token_ref)
            db_admin.session.commit()
            #Memasukkan refresh token ke Log Admin
            new_token_data = new_token_ref.get_data()
            new_log_ref = authentication_logging_login(str(accessed), str(refresh_payload), new_token_data['request_id'], administrator_exists.id)
            if new_log_ref == False:
                print("Logging Failed")


            data = {
                'id' : administrator_exists.id,
                'email' : administrator_exists.email,
                'fullname' : administrator_exists.fullname,
                'active' : administrator_exists.active,
                'access_token' : access_token,
                'expired_access' : dt_now.unix_to_datetime(_expaccess),
                'refresh_token' : refresh_token,
                'expired_refresh' : dt_now.unix_to_datetime(_exprefresh)
            }
            return jsonify(data)

        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone