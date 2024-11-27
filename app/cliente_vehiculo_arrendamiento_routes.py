from flask import Blueprint, g, jsonify, render_template, request
from flask_login import current_user, login_required

from app.models import Modulo, Parqueadero, Parqueo, Sede, SedeUsuario, Usuario

from app import db
from app.routes import propietario_admin_permission, usuario_rol
from app.routes import todos_permiso


class ClienteVehiculoArrendamientoRoutes:
    """
    Clase que gestiona las rutas de los vehículos de los clientes.
    """
    def __init__(self):
        """
        Constructor de la clase.
        """
        self.blueprint = Blueprint('cliente_vehiculo_arrendamiento', __name__)
        self.add_routes()

    def add_routes(self):
        pass
