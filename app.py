from flask import Flask
from config import ApplicationConfig
from flask_apispec.extension import FlaskApiSpec
from flask_migrate import Migrate


from administrator.models import db_admin, init_app as admin_init_app
from administrator.api import administrator_api
from administrator.login import LoginOperatorsAPI
from administrator.logout import LogoutOperatorsAPI
from administrator.main import AdministratorAPI, MeAdministratorAPI, InfoAdministratorAPI
from administrator.refresh_token import AdministratorRefreshToken

#HotspotPlan Segment
from hotspot_plan.models import db_plan, init_app as plan_init_app
from hotspot_plan.api import hotspotplan_api
from hotspot_plan.plantype import HotspotplantypeAPI, InfoHotspotplantypeAPI
from hotspot_plan.plandefault import HotspotplandefaultAPI, InfoHotspotplandefaultAPI
from hotspot_plan.plansite import HotspotplansiteAPI, InfoHotspotplansiteAPI

from config import scheduler

app = Flask(__name__)
app.config.from_object(ApplicationConfig)

# tambahkan ini untuk menggunakan Flask-Migrate
migrate_administrator = Migrate(app, db_admin)
migrate_hotspotplan = Migrate(app, db_plan)

#import yang di schedeluer
from administrator.cron_task import expired_token_admin_check
#Init Scheduler
#scheduler.init_app(app)


#Model init table
from config import db
db.init_app(app)
admin_init_app(app)
plan_init_app(app)

with app.app_context():
    scheduler.start()
    docs = FlaskApiSpec(app)

    #register Administrator
    app.register_blueprint(administrator_api, url_prefix='/administrator')
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

    #register Hotspot Plan
    app.register_blueprint(hotspotplan_api, url_prefix='/hotspot_plan')
    #Add docs CRUD hotspot Plan Type
    docs.register(HotspotplantypeAPI, blueprint='hotspotplan_api')
    docs.register(InfoHotspotplantypeAPI, blueprint='hotspotplan_api')
    #Add docs CRUD hotspot Plan default
    docs.register(HotspotplandefaultAPI, blueprint='hotspotplan_api')
    docs.register(InfoHotspotplandefaultAPI, blueprint='hotspotplan_api')
    #Add docs CRUD hotspot Plan Site
    docs.register(HotspotplansiteAPI, blueprint='hotspotplan_api')
    docs.register(InfoHotspotplansiteAPI, blueprint='hotspotplan_api')

# fungsi untuk menghentikan scheduler
def shutdown_scheduler():
    scheduler.shutdown()

if __name__ == "__main__":
    app.run('0.0.0.0', debug=True)
    app.teardown_appcontext(shutdown_scheduler)
    