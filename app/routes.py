from datetime import datetime, timedelta
import io
import os
import tempfile

from flask import current_app, flash, g, jsonify, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_user, logout_user, login_required
from flask_principal import Permission, RoleNeed, UserNeed, identity_loaded, identity_changed, Identity, AnonymousIdentity
from werkzeug.security import generate_password_hash
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
import qrcode

from app import app, db

from app.forms import CambiarClaveForm, ParqueaderoInformacionForm, UsuarioForm
from app.models import Arrendamiento, Cliente, MedioPago, Modulo, Pais, Parqueadero, Parqueo, Periodicidad, Rol, Sede, SedeUsuario, Tarifa, TarifaTipo, Usuario, Vehiculo, VehiculoTipo, usuario_rol
from app.util.roles_enum import Roles
from app.util.utilitarios import to_json

propietario_role = RoleNeed(Roles.PROPIETARIO.value)
admin_role = RoleNeed(Roles.ADMINISTRADOR.value)
operario_role = RoleNeed(Roles.OPERARIO.value)

admin_permission = Permission(admin_role)
propietario_permission = Permission(propietario_role)
operario_permission = Permission(operario_role)
propietario_admin_permission = propietario_permission.union(admin_permission)
todos_permiso = propietario_permission.union(admin_permission).union(operario_permission)


def tiene_rol(roles_disponibles, roles_asignados):
    """
    Verifica si un usuario tiene un rol específico.

    :param roles_disponibles: Roles disponibles.
    :param roles_asignados: Roles asignados.
    :return: Booleano.
    """
    roles_disponibles = [rol.nombre for rol in roles_disponibles]
    return set(roles_asignados).intersection(roles_disponibles)


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    identity.user = current_user

    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.nombre))


@app.context_processor
def inject_permissions():
    # Inyecta los permisos solo si base.html es la plantilla base
    if 'base.html' in g.get('template_name', ''):
        return dict(
            admin_permission=admin_permission,
            propietario_permission=propietario_permission,
            propietario_admin_permission=propietario_admin_permission,
            operario_permission=operario_permission
        )
    return {}


@app.route("/")
def index():
    """
    Muestra la página de inicio de la aplicación.

    :return: Plantilla HTML.
    """
    return render_template("login.html", titulo='Inicio', nombre='Alex')


@app.route('/dashboard', methods=['GET'])
@login_required
@propietario_admin_permission.require(http_exception=403)
def dashboard():
    """
    Muestra el dashboard de la aplicación.

    :return: Plantilla HTML.
    """
    g.template_name = 'base.html'
    return render_template('dashboard.html', titulo='Dashboard')


from app.auth_routes import AuthRoutes
from app.cliente_vehiculo_routes import ClienteVehiculoRoutes
from app.cliente_vehiculo_arrendamiento_routes import ClienteVehiculoArrendamientoRoutes
from app.vehiculo_tipo_routes import VehiculoTipoRoutes
from app.tarifa_tipo_routes import TarifaTipoRoutes
from app.medio_pago_routes import MedioPagoRoutes
from app.cliente_routes import ClienteRoutes
from app.parqueadero_routes import ParqueaderoRoutes
from app.sede_routes import SedeRoutes
from app.usuario_routes import UsuarioRoutes

app.register_blueprint(AuthRoutes().blueprint)
app.register_blueprint(ClienteRoutes().blueprint)
app.register_blueprint(ClienteVehiculoRoutes().blueprint)
app.register_blueprint(ClienteVehiculoArrendamientoRoutes().blueprint)
app.register_blueprint(MedioPagoRoutes().blueprint)
app.register_blueprint(ParqueaderoRoutes().blueprint)
app.register_blueprint(SedeRoutes().blueprint)
app.register_blueprint(TarifaTipoRoutes().blueprint)
app.register_blueprint(UsuarioRoutes().blueprint)
app.register_blueprint(VehiculoTipoRoutes().blueprint)
