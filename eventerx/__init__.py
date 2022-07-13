from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from flask_migrate import Migrate

from eventerx.config import DevConfig, ProdConfig


app = Flask(__name__)
ENV = "dev"

app.config.from_object(DevConfig() if ENV == 'dev' else ProdConfig())

db = SQLAlchemy(app)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)
# csrf = CSRFProtect(app)
migrate = Migrate(app, db)

login_manager.login_view = "login"
login_manager.login_message = u"You need to login to get access to that page"
login_manager.login_message_category = "warning"

ROOT_FODLER = os.path.join(os.getcwd(), "eventerx")
PROJECT_FILES_FOLDER = os.path.join(ROOT_FODLER, "files")


from eventerx.routes import *
from eventerx.models import *