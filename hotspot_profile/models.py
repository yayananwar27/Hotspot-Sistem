from config import db
db_hs = db

def init_app(app):
    with app.app_context():
        db_hs.create_all()

class hotspot_profile(db_hs.Model):
    __tablename__="hotspot_profile"
    id = db_hs.Column(db_hs.Integer, primary_key=True,  unique=True, autoincrement=True)
    name = db_hs.Column(db_hs.String(255), unique=True)
    radius_servering = db_hs.relationship('radius_server', backref='hotspot_profile', cascade="all, delete", passive_deletes=True, lazy=True)
    templating = db_hs.relationship('template_hotspot_plan', backref='hotspot_profile', cascade="all, delete", passive_deletes=True, lazy=True)
    siteing = db_hs.relationship('site', backref=   'hotspot_profile', cascade="all, delete", passive_deletes=True, lazy=True)

    def __init__(self, name):
        self.name = name

    def get_data(self):
        data = {
            'id': self.id,
            'name': self.name
        }
        return data

class radius_server(db_hs.Model):
    __tablename__="radius_server"
    id = db_hs.Column(db_hs.Integer, primary_key=True,  unique=True, autoincrement=True)
    host = db_hs.Column(db_hs.String(255))
    secret_key = db_hs.Column(db_hs.String(255))
    port = db_hs.Column(db_hs.Integer, nullable=False, default=5000)
    profile_id = db_hs.Column(db_hs.Integer, db_hs.ForeignKey('hotspot_profile.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, host, secret_key, profile_id, port=5000):
        self.host = host
        self.secret_key = secret_key
        self.profile_id = profile_id
        self.port = port
    
    def get_data(self):
        data = {
            'id': self.id,
            'host': self.host,
            'secret_key': self.secret_key,
            'port': self.port,
            'profile_id': self.profile_id
        }
        return data

class template_hotspot_plan(db_hs.Model):
    __tablename__="template_hotspot_plan"
    id = db_hs.Column(db_hs.Integer, primary_key=True,  unique=True, autoincrement=True)
    id_hotspot_profile = db_hs.Column(db_hs.Integer, db_hs.ForeignKey('hotspot_profile.id', ondelete='CASCADE'), nullable=False)
    id_plan_template  = db_hs.Column(db_hs.String(255), db_hs.ForeignKey('plan_template.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, id_hotspot_profile, id_plan_template):
        self.id_hotspot_profile = id_hotspot_profile
        self.id_plan_template = id_plan_template

    def get_data(self):
        data = {
            'id' : self.id,
            'id_hotspot_profile' : self.id_hotspot_profile,
            'id_plan_template': self.id_plan_template
        }
        return data
        
    