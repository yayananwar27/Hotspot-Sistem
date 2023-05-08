from flask import jsonify, request, make_response
from flask_restful import Resource
from marshmallow import Schema, fields
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from functools import wraps
from secrets import token_hex
from administrator.main import info_administrator

from config import redis_conn
from .models import db_plan, plan_template, plan_type
from .logging import plantemplate_logging_create, plantemplate_logging_update, plantemplate_logging_delete

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

def id_plantemplate():
    id = str(get_uuid(8))
    i = False
    while i == False:
        id_exists = plan_template.query.filter_by(id=id).first()
        if id_exists is None:
            i = True
        else:
            i = False
            id = str(get_uuid(8))
    return id

#plantype schema
class HotspotplantemplateSchema(Schema):
    id = fields.String(required=True, metadata={"description":"ID Plan Type"})
    name = fields.String(required=True, metadata={"description":"Name Plan Type"})
    uptime = fields.Integer(metadata={"description":"Total Uptime in second"})
    expired = fields.Integer(metadata={"description":"Epoch Unix expired time"})
    price = fields.Integer(metadata={"description":"price in integer"})
    kuota = fields.Integer(metadata={"description":"Total Kuota in Megabyte MB"})
    limit_shared = fields.Integer(metadata={"description":"Max simultaneous Use"})
    type_id = fields.Integer(metadata={"description":"ID Plan Type"})

class HotspotplantemplateSchemaCreate(Schema):
    name = fields.String(required=True, metadata={"description":"Name Plan Type"})
    uptime = fields.Integer(metadata={"description":"Total Uptime in second"})
    expired = fields.Integer(metadata={"description":"Epoch Unix expired time"})
    price = fields.Integer(metadata={"description":"price in integer"})
    kuota = fields.Integer(metadata={"description":"Total Kuota in Megabyte MB"})
    limit_shared = fields.Integer(metadata={"description":"Max simultaneous Use"})
    type_id = fields.Integer(metadata={"description":"ID Plan Type"})

class HotspotplantemplateSchemaDelete(Schema):
    id = fields.String(required=True, metadata={"description":"ID Plan Type"})

class HotspotplantemplateSchemaList(Schema):
    data = fields.List(fields.Nested(HotspotplantemplateSchema))

class HotspotplantemplateAPI(MethodResource,  Resource):
    @doc(description="Create Hotspot Plan template", tags=['Hotspot Plan'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(HotspotplantemplateSchemaCreate, location=('json'))
    @marshal_with(HotspotplantemplateSchema)
    @check_header
    #Create Plant Type
    def post(self,**kwargs):
        try:
            name = kwargs['name']
            uptime = kwargs['uptime']
            kuota = kwargs['kuota']
            _expired = kwargs['expired']
            price = kwargs['price']
            type_id = kwargs['type_id']
            limit_shared = kwargs['limit_shared']
            
            type_id_exisis = plan_type.query.filter_by(id=type_id).first()
            if type_id_exisis is None:
                return jsonify({"message":"type id not exists"})

            #name_exists = plan_template.query.filter_by(name=name).first()
            #if name_exists:
            #    return jsonify({"message": "Name already exists"}), 409
            
            id = id_plantemplate()
            new_plan_template = plan_template(id, name, uptime, _expired, price, kuota, type_id,limit_shared)
            db_plan.session.add(new_plan_template)
            db_plan.session.commit()

            data = new_plan_template.get_data()

            #Logging
            info_admin = info_administrator()
            accessed = {'ip':request.remote_addr, 'id_token': info_admin['request_id']}
            new_log = plantemplate_logging_create(accessed, str(data), data['id'], info_admin['admin_id'])
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
        
    @doc(description="List Hotspot Plan template", tags=['Hotspot Plan'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @marshal_with(HotspotplantemplateSchemaList)
    @check_header
    #Get list hotspot plant_type
    def get(self):
        try:
            hotspottemplate_list = []
            hotspottemplate = plan_template.query.order_by(plan_template.name.asc()).all()

            for _hotspottemplate in hotspottemplate:
                __hotspottemplate = {
                    "id":_hotspottemplate.id,
                    "name":_hotspottemplate.name,
                    "uptime":_hotspottemplate.uptime,
                    "expired":_hotspottemplate.expired,
                    "kuota":_hotspottemplate.kuota,
                    "limit_shared":_hotspottemplate.limit_shared,
                    "type_id": _hotspottemplate.type_id
                }
                hotspottemplate_list.append(__hotspottemplate)
            
            data = {'data':hotspottemplate_list}
            return jsonify(data)

        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        finally:
            db_plan.session.expire_all()
    
    @doc(description="Update Hotspot Plan template", tags=['Hotspot Plan'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(HotspotplantemplateSchema, location=('json'))
    @marshal_with(HotspotplantemplateSchema)
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

            get_plantemplate = plan_template.query.filter_by(id=id).first()
            if get_plantemplate:
                get_plantemplate.name = name
                get_plantemplate.uptime = uptime
                get_plantemplate.kuota = kuota
                get_plantemplate.expired = expired
                get_plantemplate.price = price
                get_plantemplate.type_id = type_id
                get_plantemplate.limit_shared = limit_shared
                db_plan.session.commit()
            
                data = get_plantemplate.get_data()
                #Logging
                info_admin = info_administrator()
                accessed = {'ip':request.remote_addr, 'id_token': info_admin['request_id']}
                new_log = plantemplate_logging_update(accessed, str(data), data['id'], info_admin['admin_id'])
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
    
    @doc(description="Delete Hotspot Plan template", tags=['Hotspot Plan'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(HotspotplantemplateSchemaDelete, location=('json'))
    @marshal_with(HotspotplantemplateSchema)
    @check_header
    #Delete Plant Type
    def delete(self, **kwargs):
        try:
            id = kwargs['id']
            get_plantemplate = plan_template.query.filter_by(id=id).first()

            if get_plantemplate:
                old_data = get_plantemplate.get_data()
                db_plan.session.delete(get_plantemplate)
                db_plan.session.commit()

                #Logging
                info_admin = info_administrator()
                accessed = {'ip':request.remote_addr, 'id_token':info_admin['request_id']}
                new_log = plantemplate_logging_delete(accessed, str(old_data), old_data['id'], info_admin['admin_id'])
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

class InfoHotspotplantemplateAPI(MethodResource, Resource):
    @doc(description="Info Hotspot Plan template", tags=['Hotspot Plan'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @marshal_with(HotspotplantemplateSchema)
    @check_header
    #Get hotspot plant_type
    def get(self, id):
        try:
            
            hotspottemplates = plan_template.query.filter_by(id=id).first()
            if hotspottemplates:
                data = hotspottemplates.get_data()
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