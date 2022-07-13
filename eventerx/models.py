from eventerx import db, login_manager
from flask_login import UserMixin
from datetime import datetime



class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country_name = db.Column(db.String(20))

    def __repr__(self) -> str:
        return f"<Country {self.country_name}>"


class Town(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    town_name = db.Column(db.String(20))

    country_id = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=False)
    country = db.relationship('Country', backref=db.backref('towns', lazy=True, cascade="all, delete-orphan"))


    def __repr__(self) -> str:
        return f"<Town {self.town_name}>"


class UserRoles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))
    
    def __repr__(self) -> str:
        return f"<UserRole {self.name}>"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    first_name = db.Column(db.String(25))
    last_name = db.Column(db.String(25))
    password = db.Column(db.String(250))
    profile_picture = db.Column(db.String(250))
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    role_id = db.Column(db.Integer, db.ForeignKey('user_roles.id'), nullable=False)
    role = db.relationship('UserRoles', backref=db.backref('users', lazy=True, cascade="all, delete-orphan"))

    @property
    def fullname(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def username(self):
        return f"@{self.fullname.title().replace(' ', '')}_{self.id}"

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class SchoolInstitution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(25), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    address1 = db.Column(db.String(10), nullable=False)
    address2 = db.Column(db.String(10))
    phone = db.Column(db.String(10), nullable=False)
    pobox = db.Column(db.Integer)
    website = db.Column(db.String(100))    
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<School {self.name}>"


class Student(db.Model):
    matricule = db.Column(db.String(50), primary_key=True)
    speciality = db.Column(db.String(50))
    phone = db.Column(db.String(50), nullable=False)
    student_class = db.Column(db.String(50), nullable=False)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    school_institution_id = db.Column(db.Integer, db.ForeignKey('school_institution.id'), nullable=False)
    # backrefs
    user = db.relationship('User', backref=db.backref('students', lazy=True, cascade="all, delete-orphan"))
    school_institution = db.relationship('SchoolInstitution', backref=db.backref('students', lazy=True, cascade="all, delete-orphan"))

    def __repr__(self) -> str:
        return f"<Student {self.matricule}>"


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Foreign keys
    school_institution_id = db.Column(db.Integer, db.ForeignKey('school_institution.id'), nullable=False)
    # backrefs
    school_institution = db.relationship('SchoolInstitution', backref=db.backref('teams', lazy=True, cascade="all, delete-orphan"))


class StaffMember(db.Model):
    matricule = db.Column(db.String(50), primary_key=True)
    phone = db.Column(db.String(50), nullable=False)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    school_institution_id = db.Column(db.Integer, db.ForeignKey('school_institution.id'), nullable=False)
    # backrefs
    user = db.relationship('User', backref=db.backref('staff_members', lazy=True, cascade="all, delete-orphan"))
    team = db.relationship('Team', backref=db.backref('staff_members', lazy=True))
    school_institution = db.relationship('SchoolInstitution', backref=db.backref('staff_members', lazy=True, cascade="all, delete-orphan"))


class EventProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    venue = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(512))
    start_date = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    budget = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Integer, default=1, nullable=False)
    private = db.Column(db.SmallInteger, nullable=False, default=0)
    
    # Foreign keys
    school_institution_id = db.Column(db.Integer, db.ForeignKey('school_institution.id'), nullable=False)
    # backrefs
    school_institution = db.relationship('SchoolInstitution', backref=db.backref('event_projects', lazy=True, cascade="all, delete-orphan"))

    
class TaskState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    
class CommissionStates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


class Commission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(512))
    start_date = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    priority = db.Column(db.Integer)
    
    # Foreign keys
    event_project_id = db.Column(db.Integer, db.ForeignKey('event_project.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    state_id = db.Column(db.Integer, db.ForeignKey('commission_states.id'), nullable=False)
    # backrefs
    event_project = db.relationship('EventProject', backref=db.backref('commissions', lazy=True, cascade="all, delete-orphan"))
    team = db.relationship('Team', backref=db.backref('commissions', lazy=True))
    commision_state = db.relationship('CommissionStates', backref=db.backref('commissions', lazy=True, cascade="all, delete-orphan"))


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    manager_matricule = db.Column(db.String(50), db.ForeignKey('staff_member.matricule'), nullable=False)
    manager = db.relationship('StaffMember', backref=db.backref('tasks', lazy=True, cascade="all, delete-orphan"))


class ExternalAttendee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(50), nullable=False)


class ServiceProvider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    phone = db.Column(db.String(15))
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    role_id = db.Column(db.Integer, db.ForeignKey('user_roles.id'), nullable=False)
    role = db.relationship('UserRoles', backref=db.backref('user', lazy=True, cascade="all, delete-orphan"))


class InvitationCode(db.Model):
    code = db.Column(db.String(200), unique=True, primary_key=True)
    duration = db.Column(db.Integer)
    purpose = db.Column(db.String(100))
    school_institution_id = db.Column(db.Integer, db.ForeignKey('school_institution.id'), nullable=False)


    def __repr__(self):
        return f"<InvitationCode '{self.code}'>"


@login_manager.user_loader
def load_user(user_id):
    """This callback is used to reload the user object from the user ID stored in the session. 
    It should take the unicode ID of a user, and return the corresponding user object."""
    return User.query.get(user_id)