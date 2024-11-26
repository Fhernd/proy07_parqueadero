from flask import Blueprint, g, jsonify, render_template, request
from flask_login import current_user, login_required

from app.models import Modulo, Sede

from app import db
from app.routes import propietario_admin_permission, usuario_rol
from app.routes import todos_permiso


class SedeRoutes:
    """
    Clase que gestiona las rutas de las sedes.
    """
    def __init__(self):
        """
        Constructor de la clase.
        """
        self.blueprint = Blueprint('sede', __name__)
        self.add_routes()

    def add_routes(self):
        pass
