from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

from .plantype import HotspotplantypeAPI, InfoHotspotplantypeAPI
from .plantemplate import HotspotplantemplateAPI, InfoHotspotplantemplateAPI
from .plansite import HotspotplansiteAPI, InfoHotspotplansiteAPI


hotspotplan_api = Blueprint('hotspotplan_api',__name__)
CORS(hotspotplan_api, supports_credentials=True, resources=r'*', origins="*", allow_headers=["Content-Type", "Authorization", "Accept"], methods=['GET','POST','PUT','DELETE'])

api = Api(hotspotplan_api)

api.add_resource(HotspotplantypeAPI, '/plan_type')
api.add_resource(InfoHotspotplantypeAPI, '/plant_type/<id>')
api.add_resource(HotspotplantemplateAPI, '/plan_template')
api.add_resource(InfoHotspotplantemplateAPI, '/plan_template/<id>')
api.add_resource(HotspotplansiteAPI, '/plan_site')
api.add_resource(InfoHotspotplansiteAPI, '/plan_site/<id>')

def init_docs(docs):
    #Add docs CRUD hotspot Plan Type
    docs.register(HotspotplantypeAPI, blueprint='hotspotplan_api')
    docs.register(InfoHotspotplantypeAPI, blueprint='hotspotplan_api')
    #Add docs CRUD hotspot Plan template
    docs.register(HotspotplantemplateAPI, blueprint='hotspotplan_api')
    docs.register(InfoHotspotplantemplateAPI, blueprint='hotspotplan_api')
    #Add docs CRUD hotspot Plan Site
    docs.register(HotspotplansiteAPI, blueprint='hotspotplan_api')
    docs.register(InfoHotspotplansiteAPI, blueprint='hotspotplan_api')