from flask import Blueprint, g, jsonify, render_template, request
from flask_login import login_required

from app.models import MedioPago

from app import db
from app.routes import propietario_admin_permission
from app.routes import todos_permiso


class AuthRoutes:
    """
    Clase que gestiona las rutas de autenticación.
    """
    def __init__(self):
        """
        Constructor de la clase.
        """
        self.blueprint = Blueprint('auth', __name__)
        self.add_routes()

    def add_routes(self):
        pass
