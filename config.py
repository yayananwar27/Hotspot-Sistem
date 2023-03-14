from dotenv import load_dotenv
import os
load_dotenv()

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
import redis

from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()

#from flask_apscheduler import APScheduler
#scheduler = APScheduler()

class redis_conn:
    def __init__(self):
        self.key = ''
        self.r = redis.from_url("redis://{0}:{1}".format(os.environ["REDIS_HOST"],os.environ["REDIS_PORT"]))
        self.value = ''
        
    def get(self, key):
        data = self.r.get(key)
        return data

    def set(self, key, value):
        data = self.r.set(key, value)
        return data

    def delete(self, key):
        data = self.r.delete(key)
        return data


class ApplicationConfig:
    SECRET_KEY = os.environ["SECRET_KEY"]

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = "mysql://{0}:{1}@{2}:{3}/{4}".format(os.environ["DATABASE_USER"],os.environ["DATABASE_PASSWORD"],os.environ["DATABASE_HOST"],os.environ["DATABASE_PORT"],os.environ["DATABASE_DB"])

    #SESSION_TYPE = "redis"
    #SESSION_PERMANENT = False
    #SESSION_USE_SIGNER = True
    #SESSION_REDIS = redis.from_url("redis://172.16.26.97:6379")

    APISPEC_SPEC = APISpec(
        title='HS Sistem',
        version='1.0.0',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    )
    APISPEC_SWAGGER_URL = "/swagger/"  # URI to access API Doc JSON
    APISPEC_SWAGGER_UI_URL = '/swagger-ui/'  # URI to access UI of API Doc