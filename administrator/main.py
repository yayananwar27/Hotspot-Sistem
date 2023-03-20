from flask import jsonify, request, make_response
from flask_restful import Resource
from marshmallow import Schema, fields
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from functools import wraps

from config import redis_conn
from werkzeug.security import generate_password_hash
from .models import db_admin, administrator, admin_token
from .logging import administrator_logging_create, administrator_logging_update, administrator_logging_delete

import ast

redcon = redis_conn()


def check_header(f):
    @wraps(f)
    def check_authorization(*args,**kwargs):
        try:
            #try:
            #    authorization = request.headers['x-api-token']
            #    if authorization != None:
            #        token_exists = admin_token.query.filter_by(token_value=authorization).first()
            #        if token_exists == None:
            #            return jsonify({"message": "Unauthorized"}), 401
            #        resp = make_response(f(*args, **kwargs))
            #        return resp        
            #except:
            #    authorization = 'admin_access_token:'+request.headers['Authorization']
            
            authorization = 'admin_access_token:'+request.headers['Authorization']
            redcon.get(authorization).decode('utf-8')
            if redcon == None:
                return jsonify({"message": "Unauthorized"}), 401
        except:
            return jsonify({"message": "Unauthorized"}), 401
        resp = make_response(f(*args, **kwargs))
        return resp
    return check_authorization

#Fungsi Info Administrator dari access_token
def info_administrator():
    token=request.headers['Authorization']
    authorization = 'admin_access_token:'+token
    data = redcon.get(authorization).decode('utf-8')
    result = ast.literal_eval(data)
    request_id = admin_token.query.filter_by(token_value=token).first()
    result['request_id'] = request_id.request_id
    return result

#User Schema
class AdministratorSchema(Schema):
    id = fields.String(required=True, metadata={"description":"ID Administrator"})
    email = fields.String(metadata={"description":"E-mail untuk Administrator"})
    password = fields.String(metadata={"description":"Password untuk Administrator"})
    fullname = fields.String(metadata={"description":"fullname untuk Administrator"})
    active = fields.Boolean(metadata={"description":"administrator status True/False"})

#Class schema Create Administrator
class AdministratorSchemaCreate(Schema):
    email = fields.String(required=True, metadata={"description":"E-mail untuk Username"})
    password = fields.String(required=True, metadata={"description":"Password untuk Administrator"})
    fullname = fields.String(metadata={"description":"Fullname Administrator"})

class RespAdministratorSchemaCreate(Schema):
    id = fields.String(metadata={"description":"ID Administrator"})
    email = fields.String(required=True, metadata={"description":"E-mail untuk Username"})
    fullname = fields.String(metadata={"description":"Fullname Administrator"})
    created_at = fields.DateTime(metadata={"description":"Date Time created"})
    active = fields.Boolean(metadata={"description":"administrator status True/False"})

#Class Schema list Administrator
class AdministratorSchemaList(Schema):
    data = fields.List(fields.Nested(RespAdministratorSchemaCreate))

#Class schema Delete Administrator
class AdministratorSchemaDelete(Schema):
    id = fields.String(required=True, metadata={"description":"ID Administrator"})

class RespAdministratorSchemaDelete(Schema):
    message = fields.String(required=True, metadata={"description":"message"})
    old_data = fields.Nested(RespAdministratorSchemaCreate)

#Class CRUD Administrator
class AdministratorAPI(MethodResource, Resource):
    #@doc(description='Create Administrator', tags=['Administrator'])
    @doc(description='Create Administrator', tags=['Administrator'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(AdministratorSchemaCreate, location=('json'))
    @marshal_with(RespAdministratorSchemaCreate)
    @check_header
    #Create Operator
    def post(self, **kwargs):
        try:
            email = kwargs['email']
            password = kwargs['password']
            fullname = kwargs['fullname']

            administrator_exists = administrator.query.filter_by(email=email).first() is not None

            if administrator_exists:
                return jsonify({"message": "Administrator already exists"}), 409
            
            hashed_password = generate_password_hash(password)
            new_administrator = administrator(email, hashed_password, fullname, True)
            db_admin.session.add(new_administrator)
            db_admin.session.commit()

            data = {
                'id' : new_administrator.id,
                'email' : new_administrator.email, 
                'fullname' : new_administrator.fullname,
                'created_at' : new_administrator.created_at,
                'active' : new_administrator.active
                }

            #Logging
            info_admin = info_administrator()
            accessed = {'ip':request.remote_addr, 'id_token': info_admin['admin_id']}
            new_log = administrator_logging_create(str(accessed), str(data), data['id'], info_admin['admin_id'])
            if new_log == False:
                print("Logging Failed")

            return jsonify(data)

        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        
    @doc(description='List Administrator', tags=['Administrator'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @marshal_with(AdministratorSchemaList)
    @check_header
    def get(self, **kwargs):
        try:
            administrators = administrator.query.order_by(administrator.email.asc()).all()
            administrators_list = []

            for _administrator in administrators:
                __administrator = {
                    'id' : _administrator.id,
                    'email' : _administrator.email,
                    'fullname' : _administrator.fullname,
                    'created_at' : _administrator.created_at, 
                    'active':_administrator.active
                    }
                administrators_list.append(__administrator)

            data = {'data':administrators_list}

            return jsonify(data)
        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
    
    @doc(description='Update Administrator', tags=['Administrator'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(AdministratorSchema, location=('json'))
    @marshal_with(RespAdministratorSchemaCreate)
    @check_header
    def put(self, **kwargs):
        try:
            id = kwargs['id']
            try:
                email = kwargs['email']
            except:
                email = None
            try:
                password = kwargs['password']
            except:
                password = None
            try:
                fullname = kwargs['fullname']
            except:
                fullname = None
            try:
                active = kwargs['active']
            except:
                active = None
            
            get_administrator = administrator.query.filter_by(id=id).first()

            if get_administrator:
                if email != None:
                    get_administrator.email = email
                    db_admin.session.commit()
                if password != None:
                    hashed_password = generate_password_hash(password)
                    get_administrator.password = hashed_password
                    db_admin.session.commit()
                if fullname != None:
                    get_administrator.fullname = fullname
                    db_admin.session.commit()
                if active != None:
                    get_administrator.active = active
                    db_admin.session.commit()

                get_administrator = administrator.query.filter_by(id=id).first()
                data = {
                    'id' : get_administrator.id,
                    'email' : get_administrator.email,
                    'fullname' : get_administrator.fullname,
                    'crated_at' : get_administrator.created_at,
                    'active' : get_administrator.active
                }

                #Logging
                info_admin = info_administrator()
                accessed = {'ip':request.remote_addr, 'id_token':info_admin['request_id']}
                new_log = administrator_logging_update(accessed, str(data), data['id'], info_admin['admin_id'])
                if new_log == False:
                    print("Logging Failed")

                return jsonify(data)

            return jsonify({"message": "User Not exists"}), 404


        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        
    @doc(description='Delete Administrator', tags=['Administrator'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(AdministratorSchemaDelete, location=('json'))
    @marshal_with(RespAdministratorSchemaCreate)
    @check_header
    def delete(self, **kwargs):
        try:
            id = kwargs['id']
            
            get_administrator = administrator.query.filter_by(id=id).first()

            if get_administrator:
                old_data = {
                    'id' : get_administrator.id,
                    'email' : get_administrator.email,
                    'fullname' : get_administrator.fullname,
                    'crated_at' : get_administrator.created_at,
                    'active' : get_administrator.active
                }
                
                db_admin.session.delete(get_administrator)
                db_admin.session.commit()

                data = {'message':'success', 'old_data' : old_data}
                
                #Logging
                info_admin = info_administrator()
                accessed = {'ip':request.remote_addr, 'id_token':info_admin['request_id']}
                new_log = administrator_logging_delete(accessed, str(old_data), old_data['id'], info_admin['admin_id'])
                if new_log == False:
                    print("Logging Failed")
                
                return jsonify(data)

            return jsonify({"message": "User Not exists"}), 404


        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone

#Class CRUD Administrator
class InfoAdministratorAPI(MethodResource, Resource):
    @doc(description='Administrato Info', tags=['Administrator'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @marshal_with(AdministratorSchema)
    @check_header
    def get(self, id):
        try:
            administrators = administrator.query.filter_by(id=id).first()
            
            if administrators:
                _administrators = {
                    'id' : administrators.id,
                    'email' : administrators.email,
                    'fullname' : administrators.fullname,
                    'created_at' : administrators.created_at, 
                    'active':administrators.active
                }
                return jsonify(_administrators)
            
            return jsonify({"message": "Not Found"}), 404
        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone


#Class untuk info administrator berdasarkan access_token
class MeAdministratorAPI(MethodResource, Resource):
    @doc(description='Me Administrator', tags=['Administrator Authorization'], params={'Authorization': {'in': 'header', 'description': 'An authorization token'}})
    @check_header
    def get(self):
        result = info_administrator()
        return jsonify(result)
    