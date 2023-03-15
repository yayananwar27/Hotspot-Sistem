from .models import admin_log, db_admin

def authentication_logging_login(accessed, access_payload, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'authentication', 'login', access_payload, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True


def authentication_logging_logout(accessed, access_payload, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'authentication', 'logout', access_payload, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True

def administrator_logging_create(accessed, admincreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'administrator', 'create', admincreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True

def administrator_logging_update(accessed, admincreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'administrator', 'update', admincreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True

def administrator_logging_delete(accessed, admincreate, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'administrator', 'delete', admincreate, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True

def authentication_logging_refreshtoken(accessed, access_payload, refrence_id, administrator_id):
    new_log = admin_log(accessed, 'authentication', 'refresh_token', access_payload, refrence_id, administrator_id)
    db_admin.session.add(new_log)
    db_admin.session.commit()
    return True