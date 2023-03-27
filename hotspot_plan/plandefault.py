from flask import jsonify, request, make_response
from flask_restful import Resource
from marshmallow import Schema, fields
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from functools import wraps
from secrets import token_hex
from administrator.main import info_administrator

from config import redis_conn
from .models import db_plan, plan_default, plan_type
from .logging import plandefault_logging_create, plandefault_logging_update, plandefault_logging_delete

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

def get_uuid(x : int):
    return token_hex(x)

def id_plandefault():
    id = str(get_uuid(8))
    i = False
    while i == False:
        id_exists = plan_default.query.filter_by(id=id).first()
        if id_exists is None:
            i = True
        else:
            i = False
            id = str(get_uuid(8))
    return id

#plantype schema
class HotspotplandefaultSchema(Schema):
    id = fields.String(required=True, metadata={"description":"ID Plan Type"})
    name = fields.String(required=True, metadata={"description":"Name Plan Type"})
    uptime = fields.Integer(metadata={"description":"Total Uptime in second"})
    expired = fields.Integer(metadata={"description":"Epoch Unix expired time"})
    price = fields.Integer(metadata={"description":"price in integer"})
    kuota = fields.Integer(metadata={"description":"Total Kuota in Megabyte MB"})
    limit_shared = fields.Integer(metadata={"description":"Max simultaneous Use"})
    type_id = fields.Integer(metadata={"description":"ID Plan Type"})

class HotspotplandefaultSchemaCreate(Schema):
    name = fields.String(required=True, metadata={"description":"Name Plan Type"})
    uptime = fields.Integer(metadata={"description":"Total Uptime in second"})
    expired = fields.Integer(metadata={"description":"Epoch Unix expired time"})
    price = fields.Integer(metadata={"description":"price in integer"})
    kuota = fields.Integer(metadata={"description":"Total Kuota in Megabyte MB"})
    limit_shared = fields.Integer(metadata={"description":"Max simultaneous Use"})
    type_id = fields.Integer(metadata={"description":"ID Plan Type"})

class HotspotplandefaultSchemaDelete(Schema):
    id = fields.String(required=True, metadata={"description":"ID Plan Type"})

class HotspotplandefaultSchemaList(Schema):
    data = fields.List(fields.Nested(HotspotplandefaultSchema))

class HotspotplandefaultAPI(MethodResource,  Resource):
    @doc(description="Create Hotspot Plan default", tags=['Hotspot Plan'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(HotspotplandefaultSchemaCreate, location=('json'))
    @marshal_with(HotspotplandefaultSchema)
    @check_header
    #Create Plant Type
    def post(self,**kwargs):
        try:
            name = kwargs['name']
            uptime = kwargs['uptime']
            kuota = kwargs['kuota']
            expired = kwargs['expired']
            price = kwargs['price']
            type_id = kwargs['type_id']
            limit_shared = kwargs['limit_shared']
            
            type_id_exisis = plan_type.query.filter_by(id=type_id).first()
            if type_id_exisis is None:
                return jsonify({"message":"type id not exists"})

            name_exists = plan_default.query.filter_by(name=name).first()
            if name_exists:
                return jsonify({"message": "Name already exists"}), 409
            id = id_plandefault()
            new_plan_default = plan_default(id, name, uptime, expired, price, kuota, type_id,limit_shared)
            db_plan.session.add(new_plan_default)
            db_plan.session.commit()

            data = new_plan_default.get_data()

            #Logging
            info_admin = info_administrator()
            accessed = {'ip':request.remote_addr, 'id_token': info_admin['admin_id']}
            new_log = plandefault_logging_create(accessed, str(data), data['id'], info_admin['admin_id'])
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
            db_plan.session.expire_all()
        
    @doc(description="List Hotspot Plan default", tags=['Hotspot Plan'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @marshal_with(HotspotplandefaultSchemaList)
    @check_header
    #Get list hotspot plant_type
    def get(self):
        try:
            hotspotdefault_list = []
            hotspotdefault = plan_default.query.order_by(plan_default.name.asc()).all()

            for _hotspotdefault in hotspotdefault:
                __hotspotdefault = {
                    "id":_hotspotdefault.id,
                    "name":_hotspotdefault.name,
                    "uptime":_hotspotdefault.uptime,
                    "expired":_hotspotdefault.expired,
                    "kuota":_hotspotdefault.kuota,
                    "limit_shared":_hotspotdefault.limit_shared,
                    "type_id": _hotspotdefault.type_id
                }
                hotspotdefault_list.append(__hotspotdefault)
            
            data = {'data':hotspotdefault_list}
            return jsonify(data)

        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        finally:
            db_plan.session.expire_all()
    
    @doc(description="Update Hotspot Plan default", tags=['Hotspot Plan'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(HotspotplandefaultSchema, location=('json'))
    @marshal_with(HotspotplandefaultSchema)
    @check_header
    #Update Plant Type
    def put(self,**kwargs):
        try:
            id = kwargs['id']
            name = kwargs['name']
            uptime = kwargs['uptime']
            kuota = kwargs['kuota']
            expired = kwargs['expired']
            price = kwargs['price']
            type_id = kwargs['type_id']
            limit_shared = kwargs['limit_shared']

            get_plandefault = plan_default.query.filter_by(id=id).first()
            if get_plandefault:
                get_plandefault.name = name
                get_plandefault.uptime = uptime
                get_plandefault.kuota = kuota
                get_plandefault.expired = expired
                get_plandefault.price = price
                get_plandefault.type_id = type_id
                get_plandefault.limit_shared = limit_shared
                db_plan.session.commit()
            
                data = get_plandefault.get_data()
                #Logging
                info_admin = info_administrator()
                accessed = {'ip':request.remote_addr, 'id_token': info_admin['admin_id']}
                new_log = plandefault_logging_update(accessed, str(data), data['id'], info_admin['admin_id'])
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
            db_plan.session.expire_all()
    
    @doc(description="Delete Hotspot Plan Default", tags=['Hotspot Plan'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(HotspotplandefaultSchemaDelete, location=('json'))
    @marshal_with(HotspotplandefaultSchema)
    @check_header
    #Delete Plant Type
    def delete(self, **kwargs):
        try:
            id = kwargs['id']
            get_plandefault = plan_default.query.filter_by(id=id).first()

            if get_plandefault:
                old_data = get_plandefault.get_data()
                db_plan.session.delete(get_plandefault)
                db_plan.session.commit()

                #Logging
                info_admin = info_administrator()
                accessed = {'ip':request.remote_addr, 'id_token':info_admin['request_id']}
                new_log = plandefault_logging_delete(accessed, str(old_data), old_data['id'], info_admin['admin_id'])
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
            db_plan.session.expire_all()

class InfoHotspotplandefaultAPI(MethodResource, Resource):
    @doc(description="Info Hotspot Plan default", tags=['Hotspot Plan'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @marshal_with(HotspotplandefaultSchema)
    @check_header
    #Get hotspot plant_type
    def get(self, id):
        try:
            
            hotspotdefaults = plan_default.query.filter_by(id=id).first()
            if hotspotdefaults:
                data = hotspotdefaults.get_data()
                return jsonify(data)
            
            return jsonify({"message": "Not Found"}), 404
        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        finally:
            db_plan.session.expire_all()