from config import db
db_site = db

def init_app(app):
    with app.app_context():
        db_site.create_all()


class site(db_site.Model):
    __tablename__ = "site"
    id = db_site.Column(db_site.String(50), primary_key=True, unique=True)
    name = db_site.Column(db_site.String(255), unique=True)
    landing_name = db_site.Column(db_site.String(255), nullable=True)
    profile_id = db_site.Column(db_site.Integer, db_site.ForeignKey('hotspot_profile.id', ondelete='CASCADE'), nullable=False)
    
    def __init__(self, id, name, landing_name, profile_id):
        self.id = id
        self.name = name
        self.landing_name = landing_name
        self.profile_id = profile_id

    def get_data(self):
        data = {
            'id': self.id, 
            'name': self.name,
            'landing_name': self.landing_name,
            'profile_id' : self.profile_id
        }
        return data

class site_hotspot_plan(db_site.Model):
    __tablename__ = "site_hotspot_plan"
    id = db_site.Column(db_site.Integer, primary_key=True,  unique=True, autoincrement=True)
    id_site = db_site.Column(db_site.String(50), db_site.ForeignKey('site.id', ondelete='CASCADE'), nullable=False)
    id_site_plan = db_site.Column(db_site.String(255), db_site.ForeignKey('plan_site.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, id_site, id_site_plan):
        self.id_site = id_site
        self.id_site_plan = id_site_plan

    def get_data(self):
        data = {
            'id_site': self.id, 
            'id_site_plan': self.id_site_plan
        }

        return data

class site_landing_template(db_site.Model):
    id = db_site.Column(db_site.Integer, primary_key=True,  unique=True, autoincrement=True)
    id_site = db_site.Column(db_site.String(50), db_site.ForeignKey('site.id', ondelete='CASCADE'), nullable=False)
    

    