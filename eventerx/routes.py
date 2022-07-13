from datetime import datetime, timedelta
from eventerx.utils import check_invitation_code
from secrets import token_hex

from flask import flash, render_template, request, abort
from flask.helpers import url_for
from flask_login import current_user, login_required, logout_user
from flask_login.utils import login_user
from werkzeug.utils import redirect

from eventerx import app, bcrypt, db
from eventerx.forms import CreateCommissionForm, CreateEventForm, CreateTeamForm, LoginForm, RegisterSchoolForm, RegisterStaffForm, StudentRegistrationForm
from eventerx.models import (Commission, CommissionStates, EventProject, InvitationCode, SchoolInstitution,
                             StaffMember, Student, Team, User)


@app.route("/")
@login_required
def homepage():
    school = SchoolInstitution.query.filter_by(
        email=current_user.email).first()

    if current_user.role.id == 3:  # only managers
        staff = StaffMember.query.filter_by(
            user_id=current_user.id).first().tasks
        return render_template("eventerx/pages/admin_homepage.html", current_user=current_user, page={'title': 'dashboard'}, school=school)

    else:
        return render_template("eventerx/pages/homepage.html", current_user=current_user, page={'title': 'dashboard'}, school=school)


@app.route('/calendar')
@login_required
def calendar():
    school = SchoolInstitution.query.filter_by(
        email=current_user.email).first()
    return render_template('eventerx/pages/calendar.html', current_user=current_user, page={'title': 'calendar'}, school=school)


@app.route('/chat')
@login_required
def chat():
    return render_template("eventerx/pages/chat.html", current_user=current_user, page={'title': 'chat'})


@app.route('/events')
@login_required
def events():
    if current_user.role.id != 3:  # only managers
        return "<h1>Access denied</h1>", 403
    events = EventProject.query.filter_by().all()
    school = SchoolInstitution.query.filter_by(
        email=current_user.email).first()
    return render_template('eventerx/pages/events.html', current_user=current_user, page={'title': 'events'}, events=events, school=school)


@app.route('/add/event', methods=['GET', 'POST'])
@login_required
def add_event():
    if current_user.role.id != 3:  # only managers
        return "<h1>Access denied</h1>", 403

    form = CreateEventForm(request.form)
    if request.method == "POST" and form.validate():
        school_id = StaffMember.query.filter_by(
            user_id=current_user.id).first().school_institution_id
        event = EventProject(title=form.title.data, venue=form.venue.data, description=form.description.data,
                             start_date=form.start_date.data, due_date=form.due_date.data, budget=form.budget.data, school_institution_id=school_id)
        db.session.add(event)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
        else:
            return redirect(url_for('events'))

    else:
        print(form.errors)

    school = SchoolInstitution.query.filter_by(
        email=current_user.email).first()
    return render_template('eventerx/pages/add_event.html', current_user=current_user, page={'title': 'events'}, events=events, school=school, form=form)


@app.route('/event/<string:event_id>')
@login_required
def event_details(event_id):

    if current_user.role_id != 3 and current_user.role_id != 2:  # only managers and school
        return "<h1>Access denied</h1>", 403

    # check if the event do not exist
    event = EventProject.query.get(event_id)
    if not event:
        return abort(404)

    # distinguish how a school object is gotten based on the current user role
    if current_user.role_id == 3:
        school = StaffMember.query.filter_by(
            user_id=current_user.id).first().school_institution
    else:
        school = SchoolInstitution.query.filter_by(
            email=current_user.email).first()

    return render_template('eventerx/pages/event_detail.html', current_user=current_user, page={'title': event.title.title()}, event=event, school=school)


@app.route('/settings')
@login_required
def settings():
    school = SchoolInstitution.query.filter_by(
        email=current_user.email).first()
    return render_template('eventerx/pages/settings.html', page={'title': 'settings'}, school=school)


@app.route('/event/<string:event_id>/tasks', methods=["GET", "POST"])
@login_required
def tasks(event_id):
    if current_user.role.id != 3:  # only managers
        return "<h1>Access denied</h1>", 403

    # staff = StaffMember.query.filter_by(user_id=current_user.id).first()
    school = SchoolInstitution.query.filter_by(
        email=current_user.email).first()
    event = EventProject.query.get(event_id)

    if not event:
        return abort(404)

    form = CreateCommissionForm(request.form)
    form.priority.choices = ((1, "Low"), (2, "Medium"),
                             (3, "High"))  # set priority options
    form.state.choices = [(i.id, i.name)
                          for i in CommissionStates.query.all()]  # set states options

    if request.method == "POST" and form.validate():
        commision = Commission(title=form.title.data, description=form.description.data, start_date=form.start_date.data,
                               due_date=form.due_date.data, priority=form.priority.data, event_project_id=event_id, state_id=form.state.data)

        db.session.add(commision)

        try:
            db.session.commit()
        except:
            # flash("Commission added successfully", "danger")
            db.session.rollback()
            raise
        else:
            flash("Commission added successfully")

    else:
        print(form.errors)

    commissions = event.commissions

    return render_template('eventerx/pages/tasks.html', current_user=current_user, page={'title': 'tasks'}, commissions=commissions, school=school, form=form)


@app.route('/staff')
@login_required
def staff():
    # refuse access to this page to non-school and manager users
    if current_user.role.id != 2 and current_user.role.id != 3:
        return "<h1>Access denied</h1>", 403

    if current_user.role.id == 2:  # if it is the school
        school_id = SchoolInstitution.query.filter_by(
            email=current_user.email).first().id

    else:  # if it the  manager
        school_id = StaffMember.query.filter_by(
            user_id=current_user.id).first().school_institution_id

    # getting the staff members for the current user's school
    staff = StaffMember.query.filter_by(school_institution_id=school_id).all()

    # get the invitation key to use for adding staff members
    invitation_code = InvitationCode.query.filter_by(
        purpose="staff", school_institution_id=school_id).first()
    if invitation_code:
        invitation_code = invitation_code.code
        invitation_url = url_for(
            'invitation', purpose="staff", code=invitation_code, _external=True)
    else:
        invitation_url = None

    school = SchoolInstitution.query.filter_by(
        email=current_user.email).first()

    return render_template('eventerx/pages/staff.html', current_user=current_user, page={'title': 'staff'}, staff_members=staff, invitation_url=invitation_url, school=school)


@app.route('/invite/<string:purpose>/<string:code>')
def invitation(purpose, code):
    code = check_invitation_code(code)
    if code:

        if purpose.lower() == "staff":
            page_template = "add_staff"
            form = RegisterStaffForm(request.form)
            form.school_id = code.school_institution_id

        elif purpose.lower() == "students":
            page_template = "add_student"
            form = StudentRegistrationForm(request.form)
            form.school_id = code.school_institution_id

        elif purpose.lower() == "attendee":
            page_template = "add_attendee"
            form = RegisterStaffForm(request.form)

        else:
            return abort(404)

    else:
        print("invalid code")
        return abort(404)

    return render_template(f"eventerx/pages/{page_template}.html", page={'title': page_template.replace('_', " ").title()}, form=form)


@app.route('/add/staff', methods=['GET', 'POST'])
def add_staff():
    form = RegisterStaffForm(request.form)

    # make sure there is an existing invitation link for the staff for the pretended school
    school_id = form.school_id.data
    inv_code = InvitationCode.query.filter_by(purpose="staff", school_institution_id=school_id).first()
    if inv_code:
        form_view = url_for('invitation', purpose="staff", code=inv_code.code)
    else:
        return abort(404)

    if User.query.filter_by(email=form.email.data).count() > 0:
        flash("Email already registered by a user", "danger")
        return redirect(form_view)

    if request.method == "POST" and form.validate():
        password = bcrypt.generate_password_hash(
            form.password.data).decode("utf-8")
        user = User(email=form.email.data, first_name=form.first_name.data,
                    last_name=form.last_name.data, password=password, role_id=6)
        db.session.add(user)
        try:
            db.session.flush()
            user_id = user.id
            staff = StaffMember(matricule=form.matricule.data, phone=form.phone_number.data,
                                user_id=user_id, school_institution_id=form.school_id.data)

            db.session.add(staff)
            db.session.commit()

        except:
            raise

        else:
            return redirect(url_for('login'))

    return redirect(form_view)


@app.route('/staff/<string:staff_id>')
@login_required
def staff_member_details(staff_id):
    if current_user.role.id != 3 and current_user.role.id != 2:
        return "<h1>Access denied</h1>", 403

    staff = StaffMember.query.get(staff_id)

    if not staff:
        return abort(404)

    staff_user = staff.user
    school = SchoolInstitution.query.filter_by(
        email=current_user.email).first()

    return render_template('eventerx/pages/staff_detail.html', page={'title': staff_user.fullname}, staff=staff, staff_user=staff_user, school=school)


@app.route('/make_manager/<string:staff_id>')
@login_required
def make_staff_manager(staff_id):
    # only school has the right to make staff member a manager
    if current_user.role.id != 2:
        return abort(404)

    staff = StaffMember.query.get(staff_id)

    # if the matricule passed matches no account
    if not staff:
        return abort(404)

    staff_user = User.query.get(staff.user_id)

    # if the staff member is already a mangger
    if staff_user.role.id == 3:
        return redirect(url_for('staff_member_details', staff_id=staff.matricule))

    staff_user.role_id = 3
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise
    else:
        return redirect(url_for('staff_member_details', staff_id=staff.matricule))


@app.route('/students')
@login_required
def students():
    if current_user.role.id != 3 and current_user.role.id != 2:  # only for managers and school
        return "<h1>Access denied</h1>", 403

     # if it is a manager, get the school id via the StaffMember class
    if current_user.role.id == 3:
        school_id = StaffMember.query.filter_by(
            user_id=current_user.id).first().school_institution_id

    # if it is the school itself, get the id through the SchoolInstitution class using email
    else:
        school_id = SchoolInstitution.query.filter_by(
            email=current_user.email).first().id
        
    # getting the student for the current user's school
        
    student = Student.query.filter_by(school_institution_id=school_id).all()
    

    invitation_code = InvitationCode.query.filter_by(
        purpose="students", school_institution_id=school_id).first()
    if invitation_code:
        invitation_code = invitation_code.code
        invitation_url = url_for(
            'invitation', purpose="students", code=invitation_code, _external=True)
    else:
        invitation_url = None

    return render_template("eventerx/pages/students.html", page={"title": "students"}, students=student, invitation_url=invitation_url)


@app.route('/add/student', methods=['POST'])
def add_student():
    form = StudentRegistrationForm(request.form)

    # make sure there is an existing invit  ation link for the students for the pretended school
    school_id = form.school_id.data
    inv_code = InvitationCode.query.filter_by(purpose="students", school_institution_id=school_id).first()
    if inv_code:
        form_view = url_for('invitation', purpose="students", code=inv_code.code)
    else:
        return abort(404)

    # check if there is already an account with the email and matricult
    if User.query.filter_by(email=form.email.data).count() > 0 or Student.query.get(form.matricule.data or ''):
        flash("Email and/or Matricule already registered by a student", "danger")
        return redirect(form_view)

    if request.method == "POST" and form.validate():
        password = bcrypt.generate_password_hash(
            form.password.data).decode("utf-8")
        user = User(email=form.email.data, first_name=form.first_name.data,
                    last_name=form.last_name.data, password=password, role_id=4)

        db.session.add(user)
        db.session.flush()

        if user.id:
            student = Student(matricule=form.matricule.data, phone=form.phone_number.data, speciality = form.speciality.data,
                              student_class=form.student_class.data, user_id=user.id, school_institution_id=form.school_id.data)
            db.session.add(student)

            try:
                db.session.commit()
            except:
                flash("Registration failed. Internal error", "danger")
                db.session.rollback()
            else:
                flash("Registration completed", "success")
                return redirect(url_for('login'))

        else:
            db.session.rollback()
            flash("Something went wrong. Registration failed!", "danger")

    return redirect(form_view)  # back to the source


@app.route('/teams', methods=['GET', 'POST'])
@login_required
def teams():
    if current_user.role.id != 3:  # only for managers
        return "<h1>Access denied</h1>", 403

    school = StaffMember.query.filter_by(
        user_id=current_user.id).first().school_institution_id
    # get a list of members which are not in a team,and is not a manager
    members = StaffMember.query.filter_by(team_id=None).all()
    members = [i for i in members if i.user.role_id != 3]

    commissions = Commission.query.filter_by(team_id=None).all()

    form = CreateTeamForm(request.form)
    form.members.choices = [(m.matricule, m.user.fullname) for m in members]
    form.commissions.choices = [(str(c.id), c.title) for c in commissions]

    if request.method == "POST" and form.validate():
        error_free = True
        team = Team(school_institution_id=school, title=form.title.data)
        db.session.add(team)
        db.session.flush()

        # update the team id of selected members
        for member_id in form.members.data:
            member = StaffMember.query.get(member_id)
            if member:
                member.team_id = team.id
            else:
                flash(
                    "Sorry, we can only add staff if they exist. Operation cancelled. Try again", "danger")
                db.session.rollback()
                error_free = False
                break

        # update the commission team id of selected commissions
        if error_free:
            for commission_id in form.commissions.data:
                if commission_id.isdigit():
                    commission = Commission.query.get(int(commission_id))
                    if commission:
                        commission.team_id = team.id
                    else:
                        flash(
                            "Attempt to assign an invalid commission. Operation cancelled. Try again!", "danger")
                        db.session.rollback()
                        break

            try:
                db.session.commit()
            except:
                flash("Operration failed. Team was not created. Try again", "danger")
                raise
            else:
                flash(
                    f"Team \"{form.title.data}\" was created successfully!", "success")

        else:
            pass

    else:
        print(form.errors)

    teams = Team.query.filter_by(school_institution_id=school).all()

    return render_template('eventerx/pages/teams.html', current_user=current_user, page={'title': 'teams'}, teams=teams, form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('homepage'))

    form = LoginForm(request.form)
    if form.validate and request.method == "POST":
        email1 = form.email.data
        user = User.query.filter_by(email=email1).first()
        if user:
            if not bcrypt.check_password_hash(user.password, form.password.data):
                flash("Invalid password", "error")
            else:
                login_user(user)
                return redirect(url_for('homepage'))
        else:
            flash("Invalid login credentials", "error")

    return render_template("eventerx/pages/login.html", page={'title': "login"}, form=form)


@app.route("/register/school", methods=['GET', 'POST'])
def register_school():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))

    form = RegisterSchoolForm(request.form)
    if request.method == "POST" and form.validate():

        if User.query.filter_by(email=form.email_address.data).count() > 0:
            flash("Email already in used!", category="danger")
        elif SchoolInstitution.query.filter_by(name=form.name.data).first():
            flash("School already exists! Pleas try a different school name", category="danger")

        else:
            password = bcrypt.generate_password_hash(
                form.password.data).decode('utf-8')
            school_user = User(email=form.email_address.data,
                            password=password, role_id=2)
            db.session.add(school_user)

            school = SchoolInstitution(email=form.email_address.data, name=form.name.data, address1=form.address1.data,
                                    address2=form.address2.data, phone=form.phone_number.data, pobox=form.pobox.data, website=form.website.data)
            db.session.add(school)

            try:
                db.session.commit()

            except:
                db.session.rollback()
                raise

            else:
                return redirect(url_for('login'))

    else:
        print(form.errors)

    return render_template("eventerx/pages/register_school.html", page={'title': "register school"}, form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

#generating link
@app.route('/gen_link/<string:purpose>')
@login_required
def generate_link(purpose):
    if current_user.role.id != 3 and current_user.role.id != 2:  # only managers and school admins
        return "<h1>Access denied</h1>", 403

    # if it is a manager, get the school id via the StaffMember class
    if current_user.role.id == 3:
        school_id = StaffMember.query.filter_by(
            user_id=current_user.id).first().school_institution_id

    # if it is the school itself, get the id through the SchoolInstitution class using email
    else:
        school_id = SchoolInstitution.query.filter_by(
            email=current_user.email).first().id

    purpose = purpose.lower()
    url_code = token_hex(8)
    duration = datetime.now() + timedelta(days=31)  # make validity only for 7 days

    check = InvitationCode.query.filter_by(
        purpose=purpose, school_institution_id=school_id).count() < 1
    if check:
        db.session.add(InvitationCode(
            code=url_code, duration=int(duration.timestamp()), purpose=purpose, school_institution_id=school_id))

    try:
        db.session.commit()
    except:
        db.session.rollabck()
        raise
    else:
        return redirect(url_for(purpose))
    
    #delete staff member
@app.route('/staff/delete/<string:id>')
@login_required
def delete_staff_member(id):
    if current_user.role.id != 3 and current_user.role.id != 2:
        return "<h1>Access denied</h1>", 403
    #if current_user.role.id == 3:
            #return "<h1>Access denied</h1>", 403
    #else:

    staff_user = User.query.get_or_404(id)
    db.session.delete(staff_user)
    db.session.commit()
    return redirect(url_for('staff', current_user=current_user))

 #delete student
@app.route('/students/delete/<string:id>')
@login_required
def delete_student(id):
    if current_user.role.id != 3 and current_user.role.id != 2:
        return "<h1>Access denied</h1>", 403
    #if current_user.role.id == 3:
            #return "<h1>Access denied</h1>", 403
    #else:

    student_user = User.query.get_or_404(id)
    db.session.delete(student_user)
    db.session.commit()
    return redirect(url_for('students', current_user=current_user))
   
   #delete Event
@app.route('/events/delete/<string:id>')
@login_required
def delete_events(id):
     if current_user.role.id != 3 and current_user.role.id != 2:
        return "<h1>Access denied</h1>", 403
     event = EventProject.query.get_or_404(id)
     db.session.delete(event)
     db.session.commit()
     return redirect(url_for('events', current_user=current_user))
 
    #delete team
@app.route('/teams/delete/<string:id>')
@login_required
def delete_team(id):
     if current_user.role.id != 3 and current_user.role.id != 2:
        return "<h1>Access denied</h1>", 403
     team = Team.query.get_or_404(id)
     db.session.delete(team)
     db.session.commit()
     return redirect(url_for('teams', current_user=current_user))
 
 
@app.route('/event/edite/<string:event_id>', methods=['GET', 'POST'])
@login_required
def edite_events(event_id):
    if current_user.role.id != 3:  # only managers
        return "<h1>Access denied</h1>", 403
    
    event = EventProject.query.get(event_id)

    if not event:
        return abort(404)

    form = CreateEventForm(request.form)
    if request.method == "POST" and form.validate():
        db.session.delete(event)
        db.session.commit()
        school_id = StaffMember.query.filter_by(
            user_id=current_user.id).first().school_institution_id
        event = EventProject(title=form.title.data, venue=form.venue.data, description=form.description.data,
                              start_date=form.start_date.data, due_date=form.due_date.data, budget=form.budget.data, school_institution_id=school_id)
        db.session.add(event)
        db.session.commit()
        return redirect(url_for('events', event_id = event.id))


    form.title.data = event.title
    form.venue.data = event.venue
    form.description.data = event.description
    form.start_date.data = event.start_date
    form.due_date.data = event.due_date
    form.budget.data = event.budget
        
    school = SchoolInstitution.query.filter_by(
    email=current_user.email).first()

    return render_template('eventerx/pages/edite_event.html', current_user=current_user, page={'title': 'events'}, school=school, form=form)
    # return redirect(url_for('add_event.html', current_user=current_user, page={'title': 'events'}, events=events, school=school, form=form, id=event.id))
 