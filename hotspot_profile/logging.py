from administrator.models import admin_log, db_admin

def hotspotprofile_logging_create(accessed, hotspotprofilecreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'hotspot_profile', 'create', hotspotprofilecreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True

def hotspotprofile_logging_update(accessed, hotspotprofilecreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'hotspot_profile', 'update', hotspotprofilecreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True

def hotspotprofile_logging_delete(accessed, hotspotprofilecreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'hotspot_profile', 'delete', hotspotprofilecreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True

def hotspotprofiletemplate_logging_create(accessed, hotspotprofilecreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'hotspot_profile_template', 'create', hotspotprofilecreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True

def hotspotprofiletemplate_logging_update(accessed, hotspotprofilecreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'hotspot_profile_template', 'update', hotspotprofilecreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True

def hotspotprofiletemplate_logging_delete(accessed, hotspotprofilecreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'hotspot_profile_template', 'delete', hotspotprofilecreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True