from flask import jsonify, request, make_response
from flask_restful import Resource
from marshmallow import Schema, fields
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from functools import wraps

from administrator.main import info_administrator

from config import redis_conn
from helper import ambil_random
from .models import db_hs, radius_server, hotspot_profile
from .logging import hotspotprofileradiusserver_logging_create, hotspotprofileradiusserver_logging_update, hotspotprofileradiusserver_logging_delete
from .hotspot_profile import HotspotprofileSchema

redcon = redis_conn()

def check_header(f):
    @wraps(f)
    def check_authorization(*args,**kwargs):
        try:            
            authorization = 'admin_access_token:'+request.headers['Authorization']
            redcon.get(authorization).decode('utf-8')
            if redcon == None:
                return jsonify({"message": "Unauthorized"}), 401
        except:
            return jsonify({"message": "Unauthorized"}), 401
        resp = make_response(f(*args, **kwargs))
        return resp
    return check_authorization

def generate_secret():
    list_keys = []
    for x in range(5):
        list_keys.append(str(ambil_random(5)).upper())
        secret_key = '-'.join([str(item) for item in list_keys])
    
    i = False
    while i == False:
        secret_key_exists = radius_server.query.filter_by(secret_key=secret_key).first()
        if secret_key_exists is None:
            i = True
        else:
            list_keys = []
            for x in range(5):
                list_keys.append(str(ambil_random(5)).upper())
                secret_key = '-'.join([str(item) for item in list_keys])
    return secret_key

class HotspotprofileradiusSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"ID Radius Server"})
    host = fields.String(required=True, metadata={"description":"URL Host Radius server"})
    port = fields.Integer(required=True, metadata={"description":"Port Radius Server"})
    secret_key = fields.String(required=True, metadata={"description":"Secret keys for "})
    profile_id = fields.Integer(required=True, metadata={"description":"ID Hotspot profile"})
    profile_info = fields.Nested(HotspotprofileSchema)
    
class HotspotprofileradiusSchemaInfo(Schema):
    id = fields.Integer(required=True, metadata={"description":"ID Radius Server"})
    host = fields.String(required=True, metadata={"description":"URL Host Radius server"})
    port = fields.Integer(required=True, metadata={"description":"Port Radius Server"})
    #secret_key = fields.String(required=True, metadata={"description":"Secret keys for "})
    profile_id = fields.Integer(required=True, metadata={"description":"ID Hotspot profile"})
    profile_info = fields.Nested(HotspotprofileSchema)

class HotspotprofileradiusSchemaCreate(Schema):
    host = fields.String(required=True, metadata={"description":"URL Host Radius server"})
    port = fields.Integer(required=True, metadata={"description":"Port Radius Server"})
    profile_id = fields.Integer(required=True, metadata={"description":"ID Hotspot profile"})

class HotspotprofileradiusSchemaUpdate(Schema):
    id = fields.Integer(required=True, metadata={"description":"ID Radius Server"})
    host = fields.String(required=True, metadata={"description":"URL Host Radius server"})
    port = fields.Integer(required=True, metadata={"description":"Port Radius Server"})
    
class HotspotprofileradiusSchemaList(Schema):
    data = fields.List(fields.Nested(HotspotprofileradiusSchemaInfo))

class HotspotprofileradiusSchemaDelete(Schema):
    id = fields.Integer(required=True, metadata={"description":"ID Radius Server"})

#CRUD
class HotspotprofileradiusAPI(MethodResource, Resource):
    @doc(description="Create Hotspot profile Radius Server", tags=['Hotspot Profile'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(HotspotprofileradiusSchemaCreate, location=('json'))
    @marshal_with(HotspotprofileradiusSchema)
    @check_header
    def post(self, **kwargs):
        try:
            host = kwargs['host']
            profile_id = kwargs['id']

            port = 5000
            try:
                port = kwargs['port']
            except:
                port = 5000
                
            secret_keys = generate_secret()
            new_radius = radius_server(host, secret_keys, profile_id, port)
            db_hs.session.add(new_radius)
            db_hs.session.commit()
            data = new_radius.get_data()

            data_profile = hotspot_profile.query.filter_by(id=data['profile_id']).first()
            data['profile_info'] = data_profile.get_data()
            
            #Logging
            info_admin = info_administrator()
            accessed = {'ip':request.remote_addr, 'id_token': info_admin['request_id']}
            new_log = hotspotprofileradiusserver_logging_create(accessed, str(data), data['id'], info_admin['admin_id'])
            if new_log == False:
                print("Logging Failed")

            return jsonify(data)

        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        finally:
            db_hs.session.expire_all()
    
    @doc(description="List Hotspot Profile Radius server", tags=['Hotspot Profile'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @marshal_with(HotspotprofileradiusSchemaList)
    @check_header
    def get(self):
        try:
            radiusserver_list = []
            radiusservers = radius_server.query.order_by(radius_server.id.asc()).all()
            for _radiusservers in radiusservers:
                info_hsprofile = hotspot_profile.query.filter_by(id=_radiusservers.profile_id).first()
                data_hsprofile = info_hsprofile.get_data()
                __radiusservers = {
                    'id' : _radiusservers.id,
                    'host' : _radiusservers.host,
                    'port' : _radiusservers.port,
                    'profile_id': _radiusservers.profile_id,
                    'profile_info' : data_hsprofile
                }
                radiusserver_list.append(__radiusservers)
            data = {'data':radiusserver_list}
            return jsonify(data)
        
        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        finally:
            db_hs.session.expire_all()

    @doc(description="Update Hotspot profile Radius Server", tags=['Hotspot Profile'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(HotspotprofileradiusSchemaCreate, location=('json'))
    @marshal_with(HotspotprofileradiusSchemaInfo)
    @check_header
    def put(self, **kwargs):
        try:
            id = kwargs['id']
            host = kwargs['host']
            port = kwargs['port']

            get_radiusserver = radius_server.query.filter_by(id=id).first()
            if get_radiusserver:
                get_radiusserver.host = host
                get_radiusserver.port = port
                db_hs.session.commit()
                data_radius = get_radiusserver.get_data()
                data_profile = hotspot_profile.query.filter_by(id=data_radius['profile_id']).first()
                data = {
                    'id': data_radius['id'],
                    'host': data_radius['host'],
                    'port': data_radius['port'],
                    'profile_id': data_radius['profile_id'],
                    'profile_info': data_profile
                }

                #logging
                info_admin = info_administrator()
                accessed = {'ip':request.remote_addr, 'id_token': info_admin['request_id']}
                new_log = hotspotprofileradiusserver_logging_update(accessed, str(data), data['id'], info_admin['admin_id'])
                if new_log == False:
                    print("Logging Failed")

                return jsonify(data)

            return jsonify({"message": "ID Not Found"}), 404

        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        finally:
            db_hs.session.expire_all()   

    @doc(description="Delete Hotspot profile", tags=['Hotspot Profile'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(HotspotprofileradiusSchemaDelete, location=('json'))
    @marshal_with(HotspotprofileradiusSchemaInfo)
    @check_header
    def delete(self, **kwargs):
        try:
            id = kwargs['id']
            get_radiusserver = radius_server.query.filter_by(id=id).first()
            if get_radiusserver:
                old_data = get_radiusserver.get_data()
                db_hs.session.delete(get_radiusserver)
                db_hs.session.commit()

                #logging
                info_admin = info_administrator()
                accessed = {'ip':request.remote_addr, 'id_token': info_admin['request_id']}
                new_log = hotspotprofileradiusserver_logging_delete(accessed, str(old_data), old_data['id'], info_admin['admin_id'])
                if new_log == False:
                    print("Logging Failed")

                return jsonify(old_data)

            return jsonify({"message": "ID Not Found"}), 404
        
        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        finally:
            db_hs.session.expire_all()   
