from flask_sqlalchemy import SQLAlchemy
from secrets import token_hex
from helper import get_datetime


db_admin = SQLAlchemy()

def get_uuid(x : int):
    return token_hex(x)

def get_requestid():
    unix_time = get_datetime()
    data = str(get_uuid(8))+'-'+str(get_uuid(4))+'-'+str(get_uuid(4))+'-'+str(get_uuid(4))+'-'+str(unix_time.unix())
    return data

def get_requestidref():
    data = str(get_uuid(8))+'-'+str(get_uuid(4))+'-'+str(get_uuid(4))+'-'+str(get_uuid(4))+'-'+str(get_uuid(12))
    return data

def get_logid():
    #unix_time = get_datetime()
    #data = str(get_uuid(16))+str(unix_time.unix())
    try:
        id = admin_log.query.order_by(admin_log.id.desc()).first()
        id = id.id
        if id:
            _id = int(id)
            _id = _id+1
            return _id
    except:
        return 1
    
    

class administrator(db_admin.Model):
    __tablename__ = "administrator"
    id = db_admin.Column(db_admin.String(255), primary_key=True, unique=True, default=get_uuid(8))
    email = db_admin.Column(db_admin.String(255), unique=True)
    password = db_admin.Column(db_admin.Text, nullable=False)
    fullname = db_admin.Column(db_admin.String(255))
    created_at = db_admin.Column(db_admin.DateTime, default=get_datetime())
    active = db_admin.Column(db_admin.Boolean, default=True, nullable=False)
    logging = db_admin.relationship('admin_log', backref='administrator', cascade="all, delete", passive_deletes=True, lazy=True)
    tokening = db_admin.relationship('admin_token', backref='administrator', cascade="all, delete", passive_deletes=True, lazy=True)
    tokening_old = db_admin.relationship('admin_token_old', backref='administrator', cascade="all, delete", passive_deletes=True, lazy=True)

    def __init__(self, email, password, fullname, active):
        self.email = email
        self.password = password
        self.fullname = fullname
        self.active = active
    

    def get_data(self):
        data = {
            "id":self.id, 
            "email":self.email, 
            "fullname":self.fullname, 
            "created_at":self.created_at, 
            "active":self.active
            }
        return data

class admin_token(db_admin.Model):
    __tablename__ = "admin_token"
    request_id = db_admin.Column(db_admin.String(255), primary_key=True, unique=True)
    admin_id = db_admin.Column(db_admin.String(255), db_admin.ForeignKey('administrator.id', ondelete='CASCADE'), nullable=False)
    type_token = db_admin.Column(db_admin.String(100), nullable=False)
    token_value = db_admin.Column(db_admin.Text, unique=True, nullable=False)
    expired = db_admin.Column(db_admin.Integer, nullable=False)
    allowed_access = db_admin.Column(db_admin.Text, nullable=False)
    created_at = db_admin.Column(db_admin.DateTime, default=get_datetime())

    def __init__(self, admin_id, type_token, token_value, expired, allowed_access):
        self.admin_id = admin_id
        self.type_token = type_token
        self.token_value = token_value
        self.expired = expired
        self.allowed_access = allowed_access
        if self.type_token == 'refresh_token':
            self.request_id = get_requestidref()
        else:
            self.request_id = get_requestid()
        
    def get_data(self):
        data = {
            "request_id": self.request_id,
            "admin_id": self.admin_id,
            "type_token": self.type_token,
            "token_value": self.token_value,
            "expired": self.expired,
            "allowed_access": self.allowed_access,
            "created_at": self.created_at
        }
        return data

class admin_token_old(db_admin.Model):
    __tablename__ = "admin_token_old"
    request_id = db_admin.Column(db_admin.String(255), primary_key=True, unique=True)
    admin_id = db_admin.Column(db_admin.String(255), db_admin.ForeignKey('administrator.id', ondelete='CASCADE'), nullable=False)
    type_token = db_admin.Column(db_admin.String(100), nullable=False)
    token_value = db_admin.Column(db_admin.Text, nullable=False)
    expired = db_admin.Column(db_admin.Integer, nullable=False)
    allowed_access = db_admin.Column(db_admin.Text, nullable=False)
    created_at = db_admin.Column(db_admin.DateTime)

    def __init__(self, request_id, admin_id, type_token, token_value, expired, allowed_access, created_at):
        self.request_id= request_id
        self.admin_id = admin_id
        self.type_token = type_token
        self.token_value = token_value
        self.expired = expired
        self.allowed_access = allowed_access
        self.created_at = created_at
        
    def get_data(self):
        data = {
            "request_id": self.request_id,
            "admin_id": self.admin_id,
            "type_token": self.type_token,
            "token_value": self.token_value,
            "expired": self.expired,
            "allowed_access": self.allowed_access,
            "created_at": self.created_at
        }
        return data

class admin_log(db_admin.Model):
    __tablename__ = "admin_log"
    id = db_admin.Column(db_admin.Integer, primary_key=True, unique=True, autoincrement=True)
    accessed = db_admin.Column(db_admin.Text, nullable=False)
    log_object = db_admin.Column(db_admin.String(255), nullable=False)
    action = db_admin.Column(db_admin.String(255), nullable=False)
    description = db_admin.Column(db_admin.Text)
    timestamp = db_admin.Column(db_admin.DateTime, default=get_datetime())
    refrence_id = db_admin.Column(db_admin.String(255))
    admin_id = db_admin.Column(db_admin.String(255), db_admin.ForeignKey('administrator.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, accessed, log_object, action, description, refrence_id, admin_id):
        self.accessed = accessed
        self.log_object = log_object
        self.action = action
        self.description = description
        self.refrence_id = refrence_id
        self.admin_id = admin_id

    def get_data(self):
        data = {
            "id": self.id,
            "accessed": self.accessed,
            "log_object": self.log_object,
            "action": self.action,
            "description": self.description,
            "timestamp": self.timestamp,
            "refrence_id": self.refrence_id,
            "admin_id": self.admin_id
        }
        return data