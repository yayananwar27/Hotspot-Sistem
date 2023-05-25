from flask_restful import Resource
from marshmallow import Schema, fields
from flask_apispec.views import MethodResource
from flask_apispec import use_kwargs
from flask import request, jsonify, current_app

import urllib3
import json


from .models import db_plan, plan_template, plan_site
from .plansite import id_plansite
from .logging import plansite_logging_create, plansite_logging_delete

from sites.models import site
from hotspot_profile.models import template_hotspot_plan

from dotenv import load_dotenv
import os
load_dotenv()
from config import scheduler
import requests

@scheduler.scheduled_job('interval', id="sync_plan_template_site",  seconds=60, max_instances=1)
def sync_plan_template_site():
    try:
        headers = {"Accept":"application/json","Content-Type": "application/json"}
        url = f"http://127.0.0.1:{os.environ['PORT']}/hotspot_plan/@syncplantemplatesite"
        body = {'secret_keys':"{}".format(os.environ["SECRET_KEY"])}
        _session = requests.Session()

        try:
            response = _session.get(url, headers=headers, data=json.dumps(body), verify=False)
            api_data = response.json()
            if api_data['message'] != "success":
                print("error task")

        except Exception as e:
            print(e)

    except Exception as e:
        print(e)
    finally:
        _session.close()

class AdministratorSchemaCheckToken(Schema):
    secret_keys = fields.String(required=True, metadata={"description":"secret_token"})

class CheckSyncPlanTemplateSite(MethodResource, Resource):
    @use_kwargs(AdministratorSchemaCheckToken, location=('json'))
    def get(self, **kwargs):
        try:     
            
            if request.remote_addr != '127.0.0.1':
                return jsonify({"message": "Unauthorized"}), 401
            if kwargs['secret_keys'] != current_app.config['SECRET_KEY']:
                return jsonify({"message": "Unauthorized"}), 401
            
            #UPDATE SYNC ada data dan deleted
            list_site = site.query.order_by(site.profile_id.asc()).all()
            
            for _list_site in list_site:
                list_plan_st = []
                list_plan_st_id = []
                st_hotspot_plan = plan_site.query.filter_by(id_site=_list_site.id).all()
                for _st_hotspot_plan in st_hotspot_plan:
                    if _st_hotspot_plan.template_id != None:
                        list_plan_st.append(_st_hotspot_plan.template_id)
                        list_plan_st_id.append({'id':_st_hotspot_plan.id, 'template_id':_st_hotspot_plan.template_id})

                tmplt_hotspot_plan = template_hotspot_plan.query.filter_by(id_hotspot_profile=_list_site.profile_id).all()
                list_plan_tmplt = []
                for _tmplt_hotspot_plan in tmplt_hotspot_plan:
                    plan_tmplt = plan_template.query.filter_by(id=_tmplt_hotspot_plan.id_plan_template).first()
                    list_plan_tmplt.append(plan_tmplt.id)

                deleting_plan = list(set(list_plan_st)-set(list_plan_tmplt))
                creating_plan = list(set(list_plan_tmplt)-set(list_plan_st))
                
                __delete_plan = []
                for _deleting_plan in deleting_plan:
                    for item in list_plan_st_id:
                        if item['template_id'] == _deleting_plan:
                            __delete_plan.append(item['id'])

                #deleting plan site yang gada di template
                for deleting in __delete_plan:
                    get_plansite = plan_site.query.filter_by(id=deleting).first()
                    if get_plansite:
                        old_data = get_plansite.get_data()
                        db_plan.session.delete(get_plansite)
                        db_plan.session.commit()

                        #Logging
                        accessed = {'ip':request.remote_addr, 'id_token': 'By System Sync'}
                        new_log = plansite_logging_delete(accessed, str(old_data), old_data['id'], None)
                        if new_log == False:
                            print("Logging Failed")

                #creating plan site from template
                for _creting_plan in creating_plan:
                    plan_create = plan_template.query.filter_by(id=_creting_plan).first()
                    id = id_plansite()
                    new_plan_site = plan_site(id, plan_create.name, plan_create.uptime, plan_create.expired, plan_create.price, plan_create.kuota, plan_create.type_id, _list_site.id, plan_create.limit_shared, plan_create.id)
                    
                    db_plan.session.add(new_plan_site)
                    db_plan.session.commit()
                    
                    #Logging
                    data = new_plan_site.get_data()
                    accessed = {'ip':request.remote_addr, 'id_token': 'By System Sync'}
                    new_log = plansite_logging_create(accessed, str(data), data['id'], None)
                    if new_log == False:
                        print("Logging Failed")

            #UPDATE SYNC data
            st_hotspot_plan = plan_site.query.order_by(plan_site.id_site.asc()).all()
            for _st_hotspot_plan in st_hotspot_plan:
                if _st_hotspot_plan.template_id != None:
                    dt_plan_site = {
                        "name":_st_hotspot_plan.name,
                        "uptime":_st_hotspot_plan.uptime,
                        "expired":_st_hotspot_plan.expired,
                        "price":_st_hotspot_plan.price,
                        "kuota":_st_hotspot_plan.kuota,
                        "limit_shared":_st_hotspot_plan.limit_shared,
                        "type_id":_st_hotspot_plan.type_id
                    }

                    pln_tmplt = plan_template.query.filter_by(id=_st_hotspot_plan.template_id).first()
                    dt_plan_tmplt = {
                        "name" :pln_tmplt.name,
                        "uptime" :pln_tmplt.uptime, 
                        "expired":pln_tmplt.expired,
                        "price":pln_tmplt.price,
                        "kouta":pln_tmplt.kouta,
                        "limit_shared":pln_tmplt.limit_shared,
                        "type_id":pln_tmplt.type_id
                    }

                    if dt_plan_site != dt_plan_tmplt:
                        _st_hotspot_plan.name = pln_tmplt.name
                        _st_hotspot_plan.uptime = pln_tmplt.uptime
                        _st_hotspot_plan.expired = pln_tmplt.expired
                        _st_hotspot_plan.price = pln_tmplt.price
                        _st_hotspot_plan.kuota = pln_tmplt.kuota
                        _st_hotspot_plan.limit_shared = pln_tmplt.limit_Shared
                        _st_hotspot_plan.type_id = pln_tmplt.type_id
                        db_plan.session.commit()

            error = {"message":"success"}
            respone = jsonify(error)
            respone.status_code = 200
            return respone

        except Exception as e:
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        
        finally:
            db_plan.session.expire_all()