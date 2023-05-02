from flask import jsonify, request, make_response
from flask_restful import Resource
from marshmallow import Schema, fields
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from functools import wraps

from administrator.main import info_administrator
from config import redis_conn
from helper import ambil_random
redcon = redis_conn()

from hotspot_profile.hotspot_profile import HotspotprofileSchema
from hotspot_profile.models import hotspot_profile

from .models import db_site, site
from .logging import site_logging_create, site_logging_update, site_logging_delete
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

def generate_id_site():
    id = str(ambil_random(8).lower())
    i = False
    while i == False:
        id_exists = site.query.filter_by(id=id).first()
        if id_exists is None:
            i = True
        else:
            i = False
            id = str(ambil_random(8).lower())
    return id

class SiteSchema(Schema):
    id = fields.String(required=True, metadata={"description":"ID Site"})
    name = fields.String(required=True, metadata={"description":"Name site"})
    landing_name = fields.String(required=True, metadata={"description":"penamaan judul pada landing page"})
    profile_id = fields.Integer(required=True, metadata={"description":"ID Hostspot Profile"})

class SiteSchemaInfo(Schema):
    id = fields.String(required=True, metadata={"description":"ID Site"})
    name = fields.String(required=True, metadata={"description":"Name site"})
    landing_name = fields.String(required=True, metadata={"description":"penamaan judul pada landing page"})
    profile_id = fields.Integer(required=True, metadata={"description":"ID Hostspot Profile"})
    profile_info = fields.Nested(HotspotprofileSchema)

class SiteSchemaCreate(Schema):
    name = fields.String(required=True, metadata={"description":"Name site"})
    landing_name = fields.String(required=True, metadata={"description":"penamaan judul pada landing page"})
    profile_id = fields.Integer(required=True, metadata={"description":"ID Hostspot Profile"}) 

class SiteSchemaList(Schema):
    data = fields.List(fields.Nested(SiteSchemaInfo))

class SiteSchemaDelete(Schema):
    id = fields.String(required=True, metadata={"description":"ID Site"})

#CRUD
class SiteAPI(MethodResource, Resource):
    @doc(description="Create Site", tags=['Hotspot Site'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(SiteSchemaCreate, location=('json'))
    @marshal_with(SiteSchemaInfo)
    @check_header
    def post(self, **kwargs):
        try:
            name = kwargs['name']
            landing_name = kwargs['landing_name']
            profile_id = kwargs['profile_id']

            get_nameexists = site.query.filter_by(name=name).first()
            if get_nameexists:
                return jsonify({"message": "Name already exists"}), 409

            id = generate_id_site()
            new_site = site(id, name, landing_name, profile_id)
            db_site.session.add(new_site)
            db_site.session.commit()
            data = new_site.get_data()

            data_profile = hotspot_profile.query.filter_by(id=data['profile_id'])
            data['profile_info'] = data_profile.get_data()

            #Logging
            info_admin = info_administrator()
            accessed = {'ip':request.remote_addr, 'id_token': info_admin['request_id']}
            new_log = site_logging_create(accessed, str(data), data['id'], info_admin['admin_id'])
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
            db_site.session.expire_all()
    
    @doc(description="List Site", tags=['Hotspot Site'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @marshal_with(SiteSchemaList)
    @check_header
    def get(self):
        try:
            sites_list = []
            sites = site.query.order_by(site.name.asc()).all()
            for _sites in sites:
                info_hsprofile = hotspot_profile.query.filter_by(id=_sites.profile_id).first()
                data_hsprofile = info_hsprofile.get_data()
                __sites = _sites.get_data()
                __sites['profile_info'] = data_hsprofile

                sites_list.append(__sites)

            data = {'data':sites_list}
            return jsonify(data)

        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        finally:
            db_site.session.expire_all()

    @doc(description="Update Site", tags=['Hotspot Site'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(SiteSchema, location=('json'))
    @marshal_with(SiteSchemaInfo)
    @check_header
    def put(self, **kwargs):
        try:
            id = kwargs['id']
            name = kwargs['name']
            landing_name = kwargs['landing_name']
            profile_id = kwargs['profile_id']

            get_idexists = site.query.filter_by(id=id).first()
            if get_idexists:
                get_nameexists = site.query.filter_by(name=name).first()
                if get_nameexists:
                    return jsonify({"message": "Name already exists"}), 409

                get_idexists.name = name
                get_idexists.landing_name = landing_name
                get_idexists.profile_id = profile_id
                db_site.session.commit()
                data = get_idexists.get_data()
                
                data_profile = hotspot_profile.query.filter_by(id=data['profile_id'])
                data['profile_info'] = data_profile.get_data()

                #Logging
                info_admin = info_administrator()
                accessed = {'ip':request.remote_addr, 'id_token': info_admin['request_id']}
                new_log = site_logging_update(accessed, str(data), data['id'], info_admin['admin_id'])
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
            db_site.session.expire_all()

    @doc(description="Delete Site", tags=['Hotspot Site'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(SiteSchemaDelete, location=('json'))
    @marshal_with(SiteSchemaInfo)
    @check_header
    def delete(self, **kwargs):
        try:
            id = kwargs['id']
            get_idexists = site.query.filter_by(id=id).first()
            if get_idexists:
                old_data = get_idexists.get_data()
                db_site.session.delete(get_idexists)
                db_site.session.commit()

                #Logging
                info_admin = info_administrator()
                accessed = {'ip':request.remote_addr, 'id_token': info_admin['request_id']}
                new_log = site_logging_delete(accessed, str(old_data), old_data['id'], info_admin['admin_id'])
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
            db_site.session.expire_all()   

#Show info site 
class InfoSiteAPI(MethodResource, Resource):
    @doc(description="Info Site", tags=['Hotspot Site'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @marshal_with(SiteSchemaInfo)
    @check_header
    def get(self, id):
        try:
            get_data = site.query.filter_by(id=id).first()
            if get_data:
                data = get_data.get_data()
                data_profile = hotspot_profile.query.filter_by(id=data['profile_id']).first()
                data['profile_info'] = data_profile.get_data()
                return jsonify(data)
            return jsonify({"message": "Not Found"}), 404

        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        finally:
            db_site.session.expire_all()