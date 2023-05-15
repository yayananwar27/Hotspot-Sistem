from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS


from .site import SiteAPI, InfoSiteAPI, ListSiteprofile

site_api = Blueprint('site_api', __name__)
CORS(site_api, supports_credentials=True, resources=r'*', origins="*", allow_headers=["Content-Type", "Authorization", "Accept"], methods=['GET','POST','PUT','DELETE'])

api = Api(site_api)

api.add_resource(SiteAPI, '')
api.add_resource(InfoSiteAPI, '/<id>')
api.add_resource(ListSiteprofile, '/hotspot_profile/<id>')

def init_docs(docs):
    docs.register(SiteAPI, blueprint='site_api')
    docs.register(InfoSiteAPI, blueprint='site_api')
    docs.register(ListSiteprofile, blueprint='site_api')