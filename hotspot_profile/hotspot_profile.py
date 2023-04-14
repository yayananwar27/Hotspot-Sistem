from flask import jsonify, request, make_response
from flask_restful import Resource
from marshmallow import Schema, fields
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from functools import wraps

from administrator.main import info_administrator

from config import redis_conn
from .models import db_hs, hotspot_profile
from .logging import hotspotprofile_logging_create, hotspotprofile_logging_delete, hotspotprofile_logging_update
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

class HotspotprofileSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"ID Hotspot profile"})
    name = fields.String(required=True, metadata={"description":"Name Hotspot profile"})

class HotspotprofileSchemaList(Schema):
    data = fields.List(fields.Nested(HotspotprofileSchema))

class HotspotprofileSchemaCreate(Schema):
    name = fields.String(required=True, metadata={"description":"Name Hotspot profile"})

class HotspotprofileSchemaDelete(Schema):
    id = fields.Integer(required=True, metadata={"description":"ID Hotspot profile"})

#CRUD
class HotspotprofileAPI(MethodResource,  Resource):
    @doc(description="Create Hotspot profile", tags=['Hotspot Profile'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(HotspotprofileSchemaCreate, location=('json'))
    @marshal_with(HotspotprofileSchema)
    @check_header
    def post(self, **kwargs):
        try:
            name = kwargs['name']
            name_exists = hotspot_profile.query.filter_by(name=name).first()
            if name_exists:
                return jsonify({"message": "Name already exists"}), 409
            
            new_profile = hotspot_profile(name)
            db_hs.session.add(new_profile)
            db_hs.session.commit()

            data = new_profile.get_data()

            #Logging
            info_admin = info_administrator()
            accessed = {'ip':request.remote_addr, 'id_token': info_admin['request_id']}
            new_log = hotspotprofile_logging_create(accessed, str(data), data['id'], info_admin['admin_id'])
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

    @doc(description="List Hotspot profile", tags=['Hotspot Profile'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @marshal_with(HotspotprofileSchemaList)
    @check_header
    def get(self):
        try:
            hotspotprofile_list = []
            hotspotprofiles = hotspot_profile.query.order_by(hotspot_profile.name.asc()).all()
            for _hotspotprofiles in hotspotprofiles:
                __hotspotprofiles = {
                    "id":_hotspotprofiles.id,
                    "name":_hotspotprofiles.name
                }
                hotspotprofile_list.append(__hotspotprofiles)

            data = {'data':hotspotprofile_list}
            return jsonify(data)
        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        finally:
            db_hs.session.expire_all()
    
    @doc(description="Update Hotspot profile", tags=['Hotspot Profile'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(HotspotprofileSchema, location=('json'))
    @marshal_with(HotspotprofileSchema)
    @check_header
    def put(self, **kwargs):
        try:
            id = kwargs['id']
            name = kwargs['name']

            get_profile = hotspot_profile.query.filter_by(id=id).first()
            if get_profile:
                get_profile.name = name
                db_hs.session.commit()
                data = get_profile.get_data()

                #logging
                info_admin = info_administrator()
                accessed = {'ip':request.remote_addr, 'id_token': info_admin['request_id']}
                new_log = hotspotprofile_logging_update(accessed, str(data), data['id'], info_admin['admin_id'])
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
    @use_kwargs(HotspotprofileSchemaDelete, location=('json'))
    @marshal_with(HotspotprofileSchema)
    @check_header
    def delete(self, **kwargs):
        try:
            id = kwargs['id']
            get_profile = hotspot_profile.query.filter_by(id=id).first()
            if get_profile:
                old_data = get_profile.get_data()
                db_hs.session.delete(get_profile)
                db_hs.session.commit()

                #logging
                info_admin = info_administrator()
                accessed = {'ip':request.remote_addr, 'id_token': info_admin['request_id']}
                new_log = hotspotprofile_logging_delete(accessed, str(old_data), old_data['id'], info_admin['admin_id'])
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

class InfoHotspotprofileAPI(MethodResource,  Resource):
    @doc(description="Info Hotspot profile", tags=['Hotspot Profile'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @marshal_with(HotspotprofileSchema)
    @check_header
    def get(self, id):
        try:
            get_data = hotspot_profile.query.filter_by(id=id).first()
            if get_data:
                data = get_data.get_data()
                return jsonify(data)
            return jsonify({"message": "Not Found"}), 404
        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        finally:
            db_hs.session.expire_all()   