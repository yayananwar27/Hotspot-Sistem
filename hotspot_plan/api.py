from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

from .plantype import HotspotplantypeAPI, InfoHotspotplantypeAPI
from .plandefault import HotspotplandefaultAPI, InfoHotspotplandefaultAPI
from .plansite import HotspotplansiteAPI, InfoHotspotplansiteAPI


hotspotplan_api = Blueprint('hotspotplan_api',__name__)
CORS(hotspotplan_api, supports_credentials=True, resources=r'*', origins="*", allow_headers=["Content-Type", "Authorization"], methods=['GET','POST','PUT','DELETE'])

api = Api(hotspotplan_api)

api.add_resource(HotspotplantypeAPI, '/plan_type')
api.add_resource(InfoHotspotplantypeAPI, '/plant_type/<id>')
api.add_resource(HotspotplandefaultAPI, '/plan_template')
api.add_resource(InfoHotspotplandefaultAPI, '/plan_template/<id>')
api.add_resource(HotspotplansiteAPI, '/plan_site')
api.add_resource(InfoHotspotplansiteAPI, '/plan_site/<id>')
