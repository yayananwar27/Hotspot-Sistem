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

class radius_server(db_hs.Model):
    __tablename__="radius_server"
    id = db_hs.Column(db_hs.Integer, primary_key=True,  unique=True, autoincrement=True)
    host = db_hs.Column(db_hs.String(255))
    secret_key = db_hs.Column(db_hs.String(255))
    port = db_hs.Column(db_hs.Integer, nullable=False, default=5000)
    profile_id = db_hs.Column(db_hs.Integer, db_hs.ForeignKey('hotspot_profile.id', ondelete='CASCADE'), nullable=False)

class template_hotspot_plan(db_hs.Model):
    __tablename__="template_hotspot_plan"
    id_hotspot_prof = db_hs.Column(db_hs.Integer, db_hs.ForeignKey('hotspot_profile.id', ondelete='CASCADE'), nullable=False)
    id_template_plan  = db_hs.Column(db_hs.String(255), db_hs.ForeigKey('plan_template', ondelete='CASCADE'), nullable=False)
    