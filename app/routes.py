from flask import render_template

from app import app

from app.models import VehiculoTipo


@app.route("/")
def index():
    return render_template("index.html", titulo='Inicio', nombre='Alex')

@app.route("/vehiculo-tipo", methods=['GET'])
def vehiculo_tipo():
    tipos_vehiculo = VehiculoTipo.query.all()
    return render_template("vehiculo-tipo.html", titulo='Tipo de Vehículo', tipos_vehiculo=tipos_vehiculo)
