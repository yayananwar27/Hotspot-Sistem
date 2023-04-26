from administrator.models import admin_log, db_admin

def site_logging_create(accessed, sitecreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'site', 'create', sitecreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True

def site_logging_update(accessed, siteupdate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'site', 'update', siteupdate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True

def site_logging_delete(accessed, sitedelete, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'site', 'delete', sitedelete, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True