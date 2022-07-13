from datetime import datetime
import json
import os


from eventerx import PROJECT_FILES_FOLDER, db, bcrypt
from eventerx.models import CommissionStates, Country, InvitationCode, TaskState, Town, UserRoles, User


def get_project_file(filename):
    try:
        with open( os.path.join(PROJECT_FILES_FOLDER, filename), "r") as raw_file:
            return raw_file.read()
    except:
        raise


def setup_cities():
    """Load the `cities.json` files and add the values to the db"""
    raw_file_content = get_project_file("cities.json")
    content = json.loads(raw_file_content)
    try:
        for country_item in content['countries']:
            country = Country(country_name=country_item.get('name'))
            db.session.add(country)
            db.session.flush()
            for town_item in country_item.get('towns'):
                town = Town(town_name=town_item.get('name'), country_id=country.id)
                db.session.add(town)
                db.session.flush()
        db.session.commit()

    except:
        db.session.rollback()
        raise

def setup_root_user():
    email = "gaetanfeutse@gmail.com"
    password = bcrypt.generate_password_hash("password").decode("utf-8")
    first_name = "GAETAN"
    last_name = "FEUTSE"
    role_id = 1

    try:
        db.session.add(User(email=email, password=password, first_name=first_name, last_name=last_name, role_id=role_id) )
        db.session.commit()
    except:
        db.session.rollback()
        raise


def setup_user_roles():
    raw_roles = json.loads(get_project_file("roles.json"))
    for role_item in raw_roles.get('roles'):
        user_role = UserRoles(**role_item)
        db.session.add(user_role)
    
    try:
        db.session.commit()

    except:
        db.session.rollback()
        raise


def setup_tasks_states():
    raw_states = json.loads(get_project_file("task_states.json"))
    for raw_state in raw_states.get('states'):
        task_state = CommissionStates(**raw_state)
        db.session.add(task_state)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise


def db_get_started():
    setup_user_roles()
    setup_root_user()
    setup_tasks_states()
    setup_cities()
    

def check_invitation_code(code):
    invitation_code = InvitationCode.query.get(code)
    # first check if the invitation code exists
    if invitation_code != None:
        # return if the code is still valid or not
        is_valid = datetime.now().date() <= datetime.fromtimestamp(invitation_code.duration).date()
        return invitation_code if is_valid else False
    else:
        return False