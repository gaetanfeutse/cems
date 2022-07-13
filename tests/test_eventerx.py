from datetime import date
from eventerx.models import Commission, EventProject, InvitationCode
from client_ficture import client
from flask import request, url_for


def test_tc01(client):
    """Register a school with all valid data"""
    rv = client.post("/register/school",
                     data=dict(
                         email_address="ub@gmail.com",
                         password="password",
                         name="UB",
                         address1="Molyko",
                         address2="Buea",
                         phone_number="690000000",
                         pobox="0000",
                         website="www.ub.com",
                     ),
                     follow_redirects=True)
    assert request.path == url_for('login')


def test_tc02(client):
    """Register a school with a few missing though required data"""
    rv = client.post("/register/school",
                     data=dict(
                         email_address=None,
                         password=None,
                         name="UB",
                         address1=None,
                         address2="Buea",
                         phone_number="690000000",
                         pobox="0000",
                         website="www.ub.com",
                     ),
                     follow_redirects=True)
    assert request.path != url_for('login')


def test_tc03(client):
    """Attempt to register a school with valid form data but with an existing email address."""
    rv = client.post("/register/school",
                     data=dict(
                         email_address="ub@gmail.com",
                         password="password",
                         name="UB",
                         address1="Molyko",
                         address2="Buea",
                         phone_number="690000000",
                         pobox="0000",
                         website="www.ub.com",
                     ),
                     follow_redirects=True)
    assert request.path != url_for('login')


# ==============================
#  User Authentication
# ==============================

def test_tc11(client):
    """Login with existing and both valid credentials"""
    rv = client.post("/login",
                     data=dict(
                         email="ub@gmail.com",
                         password="password",
                     ),
                     follow_redirects=True)
    assert request.path == url_for('homepage')


def test_tc12(client):
    """Attempts to authenticate with invalid credentials"""
    rv = client.post("/login",
                     data=dict(
                         email="anymail@gmail.com",
                         password="password",
                     ),
                     follow_redirects=True)
    assert b"Invalid login credentials" in rv.data


def test_tc13(client):
    """Login with existing email credential but invalid password"""
    rv = client.post("/login",
                     data=dict(
                         email="ub@gmail.com",
                         password="wrongpassword",
                     ),
                     follow_redirects=True)
    assert b"Invalid password" in rv.data


# ==============================
#  Invitation for staff and student registration
# ==============================

def test_tc21(client):
    """Generate an invitation link for staff registration when not existing"""
    rv_login = client.post("/login", data=dict( email="ub@gmail.com", password="password"), follow_redirects=True)
    rv = client.get("/gen_link/staff", follow_redirects=True)
    assert request.path == url_for("staff")


def test_tc22(client):
    """Generate an invitation link for staff registration when there is an existing one"""
    rv_login = client.post("/login", data=dict( email="ub@gmail.com", password="password"), follow_redirects=True)
    rv = client.get("/gen_link/staff", follow_redirects=True)
    assert request.path == url_for("staff")
    

def test_tc23(client):
    """Generate an invitation link for students’ registration when not existinge"""
    rv_login = client.post("/login", data=dict( email="ub@gmail.com", password="password"), follow_redirects=True)
    rv = client.get("/gen_link/students", follow_redirects=True)
    assert request.path == url_for("students")


def test_tc24(client):
    """Generate an invitation link for students’ registration when there is an existing one"""
    rv_login = client.post("/login", data=dict( email="ub@gmail.com", password="password"), follow_redirects=True)
    rv = client.get("/gen_link/students", follow_redirects=True)
    assert request.path == url_for("students")


# ==============================
#  Student Registration
# ==============================

def test_tc41(client):
    """Register a non-existing student with valid data"""
    rv = client.post("/add/student", 
                    data=dict( 
                        first_name = "John",
                        last_name = "Doe",
                        email = "stud001@gmail.com",
                        matricule = "STUD001",
                        phone_number = "695748456",
                        password = "password",
                        speciality = "Software",
                        student_class = "3",
                        school_id = 1
                    ), follow_redirects=True )
    assert rv.status_code == 200 and request.path == url_for("login") # make sure the user has been created
    # try to authenticate the newly created user 
    rv = client.post("/login", data=dict(email="stud001@gmail.com", password="password"), follow_redirects=True)
    assert request.path == url_for("homepage")


def test_tc42(client):
    """Register an existing student with valid data"""
    inv_code = InvitationCode.query.filter_by(purpose="students", school_institution_id=1).first()
    rv = client.post("/add/student", 
                    data=dict( 
                        first_name = "John",
                        last_name = "Doe",
                        email = "stud01@gmail.com",
                        matricule = "STUD001",
                        phone_number = "695748456",
                        password = "password",
                        speciality = "Software",
                        student_class = "3",
                        school_id = 1
                    ), follow_redirects=True )
    assert request.path == url_for('invitation', purpose="students", code=inv_code.code)


def test_tc43(client):
    """Register a non-existing student with missing data."""
    inv_code = InvitationCode.query.filter_by(purpose="students", school_institution_id=1).first()
    rv = client.post("/add/student", 
                    data=dict( 
                        first_name = "Steve",
                        last_name = "Jobs",
                        phone_number = "695748456",
                        password = "password",
                        student_class = "3",
                        school_id = 1
                    ), follow_redirects=True )
    assert request.path == url_for('invitation', purpose="students", code=inv_code.code)



# ==============================
#  Staff Registration
# ==============================

def test_tc51(client):
    """Register a non-existing staff with valid data"""
    rv = client.post("/add/staff", 
                    data=dict( 
                        first_name = "Robert",
                        last_name = "Alpha",
                        email = "staff101@gmail.com",
                        matricule = "STAFF101",
                        phone_number = "695746556",
                        password = "password",
                        school_id = 1
                    ), follow_redirects=True )
    assert rv.status_code == 200 and request.path == url_for("login") # make sure the user has been created

    rv = client.post("/login", data=dict(email="staff101@gmail.com", password="password"), follow_redirects=True)
    assert request.path == url_for("homepage")

 
def test_tc52(client):
    """Register an existing staff with valid data."""
    inv_code = InvitationCode.query.filter_by(purpose="staff", school_institution_id=1).first()
    rv = client.post("/add/staff", 
                    data=dict( 
                        first_name = "Robert",
                        last_name = "Alpha",
                        email = "staff101@gmail.com",
                        matricule = "STAFF101",
                        phone_number = "695746556",
                        password = "password",
                        school_id = 1
                    ), follow_redirects=True )

    assert request.path == url_for('invitation', purpose="staff", code=inv_code.code)


def test_tc53(client):
    """Register a non-existing staff with missing data."""
    inv_code = InvitationCode.query.filter_by(purpose="staff", school_institution_id=1).first()
    rv = client.post("/add/staff", 
                    data=dict( 
                        first_name = "Pascal",
                        last_name = "Forgeur",
                        phone_number = "6589463157",
                        password = "password",
                        school_id = 1
                    ), follow_redirects=True )

    assert request.path == url_for('invitation', purpose="staff", code=inv_code.code)


# ==============================
#  Manager Role update
# ==============================

def test_tc31(client):
    """Set a valid staff as manager"""
    rv_login = client.post("/login", data=dict( email="ub@gmail.com", password="password"), follow_redirects=True)
    assert request.path == url_for('homepage')
    rv = client.get("/make_manager/STAFF101", follow_redirects=True)
    assert request.path == url_for('staff_member_details', staff_id="STAFF101")


def test_tc32(client):
    """Set a invalid staff as manager"""
    rv_login = client.post("/login", data=dict( email="ub@gmail.com", password="password"), follow_redirects=True)
    assert request.path == url_for('homepage')
    rv = client.get("/make_manager/STAFF190", follow_redirects=True)
    assert rv.status_code == 404 


def test_tc33(client):
    """Try to set a valid staff already a manager as manager"""
    rv_login = client.post("/login", data=dict( email="ub@gmail.com", password="password"), follow_redirects=True)
    assert request.path == url_for('homepage')
    rv = client.get("/make_manager/STAFF101", follow_redirects=True)
    assert request.path == url_for('staff_member_details', staff_id="STAFF101")



# ==============================
#  Event creation
# ==============================

def test_tc61(client):
    """Create event with valid data"""
    rv_login = client.post("/login", data=dict( email="staff101@gmail.com", password="password"), follow_redirects=True)
    assert request.path == url_for('homepage')

    rv = client.post("/add/event", data=dict(
                        title =  "Event Title 1",
                        venue = "Some place 1",
                        description =  "A description",
                        budget =  584000,
                        start_date =  date(2021, 9, 19),
                        due_date =  date(2021, 9, 21)
                    ), follow_redirects=True)

    assert request.path == url_for('events') and EventProject.query.count() == 1 # there should only be one project


def test_tc62(client):
    """Create event with missing data"""
    rv_login = client.post("/login", data=dict( email="staff101@gmail.com", password="password"), follow_redirects=True)
    assert request.path == url_for('homepage')

    rv = client.post("/add/event", data=dict(
                        venue = "Some place 2",
                        budget =  584000,
                        start_date =  date(2021, 9, 19),
                    ), follow_redirects=True)

    assert request.path == url_for('add_event') and EventProject.query.count() == 1 # there should only be one project



# ==============================
#  Commission Creation
# ==============================

def test_tc71(client):
    """Create a commission with valid data for an existing event"""
    rv_login = client.post("/login", data=dict( email="staff101@gmail.com", password="password"), follow_redirects=True)
    assert request.path == url_for('homepage')

    rv = client.post("/event/1/tasks", data=dict(
                        title =  "Simple Commission 1",
                        description =  "Description 1",
                        start_date =  date(2021, 9, 19),
                        due_date =  date(2021, 9, 21),
                        priority =  1,
                        state =  1
                    ), follow_redirects=True)

    assert request.path == url_for('tasks', event_id=1) and Commission.query.count() == 1 # there should only be one project


def test_tc72(client):
    """Create a commission with valid data for a non-existing event."""
    rv_login = client.post("/login", data=dict( email="staff101@gmail.com", password="password"), follow_redirects=True)
    assert request.path == url_for('homepage')

    rv = client.post("/event/5/tasks", data=dict(
                        title =  "Simple Commission 2",
                        description =  "Description 2",
                        start_date =  date(2021, 9, 19),
                        due_date =  date(2021, 9, 21),
                        priority =  3,
                        state =  2
                    ), follow_redirects=True)

    assert rv.status_code == 404 and Commission.query.count() == 1 # there should only be one project


def test_tc73(client):
    """Create a commission with invalid data for an existing event."""
    rv_login = client.post("/login", data=dict( email="staff101@gmail.com", password="password"), follow_redirects=True)
    assert request.path == url_for('homepage')

    rv = client.post("/event/1/tasks", data=dict(
                        description =  "Description 2",
                        start_date =  date(2021, 9, 19),
                        priority =  2,
                        state =  3
                    ), follow_redirects=True)

    assert request.path == url_for('tasks', event_id=1) and Commission.query.count() == 1 # there should only be one project
