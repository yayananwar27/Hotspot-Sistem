from administrator.models import admin_log, db_admin

def planttype_logging_create(accessed, planttypecreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'plant_type', 'create', planttypecreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True

def planttype_logging_update(accessed, planttypecreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'plant_type', 'update', planttypecreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True

def planttype_logging_delete(accessed, planttypecreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'plant_type', 'delete', planttypecreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True