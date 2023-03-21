from flask_sqlalchemy import SQLAlchemy

db_plan = SQLAlchemy()


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
    id = db_plan.Column(db_plan.String(255), primary_key=True, unique=True)
    name = db_plan.Column(db_plan.String(255), unique=True)
    uptime = db_plan.Column(db_plan.Integer, nullable=False)
    expired = db_plan.Column(db_plan.Integer, nullable=False)
    price = db_plan.Column(db_plan.Integer, nullable=False)
    kuota = db_plan.Column(db_plan.Integer, nullable=False)
    limit_shared = db_plan.Column(db_plan.Integer, nullable=False)
    type_id = db_plan.Column(db_plan.Integer, db_plan.ForeignKey('plan_type.id'), nullable=False)

    def __init__(self,id, name, uptime, expired, price, kuota, type_id, limit_shared=3):
        self.id = id
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

    def __init__(self, id,name, uptime, expired, price, kuota, type_id, limit_shared=3):
        self.id = id
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