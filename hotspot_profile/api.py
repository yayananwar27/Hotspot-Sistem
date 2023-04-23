from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

from .hotspot_profile import HotspotprofileAPI, InfoHotspotprofileAPI
from .template import HotspotprofiletemplateAPI, InfoHotspotprofiletemplateAPI, ListInfoHotspotprofiletemplateAPI
from .radius_server import HotspotprofileradiusAPI, InfoHotspotprofileradiusAPI, GenerateHotspotprofileradiusAPI

hotspotprofile_api = Blueprint('hotspotprofile_api',__name__)
CORS(hotspotprofile_api, supports_credentials=True, resources=r'*', origins="*", allow_headers=["Content-Type", "Authorization", "Accept"], methods=['GET','POST','PUT','DELETE'])

api = Api(hotspotprofile_api)

api.add_resource(HotspotprofileAPI, '')
api.add_resource(InfoHotspotprofileAPI, '/<id>')
api.add_resource(ListInfoHotspotprofiletemplateAPI, '/<id>/template')

api.add_resource(HotspotprofiletemplateAPI, '/template')
api.add_resource(InfoHotspotprofiletemplateAPI, '/template/<id>')

api.add_resource(HotspotprofileradiusAPI, '/radius_server')
api.add_resource(InfoHotspotprofileradiusAPI, '/radius_server/<id>')
api.add_resource(GenerateHotspotprofileradiusAPI, '/radius_server/<id>/generate_secret')

def init_docs(docs):
    docs.register(HotspotprofileAPI, blueprint='hotspotprofile_api')
    docs.register(InfoHotspotprofileAPI, blueprint='hotspotprofile_api')
    docs.register(ListInfoHotspotprofiletemplateAPI, blueprint='hotspotprofile_api')

    docs.register(HotspotprofiletemplateAPI, blueprint='hotspotprofile_api')    
    docs.register(InfoHotspotprofiletemplateAPI, blueprint='hotspotprofile_api')   

    docs.register(HotspotprofileradiusAPI, blueprint='hotspotprofile_api')
    docs.register(InfoHotspotprofileradiusAPI, blueprint='hotspotprofile_api')
    docs.register(GenerateHotspotprofileradiusAPI, blueprint='hotspotprofile_api') 