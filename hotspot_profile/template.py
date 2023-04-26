from flask import jsonify, request, make_response
from flask_restful import Resource
from marshmallow import Schema, fields
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from functools import wraps

from administrator.main import info_administrator

from config import redis_conn
from .models import db_hs, template_hotspot_plan, hotspot_profile
from .logging import hotspotprofiletemplate_logging_create, hotspotprofiletemplate_logging_update, hotspotprofiletemplate_logging_delete

from hotspot_plan.models import plan_template
from hotspot_plan.plantemplate import HotspotplantemplateSchema
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

class HotspotprofiletemplateSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"ID Hotspot profile template"})
    id_hotspot_profile = fields.Integer(required=True, metadata={"description":"ID Hotspot profile"})
    id_plan_template = fields.String(required=True, metadata={"description":"ID plan template"})

class HotspotprofiletemplateSchemaInfo(Schema):
    id = fields.Integer(required=True, metadata={"description":"ID Hotspot profile template"})
    id_hotspot_profile = fields.Integer(required=True, metadata={"description":"ID Hotspot profile"})
    id_plan_template = fields.String(required=True, metadata={"description":"ID plan template"})
    hotspot_profile = fields.Nested(HotspotprofileSchema)
    template_plan = fields.Nested(HotspotplantemplateSchema)

class HotspotprofiletemplateSchemaInfoList(Schema):
    hotspot_profile = fields.Nested(HotspotprofileSchema)
    template_plan = fields.List(fields.Nested(HotspotplantemplateSchema))
    
class HotspotprofiletemplateSchemaList(Schema):
    data = fields.List(fields.Nested(HotspotprofiletemplateSchemaInfo))

class HotspotprofiletemplateSchemaCreate(Schema):
    id_hotspot_profile = fields.Integer(required=True, metadata={"description":"ID Hotspot profile"})
    id_plan_template = fields.String(required=True, metadata={"description":"ID plan template"})

class HotspotprofiletemplateSchemaDelete(Schema):
    id = fields.Integer(required=True, metadata={"description":"ID Hotspot profile template"})

#Crud
class HotspotprofiletemplateAPI(MethodResource, Resource):
    @doc(description="Create Hotspot profile template", tags=['Hotspot Profile'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(HotspotprofiletemplateSchemaCreate, location=('json'))
    @marshal_with(HotspotprofiletemplateSchemaInfo)
    @check_header
    def post(self, **kwargs):
        try:
            id_hotspot_profile = kwargs['id_hotspot_profile']
            id_plan_template = kwargs['id_plan_template']

            id_hotspot_profile_exists = hotspot_profile.query.filter_by(id=id_hotspot_profile).first()
            if id_hotspot_profile_exists is None:
                return jsonify({"message": "ID Hotspot Profile Not Exists"}), 404
            
            id_plan_template_exists = plan_template.query.filter_by(id=id_plan_template).first()
            if id_plan_template_exists is None:
                return jsonify({"message": "ID Plan Template Not Exists"}), 404
        
            check_template_exists = template_hotspot_plan.query.filter_by(id_hotspot_profile=id_hotspot_profile, id_plan_template=id_plan_template).first()
            if check_template_exists:
                return jsonify({"message": "Template Already registered"}), 409


            new_template_hotspot_plan = template_hotspot_plan(id_hotspot_profile, id_plan_template)
            db_hs.session.add(new_template_hotspot_plan)
            db_hs.session.commit()

            data = new_template_hotspot_plan.get_data()
            data_hotspot_profile = hotspot_profile.query.filter_by(id=data["id_hotspot_profile"]).first()
            data['hotspot_profile'] = data_hotspot_profile.get_data()
            data_plan_template = plan_template.query.filter_by(id=data["id_plan_template"]).first()
            data['plan_template'] = data_plan_template.get_data()

            #Logging
            info_admin = info_administrator()
            accessed = {'ip':request.remote_addr, 'id_token': info_admin['request_id']}
            new_log = hotspotprofiletemplate_logging_create(accessed, str(data), data['id'], info_admin['admin_id'])
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

    @doc(description="List Hotspot profile template", tags=['Hotspot Profile'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @marshal_with(HotspotprofiletemplateSchemaList)
    @check_header
    def get(self):
        try:
            hotspotprofiletemplate_list = []
            hotspotprofilestemplate = template_hotspot_plan.query.order_by(template_hotspot_plan.id.asc()).all()
            for _hotspotprofilestemplate in hotspotprofilestemplate:
                info_hsprofile = hotspot_profile.query.filter_by(id=_hotspotprofilestemplate.id_hotspot_profile).first()
                data_hsprofile = info_hsprofile.get_data()

                info_plantemplate = plan_template.query.filter_by(id=_hotspotprofilestemplate.id_plan_template).first()
                data_plantemplate = info_plantemplate.get_data() 
                
                info_profiletemplate = {
                    'id' : _hotspotprofilestemplate.id, 
                    'id_hotspot_profile' : _hotspotprofilestemplate.id_hotspot_profile,
                    'id_plan_template' : _hotspotprofilestemplate.id_plan_template,
                    'hotspot_profile':data_hsprofile,
                    'template_plan':data_plantemplate
                }
                hotspotprofiletemplate_list.append(info_profiletemplate)

            data = {'data':hotspotprofiletemplate_list}
            return jsonify(data)
        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        finally:
            db_hs.session.expire_all()

    # @doc(description="Update Hotspot profile template", tags=['Hotspot Profile'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    # @use_kwargs(HotspotplantemplateSchema, location=('json'))
    # @marshal_with(HotspotprofiletemplateSchemaInfo)
    # @check_header
    # def put(self, **kwargs):
    #     try:
    #         id = kwargs['id']
    #         id_hotspot_profile = kwargs['id_hotspot_profile']
    #         id_plan_template = kwargs['id_plan_template']

    #         get_profile_template = template_hotspot_plan.query.filter_by(id=id).first()
    #         if get_profile_template:
    #             get_profile_template.id_hotspot_profile = id_hotspot_profile
    #             get_profile_template.id_plan_template = id_plan_template
    #             db_hs.session.commit()
                
    #             data = get_profile_template.get_data()
    #             data_hotspot_profile = hotspot_profile.query.filter_by(id=data["id_hotspot_profile"]).first()
    #             data['hotspot_profile'] = data_hotspot_profile.get_data()
    #             data_plan_template = plan_template.query.filter_by(id=data["id_plan_template"]).first()
    #             data['plan_template'] = data_plan_template.get_data()

    #             #Logging
    #             info_admin = info_administrator()
    #             accessed = {'ip':request.remote_addr, 'id_token': info_admin['request_id']}
    #             new_log = hotspotprofiletemplate_logging_update(accessed, str(data), data['id'], info_admin['admin_id'])
    #             if new_log == False:
    #                 print("Logging Failed")

    #             return jsonify(data)
        
    #         return jsonify({"message": "ID Not Found"}), 404
    
    #     except Exception as e:
    #         print(e)
    #         error = {"message":e}
    #         respone = jsonify(error)
    #         respone.status_code = 500
    #         return respone
    #     finally:
    #         db_hs.session.expire_all()   

    @doc(description="Delete Hotspot profile template", tags=['Hotspot Profile'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @use_kwargs(HotspotprofiletemplateSchemaDelete, location=('json'))
    @marshal_with(HotspotprofiletemplateSchemaInfo)
    @check_header
    def delete(self, **kwargs):
        try:
            id = kwargs['id']
            get_profile_template = template_hotspot_plan.query.filter_by(id=id).first()
            if get_profile_template:
                old_data = get_profile_template.get_data()
                db_hs.session.delete(get_profile_template)
                db_hs.session.commit()

                data_hotspot_profile = hotspot_profile.query.filter_by(id=old_data["id_hotspot_profile"]).first()
                old_data['hotspot_profile'] = data_hotspot_profile.get_data()
                data_plan_template = plan_template.query.filter_by(id=old_data["id_plan_template"]).first()
                old_data['plan_template'] = data_plan_template.get_data()

                #Logging
                info_admin = info_administrator()
                accessed = {'ip':request.remote_addr, 'id_token': info_admin['request_id']}
                new_log = hotspotprofiletemplate_logging_delete(accessed, str(old_data), old_data['id'], info_admin['admin_id'])
                if new_log == False:
                    print("Logging Failed")

                return jsonify(old_data)

        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        finally:
            db_hs.session.expire_all()   

class InfoHotspotprofiletemplateAPI(MethodResource, Resource):
    @doc(description="Info Hotspot profile template", tags=['Hotspot Profile'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @marshal_with(HotspotprofiletemplateSchemaInfo)
    @check_header
    def get(self, id):
        try:
            hotspotprofilestemplate = template_hotspot_plan.query.filter_by(id=id).first()
            if hotspotprofilestemplate:
                info_hsprofile = hotspot_profile.query.filter_by(id=hotspotprofilestemplate.id_hotspot_profile).first()
                data_hsprofile = info_hsprofile.get_data()
                info_plantemplate = plan_template.query.filter_by(id=hotspotprofilestemplate.id_plan_template).first()
                data_plantemplate = info_plantemplate.get_data() 
                
                info_profiletemplate = {
                    'id' : hotspotprofilestemplate.id, 
                    'id_hotspot_profile' : hotspotprofilestemplate.id_hotspot_profile,
                    'id_plan_template' : hotspotprofilestemplate.id_plan_template,
                    'hotspot_profile':data_hsprofile,
                    'template_plan':data_plantemplate
                }
                return jsonify(info_profiletemplate)
            return jsonify({"message": "Not Found"}), 404
        
        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        finally:
            db_hs.session.expire_all()

class ListInfoHotspotprofiletemplateAPI(MethodResource, Resource):
    @doc(description="List Info Hotspot profile template", tags=['Hotspot Profile'], params={'Authorization': {'in': 'header', 'description': 'An access token'}})
    @marshal_with(HotspotprofiletemplateSchemaInfoList)
    @check_header
    def get(self, id):
        try:
            hotspotprofilestemplate = template_hotspot_plan.query.filter_by(id_hotspot_profile=id).all()
            list_template = []
            if hotspotprofilestemplate:
                for _hotspotprofilestemplate in hotspotprofilestemplate:
                    info_hsprofile = hotspot_profile.query.filter_by(id=_hotspotprofilestemplate.id_hotspot_profile).first()
                    data_hsprofile = info_hsprofile.get_data()
                    info_plantemplate = plan_template.query.filter_by(id=_hotspotprofilestemplate.id_plan_template).first()
                    data_plantemplate = info_plantemplate.get_data() 
                    data_plantemplate['id_registered'] = _hotspotprofilestemplate.id
                    list_template.append(data_plantemplate)
                
                info_profiletemplate = {
                        'hotspot_profile' : data_hsprofile,
                        'template_plan' : list_template
                }
                return jsonify(info_profiletemplate)
            return jsonify({"message": "Not Found"}), 404
        
        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        finally:
            db_hs.session.expire_all()