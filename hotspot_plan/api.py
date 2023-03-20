from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

from .plantype import HotspotplanttypeAPI, InfoHotspotplantypeAPI

hotspotplan_api = Blueprint('hotspotplan_api',__name__)
CORS(hotspotplan_api, supports_credentials=True, resources=r'*', origins="*", allow_headers=["Content-Type", "Authorization"], methods=['GET','POST','PUT','DELETE'])

api = Api(hotspotplan_api)

api.add_resource(HotspotplanttypeAPI, '/plan_type')
api.add_resource(InfoHotspotplantypeAPI, '/plant_type/<id>')
