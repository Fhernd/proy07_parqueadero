from flask import render_template

from app import app, db

from app.models import VehiculoTipo


@app.route("/")
def index():
    return render_template("index.html", titulo='Inicio', nombre='Alex')

@app.route("/vehiculo-tipo", methods=['GET'])
def vehiculo_tipo():
    tipos_vehiculo = VehiculoTipo.query.all()
    return render_template("vehiculo-tipo.html", titulo='Tipo de Vehículo', tipos_vehiculo=tipos_vehiculo)


@app.route('/vehiculo-tipo/<int:id>', methods=['DELETE'])
def vehiculo_tipo_delete(id):
    vehiculo_tipo = VehiculoTipo.query.get(id)
    
    if vehiculo_tipo is None:
        return {
            'status': 'failure',
            'data': None
        }, 204
    
    db.session.delete(vehiculo_tipo)
    db.session.commit()
    
    return {
        'status': 'success',
        'data': {
            'id': vehiculo_tipo.id,
            'nombre': vehiculo_tipo.nombre
        }
    }, 204
