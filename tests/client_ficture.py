
import pytest
from eventerx import app, db
from eventerx.utils import db_get_started
from secrets import token_hex
import pytest


db_name = token_hex()
initialized = False

@pytest.fixture
def client():
    global initialized
    # app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:////eventerx_test_dbs/{db_name}.db"
    app.config['SQLALCHEMY_DATABASE_URI']  = "mysql://root:GAEtan1234?@localhost:3306/cems_test"
    # app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///cems_test.db"
    with app.test_client() as client:
        with app.app_context():
            if not initialized:
                db.create_all()
                db_get_started()
                initialized = True
        yield client