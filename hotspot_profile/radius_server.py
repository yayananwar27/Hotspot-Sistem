from flask import jsonify, request, make_response
from flask_restful import Resource
from marshmallow import Schema, fields
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from functools import wraps

from administrator.main import info_administrator

from config import redis_conn
from .models import db_hs, radius_server
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

class HotspotprofileradiusSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"ID Radius Server"})
    host = fields.String(required=True, metadata={"description":"URL Host Radius server"})
    port = fields.Integer(required=True, metadata={"description":"Port Radius Server"})
    secret_key = fields.String(required=True, metadata={"description":"Secret keys for "})
    profile_id = fields.Integer(required=True, metadata={"description":"ID Hotspot profile"})

class HotspotprofileradiusSchemaInfo(Schema):
    id = fields.Integer(required=True, metadata={"description":"ID Radius Server"})
    host = fields.String(required=True, metadata={"description":"URL Host Radius server"})
    port = fields.Integer(required=True, metadata={"description":"Port Radius Server"})
    secret_key = fields.String(required=True, metadata={"description":"Secret keys for "})
    profile_id = fields.Integer(required=True, metadata={"description":"ID Hotspot profile"})
    profile_info = fields.Nested(HotspotprofileSchema)

class HotspotprofileradiusSchemaCreate(Schema):
    host = fields.String(required=True, metadata={"description":"URL Host Radius server"})
    port = fields.Integer(required=True, metadata={"description":"Port Radius Server"})
    profile_id = fields.Integer(required=True, metadata={"description":"ID Hotspot profile"})

class HotspotprofileradiusSchemaList(Schema):
    data = fields.List(fields.Nested(HotspotprofileradiusSchemaInfo))

class HotspotprofileradiusSchemaDelete(Schema):
    id = fields.Integer(required=True, metadata={"description":"ID Radius Server"})

#CRUD
class HotspotprofileradiusAPI(MethodResource, Resource):
    @doc(description="Create Hotspot profile Radius", tags=['Hotspot Profile'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(HotspotprofileradiusSchemaCreate, location=('json'))
    @marshal_with(HotspotprofileradiusSchemaInfo)
    @check_header
    def post(self, **kwargs):
        try:
            host = kwargs['host']
            profile_id = kwargs['id']

            secret_key = ''
            port = 5000
            try:
                port = kwargs['port']
            except:
                port = 5000
            new_radius = radius_server

        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        finally:
            db_hs.session.expire_all()