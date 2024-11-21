from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required

from app.models import VehiculoTipo
from app.models import Tarifa

from app import app

from app.routes import propietario_admin_permission

from app.models import VehiculoTipo

@app.route("/vehiculo-tipo", methods=['GET'])
@login_required
@propietario_admin_permission.require(http_exception=403)
def vehiculo_tipo():
    """
    Muestra la lista de tipos de vehículo.
    """
    g.template_name = 'base.html'
    
    tipos_vehiculo = VehiculoTipo.query.all()
    tarifas = Tarifa.query.all()
    return render_template("vehiculo-tipo.html", titulo='Tipo de Vehículo', tipos_vehiculo=tipos_vehiculo, tarifas=tarifas)