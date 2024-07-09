from flask import Flask
from flask_login import LoginManager, current_user
from flask_principal import Principal
from flask_sqlalchemy import SQLAlchemy

from config import ConfigDevelopment

app = Flask(__name__)
app.config.from_object(ConfigDevelopment)

db = SQLAlchemy(app)

login = LoginManager(app)
login.login_view = 'login'
principal = Principal(app)


from app import models

from app import routes
