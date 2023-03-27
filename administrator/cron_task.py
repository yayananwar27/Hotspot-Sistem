from config import scheduler
from .models import admin_token, admin_token_old, db_admin
from config import redis_conn
from helper import get_datetime
from flask_apispec.views import MethodResource
from flask_restful import Resource
from marshmallow import Schema, fields
from flask_apispec import use_kwargs
from flask import request, jsonify, current_app
import requests

import urllib3
import json

from dotenv import load_dotenv
import os
load_dotenv()

redcon = redis_conn()
dt_now = get_datetime()


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@scheduler.scheduled_job('interval', id="expired_check_admin_token",  seconds=60, max_instances=1)
def expired_token_admin_check():
    try:
        headers = {"Accept":"application/json","Content-Type": "application/json"}
        url = f"http://127.0.0.1:5000/administrator/@checkexpiredtoken"
        body = {'secret_keys':"{}".format(os.environ["SECRET_KEY"])}
        _session = requests.Session()

        try:
            response = _session.post(url, headers=headers, data=json.dumps(body), verify=False)
            api_data = response.json()
            if api_data['message'] != "success":
                print("Error task")
        except Exception as e:
            print(e)

    except Exception as e:
        print(e)
    finally:
        _session.close()

class AdministratorSchemaCheckToken(Schema):
    secret_keys = fields.String(required=True, metadata={"description":"secret_token"})

class CheckExpiredTokenAPI(MethodResource, Resource):
    @use_kwargs(AdministratorSchemaCheckToken, location=('json'))
    def post(self, **kwargs):
        try:
            if request.remote_addr != '127.0.0.1':
                return jsonify({"message": "Unauthorized"}), 401
            if kwargs['secret_keys'] != current_app.config['SECRET_KEY']:
                return jsonify({"message": "Unauthorized"}), 401
            
            expired_token = None
            expired_token = admin_token.query.filter(admin_token.expired<dt_now.unix()).all()
            
            if len(expired_token) < 1:
                error = {"message":"success"}
                respone = jsonify(error)
                respone.status_code = 200
                return respone
            
            for _expired_token in expired_token:
                if _expired_token.type_token == 'access_token':
                    redis_str = 'admin_access_token:'
                if _expired_token.type_token == 'refresh_token':
                    redis_str = 'admin_refresh_token:'
                
                try:
                    redcon.delete(redis_str+_expired_token.token_value)
                except:
                    'nothing'
                
                old_token = admin_token_old(_expired_token.request_id, _expired_token.admin_id, _expired_token.type_token, _expired_token.token_value, _expired_token.expired, _expired_token.allowed_access, _expired_token.created_at)
                db_admin.session.add(old_token)
                db_admin.session.commit()
                del_token = admin_token.query.filter_by(request_id=_expired_token.request_id).first()
                db_admin.session.delete(del_token)
                db_admin.session.commit()
            
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
            db_admin.session.expire_all()