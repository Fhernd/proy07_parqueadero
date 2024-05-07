from flask import jsonify, render_template, request

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
    try:
        vehiculo_tipo = VehiculoTipo.query.get(id)

        if vehiculo_tipo is None:
            return jsonify({'status': 'failure', 'message': 'Tipo de vehículo encontrado'}), 404

        db.session.delete(vehiculo_tipo)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Tipo de vehículo eliminado'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/vehiculo-tipo', methods=['POST'])
def vehiculo_tipo_create():
    try:
        data = request.get_json()
        vehiculo_tipo = VehiculoTipo(nombre=data.get('nombre'))

        db.session.add(vehiculo_tipo)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Tipo de vehículo creado'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
