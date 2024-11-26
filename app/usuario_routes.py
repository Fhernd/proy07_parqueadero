from flask import Blueprint, g, jsonify, render_template, request
from flask_login import login_required

from app.models import Usuario

from app import db
from app.routes import propietario_admin_permission
from app.routes import todos_permiso


class UsuarioRoutes:
    """
    Clase que gestiona las rutas de los usuarios.
    """
    def __init__(self):
        """
        Constructor de la clase.
        """
        self.blueprint = Blueprint('usuario', __name__)
        self.add_routes()

    def add_routes(self):
        pass
