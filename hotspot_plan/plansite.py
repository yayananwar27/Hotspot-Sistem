from flask import jsonify, request, make_response
from flask_restful import Resource
from marshmallow import Schema, fields
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from functools import wraps
from administrator.main import info_administrator

from helper import ambil_random

from config import redis_conn
from .models import db_plan, plan_site, plan_type
from .logging import plansite_logging_create, plansite_logging_update, plansite_logging_delete

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

def id_plansite():
    id = str(ambil_random(10))
    i = False
    while i == False:
        id_exists = plan_site.query.filter_by(id=id).first()
        if id_exists is None:
            i = True
        else:
            i = False
            id = str(ambil_random(10))
    return id

#plantype schema
class HotspotplansiteSchema(Schema):
    id = fields.String(required=True, metadata={"description":"ID Plan Type"})
    name = fields.String(required=True, metadata={"description":"Name Plan Type"})
    uptime = fields.Integer(metadata={"description":"Total Uptime in second"})
    expired = fields.Integer(metadata={"description":"Epoch Unix expired time"})
    price = fields.Integer(metadata={"description":"price in integer"})
    kuota = fields.Integer(metadata={"description":"Total Kuota in Megabyte MB"})
    limit_shared = fields.Integer(metadata={"description":"Max simultaneous Use"})
    type_id = fields.Integer(metadata={"description":"ID Plan Type"})

class HotspotplansiteSchemaCreate(Schema):
    name = fields.String(required=True, metadata={"description":"Name Plan Type"})
    uptime = fields.Integer(metadata={"description":"Total Uptime in second"})
    expired = fields.Integer(metadata={"description":"Epoch Unix expired time"})
    price = fields.Integer(metadata={"description":"price in integer"})
    kuota = fields.Integer(metadata={"description":"Total Kuota in Megabyte MB"})
    limit_shared = fields.Integer(metadata={"description":"Max simultaneous Use"})
    type_id = fields.Integer(metadata={"description":"ID Plan Type"})

class HotspotplansiteSchemaDelete(Schema):
    id = fields.String(required=True, metadata={"description":"ID Plan Type"})

class HotspotplansiteSchemaList(Schema):
    data = fields.List(fields.Nested(HotspotplansiteSchema))

class HotspotplansiteAPI(MethodResource,  Resource):
    @doc(description="Create Hotspot Plan site", tags=['Hotspot Plan'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(HotspotplansiteSchemaCreate, location=('json'))
    @marshal_with(HotspotplansiteSchema)
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

            name_exists = plan_site.query.filter_by(name=name).first()
            if name_exists:
                return jsonify({"message": "Name already exists"}), 409
            
            id = id_plansite()
            new_plan_site = plan_site(id, name, uptime, expired, price, kuota, type_id, limit_shared)
            db_plan.session.add(new_plan_site)
            db_plan.session.commit()

            data = new_plan_site.get_data()

            #Logging
            info_admin = info_administrator()
            accessed = {'ip':request.remote_addr, 'id_token': info_admin['request_id']}
            new_log = plansite_logging_create(accessed, str(data), data['id'], info_admin['admin_id'])
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
        
    @doc(description="List Hotspot Plan site", tags=['Hotspot Plan'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @marshal_with(HotspotplansiteSchemaList)
    @check_header
    #Get list hotspot plant_type
    def get(self):
        try:
            hotspotsite_list = []
            hotspotsite = plan_site.query.order_by(plan_site.name.asc()).all()

            for _hotspotsite in hotspotsite:
                __hotspotsite = {
                    "id":_hotspotsite.id,
                    "name":_hotspotsite.name,
                    "uptime":_hotspotsite.uptime,
                    "expired":_hotspotsite.expired,
                    "kuota":_hotspotsite.kuota,
                    "limit_shared":_hotspotsite.limit_shared,
                    "type_id": _hotspotsite.type_id
                }
                hotspotsite_list.append(__hotspotsite)
            
            data = {'data':hotspotsite_list}
            return jsonify(data)

        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        finally:
            db_plan.session.expire_all()
    
    @doc(description="Update Hotspot Plan site", tags=['Hotspot Plan'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(HotspotplansiteSchema, location=('json'))
    @marshal_with(HotspotplansiteSchema)
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

            get_plansite = plan_site.query.filter_by(id=id).first()
            if get_plansite:
                get_plansite.name = name
                get_plansite.uptime = uptime
                get_plansite.kuota = kuota
                get_plansite.expired = expired
                get_plansite.price = price
                get_plansite.type_id = type_id
                get_plansite.limit_shared = limit_shared
                db_plan.session.commit()
            
                data = get_plansite.get_data()
                #Logging
                info_admin = info_administrator()
                accessed = {'ip':request.remote_addr, 'id_token': info_admin['request_id']}
                new_log = plansite_logging_update(accessed, str(data), data['id'], info_admin['admin_id'])
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
    
    @doc(description="Delete Hotspot Plan Site", tags=['Hotspot Plan'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(HotspotplansiteSchemaDelete, location=('json'))
    @marshal_with(HotspotplansiteSchema)
    @check_header
    #Delete Plant Type
    def delete(self, **kwargs):
        try:
            id = kwargs['id']
            get_plansite = plan_site.query.filter_by(id=id).first()

            if get_plansite:
                old_data = get_plansite.get_data()
                db_plan.session.delete(get_plansite)
                db_plan.session.commit()

                #Logging
                info_admin = info_administrator()
                accessed = {'ip':request.remote_addr, 'id_token':info_admin['request_id']}
                new_log = plansite_logging_delete(accessed, str(old_data), old_data['id'], info_admin['admin_id'])
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

class InfoHotspotplansiteAPI(MethodResource, Resource):
    @doc(description="Info Hotspot Plan site", tags=['Hotspot Plan'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @marshal_with(HotspotplansiteSchema)
    @check_header
    #Get hotspot plant_type
    def get(self, id):
        try:
            
            hotspotsites = plan_site.query.filter_by(id=id).first()
            if hotspotsites:
                data = hotspotsites.get_data()
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