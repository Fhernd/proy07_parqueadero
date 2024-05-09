from flask import jsonify, render_template, request

from app import app, db

from app.models import MedioPago, TarifaTipo, VehiculoTipo


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

        return jsonify({'status': 'success', 'message': 'Tipo de vehículo creado', 'data': {
            'id': vehiculo_tipo.id,
            'nombre': vehiculo_tipo.nombre
        }}), 201

    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/vehiculo-tipo/<int:id>', methods=['PUT'])
def vehiculo_tipo_update(id):
    """
    Actualiza un tipo de vehículo.

    :param id: Identificador del tipo de vehículo.
    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()
        vehiculo_tipo = VehiculoTipo.query.get(id)

        if vehiculo_tipo is None:
            return jsonify({'status': 'failure', 'message': 'Tipo de vehículo encontrado'}), 404

        vehiculo_tipo.nombre = data.get('nombre')
        vehiculo_tipo.updated_at = db.func.current_timestamp()

        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Tipo de vehículo actualizado', 'data': {
            'id': vehiculo_tipo.id,
            'nombre': vehiculo_tipo.nombre
        }}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route("/tarifa-tipo", methods=['GET'])
def tarifa_tipo():
    """
    Muestra la lista de tipos de tarifa.
    """
    entidades = TarifaTipo.query.all()
    return render_template("tarifa-tipo.html", titulo='Tipo de Tarifa', entidades=entidades)


@app.route('/tarifa-tipo', methods=['POST'])
def tarifa_tipo_create():
    """
    Crea un nuevo tipo de tarifa.

    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()
        entidad = TarifaTipo(nombre=data.get('nombre'), unidad=data.get('unidad'))

        db.session.add(entidad)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Tipo de tarifa creado', 'data': {
            'id': entidad.id,
            'nombre': entidad.nombre,
            'unidad': entidad.unidad
        }}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/tarifa-tipo/<int:id>', methods=['PUT'])
def tarifa_tipo_update(id):
    """
    Actualiza un tipo de tarifa.

    :param id: Identificador del tipo de tarifa.
    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()
        entidad = TarifaTipo.query.get(id)

        if entidad is None:
            return jsonify({'status': 'failure', 'message': 'Tipo de tarifa encontrado'}), 404

        entidad.nombre = data.get('nombre')
        entidad.unidad = data.get('unidad')
        entidad.updated_at = db.func.current_timestamp()

        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Tipo de tarifa actualizado', 'data': {
            'id': entidad.id,
            'nombre': entidad.nombre,
            'unidad': entidad.unidad
        }}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/tarifa-tipo/<int:id>', methods=['DELETE'])
def tarifa_tipo_delete(id):
    """
    Elimina un tipo de tarifa.

    :param id: Identificador del tipo de tarifa.
    :return: Respuesta JSON.
    """
    try:
        entidad = TarifaTipo.query.get(id)

        if entidad is None:
            return jsonify({'status': 'failure', 'message': 'Tipo de tarifa encontrado'}), 404

        db.session.delete(entidad)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Tipo de tarifa eliminado'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route("/medio-pago", methods=['GET'])
def medio_pago():
    """
    Muestra la lista de tipos de tarifa.
    """
    entidades = MedioPago.query.all()
    return render_template('medio-pago.html', titulo='Medios de Pago', entidades=entidades)


@app.route('/medio-pago', methods=['POST'])
def medio_pago_create():
    """
    Crea un nuevo medio de pago.

    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()
        entidad = MedioPago(nombre=data.get('nombre'))

        db.session.add(entidad)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Medio de pago creado', 'data': {
            'id': entidad.id,
            'nombre': entidad.nombre
        }}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/medio-pago/<int:id>', methods=['PUT'])
def medio_pago_update(id):
    """
    Actualiza un medio de pago.

    :param id: Identificador del medio de pago.
    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()
        entidad = MedioPago.query.get(id)

        if entidad is None:
            return jsonify({'status': 'failure', 'message': 'Medio de pago encontrado'}), 404

        entidad.nombre = data.get('nombre')
        entidad.updated_at = db.func.current_timestamp()

        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Medio de pago actualizado', 'data': {
            'id': entidad.id,
            'nombre': entidad.nombre
        }}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500