from administrator.models import admin_log, db_admin

def plantype_logging_create(accessed, planttypecreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'plan_type', 'create', planttypecreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True

def plantype_logging_update(accessed, planttypecreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'plan_type', 'update', planttypecreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True

def plantype_logging_delete(accessed, planttypecreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'plan_type', 'delete', planttypecreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True

def plantemplate_logging_create(accessed, planttypecreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'plan_default', 'create', planttypecreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True

def plantemplate_logging_update(accessed, planttypecreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'plan_default', 'update', planttypecreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True

def plantemplate_logging_delete(accessed, planttypecreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'plan_default', 'delete', planttypecreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True

def plansite_logging_create(accessed, planttypecreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'plan_site', 'create', planttypecreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True

def plansite_logging_update(accessed, planttypecreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'plan_site', 'update', planttypecreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True

def plansite_logging_delete(accessed, planttypecreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'plan_site', 'delete', planttypecreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True