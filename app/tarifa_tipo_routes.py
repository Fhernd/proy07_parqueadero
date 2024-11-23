from flask import Blueprint, g, jsonify, render_template, request
from flask_login import login_required

from app.models import TarifaTipo

from app import db
from app.routes import propietario_admin_permission
from app.routes import todos_permiso


class TarifaTipoRoutes:
    """
    Clase que gestiona las rutas de los tipos de tarifa.
    """
    def __init__(self):
        """
        Constructor de la clase.
        """
        self.blueprint = Blueprint('tarifa_tipo', __name__)
        self.add_routes()

    def add_routes(self):
        """
        Agrega las rutas de los tipos de tarifa.
        """
        @self.blueprint.route("/tarifa-tipo", methods=['GET'])
        @login_required
        @todos_permiso.require(http_exception=403)
        def tarifa_tipo():
            """
            Muestra la lista de tipos de tarifa.
            """
            g.template_name = 'base.html'
            
            entidades = TarifaTipo.query.all()
            return render_template("tarifa-tipo.html", titulo='Tipo de Tarifa', entidades=entidades)
    