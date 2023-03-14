from flask import Flask
from config import ApplicationConfig
from flask_apispec.extension import FlaskApiSpec

from administrator.models import db_admin

from administrator.api import administrator_api
from administrator.login import LoginOperatorsAPI
from administrator.logout import LogoutOperatorsAPI
from administrator.main import AdministratorAPI, MeAdministratorAPI
from administrator.refresh_token import AdministratorRefreshToken

from config import scheduler

app = Flask(__name__)
app.config.from_object(ApplicationConfig)

#import yang di schedeluer
from administrator.cron_task import expired_token_admin_check
#Init Scheduler
#scheduler.init_app(app)


#Model init table
db_admin.init_app(app)

with app.app_context():
    scheduler.start()
    db_admin.create_all()

    #scheduler.add_job(
    #    func=expired_token_check,
    #    trigger="interval",
    #    seconds=10,
    #    id="test job 2",
    #    name="test job 2",
    #    replace_existing=True,
    #)


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
docs.register(MeAdministratorAPI, blueprint='administrator_api')

# fungsi untuk menghentikan scheduler
def shutdown_scheduler():
    scheduler.shutdown()



if __name__ == "__main__":
    app.run('0.0.0.0', debug=True)
    app.teardown_appcontext(shutdown_scheduler)
    