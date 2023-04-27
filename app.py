from flask import Flask
from config import ApplicationConfig
from flask_apispec.extension import FlaskApiSpec
from flask_migrate import Migrate
from flask_cors import CORS

from administrator.models import db_admin, init_app as admin_init_app
from administrator.api import administrator_api, init_docs as admin_init_docs

#HotspotPlan Segment
from hotspot_plan.models import db_plan, init_app as plan_init_app
from hotspot_plan.api import hotspotplan_api, init_docs as plan_init_docs

#HotspotProfile Segment
from hotspot_profile.models import db_hs, init_app as hs_init_app
from hotspot_profile.api import hotspotprofile_api, init_docs as hs_init_docs

#Hotspot Site Segement
from sites.models import db_site, init_app as site_init_app
from sites.api import site_api, init_docs as site_init_docs
from config import scheduler

app = Flask(__name__)
CORS(app, supports_credentials=True, resources=r'*', origins="*", allow_headers=["Content-Type", "Authorization", "Accept"], methods=['GET','POST','PUT','DELETE'])
app.config.from_object(ApplicationConfig)

# tambahkan ini untuk menggunakan Flask-Migrate
migrate_administrator = Migrate(app, db_admin)
migrate_hotspotplan = Migrate(app, db_plan)
migrate_hotspotprofile = Migrate(app, db_hs)
migrate_site = Migrate(app, db_site)

#import yang di schedeluer
from administrator.cron_task import expired_token_admin_check, init_cron_app
init_cron_app(app)
#Init Scheduler
#scheduler.init_app(app)


#Model init table
from config import db
db.init_app(app)
admin_init_app(app)
plan_init_app(app)
hs_init_app(app)
site_init_app(app)

with app.app_context():
    scheduler.start()
    docs = FlaskApiSpec(app)

    #register Administrator
    app.register_blueprint(administrator_api, url_prefix='/administrator')
    admin_init_docs(docs)

    #register Hotspot Plan
    app.register_blueprint(hotspotplan_api, url_prefix='/hotspot_plan')
    plan_init_docs(docs)

    #register Hostpot Profile
    app.register_blueprint(hotspotprofile_api, url_prefix='/hotspot_profile')
    hs_init_docs(docs)

    #register site
    app.register_blueprint(site_api, url_prefix='/site')
    site_init_docs(docs)

# fungsi untuk menghentikan scheduler
def shutdown_scheduler():
    scheduler.shutdown()

if __name__ == "__main__":
    app.run('0.0.0.0', debug=True)
    app.teardown_appcontext(shutdown_scheduler)
    