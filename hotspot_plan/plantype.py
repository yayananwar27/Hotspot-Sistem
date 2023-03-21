from flask import jsonify, request, make_response
from flask_restful import Resource
from marshmallow import Schema, fields
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from functools import wraps

from administrator.main import info_administrator

from config import redis_conn
from .models import db_plan, plan_type
from .logging import plantype_logging_create, plantype_logging_update, plantype_logging_delete

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

#plantype schema
class HotspotplantypeSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"ID Plan Type"})
    name = fields.String(required=True, metadata={"description":"Name Plan Type"})
    enable_uptime = fields.Boolean(metadata={"description":"True/False"})
    enable_kuota = fields.Boolean(metadata={"description":"True/False"})
    enable_expired = fields.Boolean(metadata={"description":"True/False"})
    enable_limit_shared = fields.Boolean(metadata={"description":"True/False"})

class HotspotplantypeSchemaList(Schema):
    data = fields.List(fields.Nested(HotspotplantypeSchema))

class HotspotplantypeSchemaCreate(Schema):
    name = fields.String(required=True, metadata={"description":"Name Plan Type"})
    enable_uptime = fields.Boolean(required=True, metadata={"description":"True/False"})
    enable_kuota = fields.Boolean(required=True, metadata={"description":"True/False"})
    enable_expired = fields.Boolean(required=True, metadata={"description":"True/False"})
    enable_limit_shared = fields.Boolean(required=True, metadata={"description":"True/False"})

class HotspotplantypeSchemaDelete(Schema):
    id = fields.Integer(required=True, metadata={"description":"ID Plan Type"})


#class CRUD plant type

class HotspotplantypeAPI(MethodResource,  Resource):
    @doc(description="Create Hotspot Plan Type", tags=['Hotspot Plan'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(HotspotplantypeSchemaCreate, location=('json'))
    @marshal_with(HotspotplantypeSchema)
    @check_header
    #Create Plant Type
    def post(self,**kwargs):
        try:
            name = kwargs['name']
            enable_uptime = kwargs['enable_uptime']
            enable_kuota = kwargs['enable_kuota']
            enable_expired = kwargs['enable_expired']
            enable_limit_shared = kwargs['enable_limit_shared']

            name_exists = plan_type.query.filter_by(name=name).first()
            if name_exists:
                return jsonify({"message": "Name already exists"}), 409
            
            new_plan_type = plan_type(name, enable_uptime, enable_kuota, enable_expired, enable_limit_shared)
            db_plan.session.add(new_plan_type)
            db_plan.session.commit()

            data = new_plan_type.get_data()
            
            #Logging
            info_admin = info_administrator()
            accessed = {'ip':request.remote_addr, 'id_token': info_admin['admin_id']}
            new_log = plantype_logging_create(accessed, str(data), data['id'], info_admin['admin_id'])
            if new_log == False:
                print("Logging Failed")
            
            return jsonify(data)

        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
    
    @doc(description="List Hotspot Plan Type", tags=['Hotspot Plan'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @marshal_with(HotspotplantypeSchemaList)
    @check_header
    #Get list hotspot plant_type
    def get(self):
        try:
            hotspottype_list = []
            hotspottypes = plan_type.query.order_by(plan_type.name.asc()).all()

            for _hotspottypes in hotspottypes:
                __hotspottypes = {
                    "id":_hotspottypes.id,
                    "name":_hotspottypes.name,
                    "enable_uptime":_hotspottypes.enable_uptime,
                    "enable_kuota":_hotspottypes.enable_kuota,
                    "enable_expired":_hotspottypes.enable_expired,
                    "enable_limit_shared":_hotspottypes.enable_limit_shared
                }
                hotspottype_list.append(__hotspottypes)
            
            data = {'data':hotspottype_list}
            return jsonify(data)

        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
    
    @doc(description="Update Hotspot Plan Type", tags=['Hotspot Plan'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(HotspotplantypeSchema, location=('json'))
    @marshal_with(HotspotplantypeSchema)
    @check_header
    #Update Plant Type
    def put(self,**kwargs):
        try:
            id = kwargs['id']
            name = kwargs['name']
            enable_uptime = kwargs['enable_uptime']
            enable_kuota = kwargs['enable_kuota']
            enable_expired = kwargs['enable_expired']
            enable_limit_shared = kwargs['enable_limit_shared']

            get_plantype = plan_type.query.filter_by(id=id).first()
            if get_plantype:
                get_plantype.name = name
                get_plantype.enable_uptime = enable_uptime
                get_plantype.enable_kuota = enable_kuota
                get_plantype.enable_expired = enable_expired
                get_plantype.enable_limit_shared = enable_limit_shared
                db_plan.session.commit()
            
                data = get_plantype.get_data()
                #Logging
                info_admin = info_administrator()
                accessed = {'ip':request.remote_addr, 'id_token': info_admin['admin_id']}
                new_log = plantype_logging_update(accessed, str(data), data['id'], info_admin['admin_id'])
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
        
    @doc(description="Delete Hotspot Plan Type", tags=['Hotspot Plan'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(HotspotplantypeSchemaDelete, location=('json'))
    @marshal_with(HotspotplantypeSchema)
    @check_header
    #Delete Plant Type
    def delete(self, **kwargs):
        try:
            id = kwargs['id']
            get_plantype = plan_type.query.filter_by(id=id).first()

            if get_plantype:
                old_data = get_plantype.get_data()
                db_plan.session.delete(get_plantype)
                db_plan.session.commit()

                #Logging
                info_admin = info_administrator()
                accessed = {'ip':request.remote_addr, 'id_token':info_admin['request_id']}
                new_log = plantype_logging_delete(accessed, str(old_data), old_data['id'], info_admin['admin_id'])
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

class InfoHotspotplantypeAPI(MethodResource, Resource):
    @doc(description="Info Hotspot Plan Type", tags=['Hotspot Plan'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @marshal_with(HotspotplantypeSchema)
    @check_header
    #Get hotspot plant_type
    def get(self, id):
        try:
            
            hotspottypes = plan_type.query.filter_by(id=id).first()
            if hotspottypes:
                data = hotspottypes.get_data()
                return jsonify(data)
            
            return jsonify({"message": "Not Found"}), 404
        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone