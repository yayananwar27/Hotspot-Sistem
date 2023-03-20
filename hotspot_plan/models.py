from flask_sqlalchemy import SQLAlchemy
from secrets import token_hex
from helper import ambil_random

db_plan = SQLAlchemy()

def get_uuid(x : int):
    return token_hex(x)

def id_plandefault():
    id = str(get_uuid(8))
    i = False
    while i == False:
        id_exists = plan_default.query.filter_by(id=id).first()
        if id_exists is None:
            i = True
        else:
            i = False
            id = str(get_uuid(8))
    return id

def id_plansite(id_site):
    id = id_site+'-'+str(ambil_random(8))
    i = False
    while i == False:
        id_exists = plan_default.query.filter_by(id=id).first()
        if id_exists is None:
            i = True
        else:
            i = False
            id = id_site+'-'+str(ambil_random(8))
    return id

class plan_type(db_plan.Model):
    __tablename__="plan_type"
    id = db_plan.Column(db_plan.Integer(), primary_key=True,  unique=True, autoincrement=True)
    name = db_plan.Column(db_plan.String(255), unique=True)
    enable_uptime = db_plan.Column(db_plan.Boolean, default=False, nullable=False)
    enable_kuota = db_plan.Column(db_plan.Boolean, default=False, nullable=False)
    enable_expired = db_plan.Column(db_plan.Boolean, default=False, nullable=False)
    enable_limit_shared = db_plan.Column(db_plan.Boolean, default=False, nullable=False)
    plan_dafaulting = db_plan.relationship('plan_default', backref='plan_type', passive_deletes=True, lazy=True)

    def __init__(self, name, enable_uptime=False, enable_kuota=False, enable_expired=False, enable_limit_shared=False):
        self.name = name
        self.enable_uptime = enable_uptime
        self.enable_kuota = enable_kuota
        self.enable_expired = enable_expired
        self.enable_limit_shared = enable_limit_shared
    
    def get_data(self):
        data = {
            "id":self.id,
            "name":self.name,
            "enable_uptime":self.enable_uptime,
            "enable_kuota":self.enable_kuota,
            "enable_expired":self.enable_expired,
            "enable_limit_shared":self.enable_limit_shared
        }
        return data

class plan_default(db_plan.Model):
    __tablename__="plan_default"
    id = db_plan.Column(db_plan.String(255), primary_key=True, default=id_plandefault(), unique=True)
    name = db_plan.Column(db_plan.String(255), unique=True)
    uptime = db_plan.Column(db_plan.Integer, nullable=False)
    expired = db_plan.Column(db_plan.Integer, nullable=False)
    price = db_plan.Column(db_plan.Integer, nullable=False)
    kuota = db_plan.Column(db_plan.Integer, nullable=False)
    limit_shared = db_plan.Column(db_plan.Integer, nullable=False)
    type_id = db_plan.Column(db_plan.Integer, db_plan.ForeignKey('plan_type.id'), nullable=False)

    def __init__(self, name, uptime, expired, price, kuota, type_id, limit_shared=3):
        self.name = name
        self.uptime = uptime
        self.expired = expired
        self.price = price
        self.kuota = kuota
        self.limit_shared = limit_shared
        self.type_id = type_id

    def get_data(self):
        data = {
            "id":self.id,
            "name":self.name,
            "uptime":self.uptime,
            "expired":self.expired,
            "price":self.price,
            "kuota":self.kuota,
            "limit_shared":self.limit_shared,
            "type_id":self.type_id 
        }
        return data
    
class plan_site(db_plan.Model):
    __tablename__="plan_site"
    id = db_plan.Column(db_plan.String(255), primary_key=True, unique=True)
    name = db_plan.Column(db_plan.String(255), unique=True)
    uptime = db_plan.Column(db_plan.Integer, nullable=False)
    expired = db_plan.Column(db_plan.Integer, nullable=False)
    price = db_plan.Column(db_plan.Integer, nullable=False)
    kuota = db_plan.Column(db_plan.Integer, nullable=False)
    limit_shared = db_plan.Column(db_plan.Integer, nullable=False)
    type_id = db_plan.Column(db_plan.Integer, db_plan.ForeignKey('plan_type.id'), nullable=False)

    def __init__(self, id_site,name, uptime, expired, price, kuota, type_id, limit_shared=3):
        self.id = id_plansite(id_site)
        self.name = name
        self.uptime = uptime
        self.expired = expired
        self.price = price
        self.kuota = kuota
        self.limit_shared = limit_shared
        self.type_id = type_id

    def get_data(self):
        data = {
            "id":self.id,
            "name":self.name,
            "uptime":self.uptime,
            "expired":self.expired,
            "price":self.price,
            "kuota":self.kuota,
            "limit_shared":self.limit_shared,
            "type_id":self.type_id 
        }
        return data