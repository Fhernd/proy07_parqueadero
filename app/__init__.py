from flask import Flask
from flask_login import LoginManager
from flask_principal import Principal, Permission, RoleNeed, Identity, AnonymousIdentity, identity_loaded, identity_changed
from flask_sqlalchemy import SQLAlchemy

from config import ConfigDevelopment

app = Flask(__name__)
app.config.from_object(ConfigDevelopment)

db = SQLAlchemy(app)

login = LoginManager(app)
login.login_view = 'login'

principal = Principal(app)

# Definir necesidades de rol
admin_role = RoleNeed('admin')
propietario_role = RoleNeed('propietario')

# Crear permisos basados en roles
admin_permission = Permission(admin_role)
propietario_permission = Permission(propietario_role)

from app import models

from app import routes
