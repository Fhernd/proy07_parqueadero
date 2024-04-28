from flask import render_template

from app import app


@app.route("/")
def index():
    return render_template("index.html", titulo='Inicio', nombre='Alex')

@app.route("/vehiculo-tipo", methods=['GET'])
def vehiculo_tipo():
    return render_template("vehiculo-tipo.html", titulo='Tipo de Vehículo')
