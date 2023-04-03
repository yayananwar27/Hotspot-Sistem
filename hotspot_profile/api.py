from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

from .hotspot_profile import HotspotprofileAPI, InfoHotspotprofileAPI
from .template import HotspotprofiletemplateAPI, InfoHotspotprofiletemplateAPI

hotspotprofile_api = Blueprint('hotspotprofile_api',__name__)
CORS(hotspotprofile_api, supports_credentials=True, resources=r'*', origins="*", allow_headers=["Content-Type", "Authorization", "Accept"], methods=['GET','POST','PUT','DELETE'])

api = Api(hotspotprofile_api)

api.add_resource(HotspotprofileAPI, '')
api.add_resource(InfoHotspotprofileAPI, '/<id>')

api.add_resource(HotspotprofiletemplateAPI, '/template')
api.add_resource(InfoHotspotprofiletemplateAPI, '/template/<id>')

def init_docs(docs):
    docs.register(HotspotprofileAPI, blueprint='hotspotprofile_api')
    docs.register(InfoHotspotprofileAPI, blueprint='hotspotprofile_api')

    docs.register(HotspotprofiletemplateAPI, blueprint='hotspotprofile_api')    
    docs.register(InfoHotspotprofiletemplateAPI, blueprint='hotspotprofile_api')    