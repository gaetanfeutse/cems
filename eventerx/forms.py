from wtforms import (DateField, Form, HiddenField, IntegerField, PasswordField,
                     StringField, validators, TextAreaField)
from wtforms.fields.core import BooleanField, SelectField, SelectMultipleField

from wtforms.validators import EqualTo, Email, DataRequired


class LoginForm(Form):
    email = StringField('Email', [validators.Email()])
    password = PasswordField('Password')


class RegisterSchoolForm(Form):
    name = StringField('Institution / School name', validators=[validators.DataRequired()])
    phone_number = StringField('Phone Number', validators=[validators.DataRequired()])
    address1 = StringField('Address 1', validators=[validators.DataRequired()])
    address2 = StringField('Address 2')
    pobox = StringField('PO BOX')
    email_address = StringField('Email', validators=[validators.DataRequired(), validators.Email()])
    website = StringField('School Website')
    password = PasswordField('Master Password', validators=[validators.DataRequired()])


class RegisterStaffForm(Form):
    first_name = StringField('First Name', validators=[validators.DataRequired()])
    last_name = StringField('Last Name', validators=[validators.DataRequired()])
    email = StringField('Email', validators=[validators.DataRequired()])
    matricule = StringField('Matricule', validators=[validators.DataRequired()])
    phone_number = StringField('Phone Number', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])
    school_id = HiddenField(validators=[validators.DataRequired()])


class CreateEventForm(Form):
    title = StringField('Title', validators=[validators.DataRequired()])
    venue = StringField('Venue', validators=[validators.DataRequired()])
    description = TextAreaField("Description (Optional)", validators=[validators.Length(max=512)])
    budget = IntegerField('Budget')
    start_date = DateField('Event start date', validators=[validators.DataRequired()])
    due_date = DateField('Event End date', validators=[validators.DataRequired()])
    is_private = BooleanField("Private event")

class CreateCommissionForm(Form):
    title = StringField('Title', validators=[validators.DataRequired()])
    description = TextAreaField("Description (Optional)", validators=[validators.Length(max=512)])
    start_date = DateField('Event start date', validators=[validators.DataRequired()])
    due_date = DateField('Event End date', validators=[validators.DataRequired()])
    priority = SelectField("Priority", validators=[validators.DataRequired()])
    state = SelectField("Commission state", validators=[validators.DataRequired()])

class CreateTeamForm(Form):
    title = StringField('Title', validators=[validators.DataRequired()])
    members = SelectMultipleField("Add members", validators=[validators.DataRequired()])
    commissions = SelectMultipleField("Assign Commission(s)", validators=[validators.DataRequired()])


class StudentRegistrationForm(Form):
    first_name = StringField('First Name', validators=[validators.DataRequired()])
    last_name = StringField('Last Name', validators=[validators.DataRequired()])
    email = StringField('Email', validators=[validators.DataRequired()])
    matricule = StringField('Matricule', validators=[validators.DataRequired()])
    phone_number = StringField('Phone Number', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])
    school_id = HiddenField(validators=[validators.DataRequired()])
    speciality = StringField('Speciality', validators=[validators.DataRequired()])
    student_class = StringField('Class (Level)', validators=[validators.DataRequired()])
    