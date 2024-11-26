from flask import Blueprint, g, jsonify, render_template, request
from flask_login import current_user, login_required

from app.models import Usuario, Vehiculo

from app import db
from app.routes import propietario_admin_permission, usuario_rol
from app.routes import todos_permiso


class ClienteVehiculoRoutes:
    def __init__(self):
        self.blueprint = Blueprint('cliente_vehiculo', __name__)
        self.add_routes()

    def add_routes(self):
        pass
