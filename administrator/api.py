from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

from .login import LoginOperatorsAPI
from .logout import LogoutOperatorsAPI
from .main import AdministratorAPI, MeAdministratorAPI, InfoAdministratorAPI
from .refresh_token import AdministratorRefreshToken
from .cron_task import CheckExpiredTokenAPI

administrator_api = Blueprint('administrator_api',__name__)
CORS(administrator_api, supports_credentials=True, resources=r'*', origins="*", allow_headers=["Content-Type", "Authorization", "Accept"], methods=['GET','POST','PUT','DELETE'])

api = Api(administrator_api)

api.add_resource(LoginOperatorsAPI, '/login')
api.add_resource(LogoutOperatorsAPI, '/logout')
api.add_resource(AdministratorAPI, '')
api.add_resource(InfoAdministratorAPI, '/<id>')
api.add_resource(MeAdministratorAPI, '/@me')
api.add_resource(AdministratorRefreshToken, '/@refresh_token')
api.add_resource(CheckExpiredTokenAPI, '/@checkexpiredtoken')

def init_docs(docs):
    #Add docs Administrator login
    docs.register(LoginOperatorsAPI, blueprint='administrator_api')
    #Add docs Administrator logout
    docs.register(LogoutOperatorsAPI, blueprint='administrator_api')
    #Add docs Administrator Refresh Token
    docs.register(AdministratorRefreshToken, blueprint='administrator_api')
    #Add docs Administrator API
    docs.register(AdministratorAPI, blueprint='administrator_api')
    docs.register(InfoAdministratorAPI, blueprint='administrator_api')
    docs.register(MeAdministratorAPI, blueprint='administrator_api')