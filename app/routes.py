from flask import jsonify, render_template, request
from werkzeug.security import generate_password_hash

from app import app, db

from app.models import Cliente, MedioPago, Rol, TarifaTipo, Usuario, VehiculoTipo


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
def vehiculo_tipo_crear():
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


@app.route('/medio-pago/<int:id>', methods=['DELETE'])
def medio_pago_delete(id):
    """
    Elimina un medio de pago.

    :param id: Identificador del medio de pago.
    :return: Respuesta JSON.
    """
    try:
        entidad = MedioPago.query.get(id)

        if entidad is None:
            return jsonify({'status': 'failure', 'message': 'Medio de pago encontrado'}), 404

        db.session.delete(entidad)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Medio de pago eliminado'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route("/cliente", methods=['GET'])
def cliente():
    """
    Muestra la lista de tipos de tarifa.
    """
    entidades = Cliente.query.all()
    return render_template('cliente.html', titulo='Clientes', entidades=entidades)


@app.route('/cliente', methods=['POST'])
def cliente_crear():
    """
    Crea un nuevo cliente.

    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()
        entidad = Cliente(documento=data.get('documento'), nombres=data.get('nombres'), apellidos=data.get('apellidos'), telefono=data.get('telefono'), email=data.get('email'), direccion=data.get('direccion'), parqueadero_id=data.get('parqueadero_id'))

        db.session.add(entidad)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Cliente creado', 'data': {
            'id': entidad.id,
            'documento': entidad.documento,
            'nombres': entidad.nombres,
            'apellidos': entidad.apellidos,
            'telefono': entidad.telefono,
            'email': entidad.email,
            'direccion': entidad.direccion,
            'parqueadero_id': entidad.parqueadero_id
        }}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/cliente/<string:documento>', methods=['PUT'])
def cliente_actualizar(documento):
    """
    Actualiza un cliente.

    :param id: Identificador del cliente.
    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()
        entidad = Cliente.query.filter_by(documento=documento).first()

        if entidad is None:
            return jsonify({'status': 'failure', 'message': 'Cliente encontrado'}), 404

        entidad.documento = data.get('documento')
        entidad.nombres = data.get('nombres')
        entidad.apellidos = data.get('apellidos')
        entidad.telefono = data.get('telefono')
        entidad.email = data.get('email')
        entidad.direccion = data.get('direccion')
        entidad.parqueadero_id = data.get('parqueadero_id')
        entidad.updated_at = db.func.current_timestamp()

        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Cliente actualizado', 'data': {
            'id': entidad.id,
            'documento': entidad.documento,
            'nombres': entidad.nombres,
            'apellidos': entidad.apellidos,
            'telefono': entidad.telefono,
            'email': entidad.email,
            'direccion': entidad.direccion,
            'parqueadero_id': entidad.parqueadero_id
        }}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/cliente/<string:documento>', methods=['DELETE'])
def cliente_eliminar(documento):
    """
    Elimina un cliente.

    :param id: Identificador del cliente.
    :return: Respuesta JSON.
    """
    try:
        entidad = Cliente.query.filter_by(documento=documento).first()

        if entidad is None:
            return jsonify({'status': 'failure', 'message': 'Cliente encontrado'}), 404

        db.session.delete(entidad)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Cliente eliminado'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route("/rol", methods=['GET'])
def rol():
    """
    Muestra la lista de roles.
    """
    entidades = Rol.query.all()
    return render_template('rol.html', titulo='Roles', entidades=entidades)


@app.route("/usuario", methods=['GET'])
def usuario():
    """
    Muestra la lista de usuarios.
    """
    entidades = Usuario.query.all()
    roles = Rol.query.all()
    return render_template('usuario.html', titulo='Usuarios', entidades=entidades, roles=roles)


@app.route('/usuario', methods=['POST'])
def usuario_crear():
    """
    Crea un nuevo usuario.

    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()

        hashed_password = generate_password_hash(data.get('password'), method='pbkdf2:sha256')

        entidad = Usuario(
            documento=data.get('documento'),
            nombres=data.get('nombres'),
            apellidos=data.get('apellidos'),
            telefono=data.get('telefono'),
            email=data.get('email'),
            rol_id=data.get('rolId'),
            password=hashed_password
        )

        db.session.add(entidad)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Usuario creado', 'data': {
            'id': entidad.id,
            'documento': entidad.documento,
            'nombres': entidad.nombres,
            'apellidos': entidad.apellidos,
            'telefono': entidad.telefono,
            'email': entidad.email,
            'rol_id': entidad.rol_id
        }}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/usuario/<string:documento>', methods=['PUT'])
def usuario_actualizar(documento):
    """
    Actualiza un usuario.

    :param id: Identificador del usuario.
    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()
        entidad = Usuario.query.filter_by(documento=documento).first()

        if entidad is None:
            return jsonify({'status': 'failure', 'message': 'Usuario encontrado'}), 404

        entidad.documento = data.get('documento')
        entidad.nombres = data.get('nombres')
        entidad.apellidos = data.get('apellidos')
        entidad.telefono = data.get('telefono')
        entidad.email = data.get('email')
        entidad.rol_id = data.get('rolId')
        entidad.updated_at = db.func.current_timestamp()

        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Usuario actualizado', 'data': {
            'id': entidad.id,
            'documento': entidad.documento,
            'nombres': entidad.nombres,
            'apellidos': entidad.apellidos,
            'telefono': entidad.telefono,
            'email': entidad.email,
            'rol_id': entidad.rol_id
        }}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/usuario/<string:documento>', methods=['DELETE'])
def usuario_eliminar(documento):
    """
    Elimina un usuario.

    :param id: Identificador del usuario.
    :return: Respuesta JSON.
    """
    try:
        entidad = Usuario.query.filter_by(documento=documento).first()

        if entidad is None:
            return jsonify({'status': 'failure', 'message': 'Usuario encontrado'}), 404

        db.session.delete(entidad)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Usuario eliminado'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/usuario/cambiar-password', methods=['PUT'])
def usuario_cambiar_password():
    """
    Cambia la contraseña de un usuario.

    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()
        entidad = Usuario.query.filter_by(documento=data.get('documento')).first()

        if entidad is None:
            return jsonify({'status': 'failure', 'message': 'Usuario no encontrado'}), 404

        hashed_password = generate_password_hash(data.get('password'), method='pbkdf2:sha256')

        entidad.password = hashed_password
        entidad.updated_at = db.func.current_timestamp()

        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Contraseña actualizada'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route("/registro", methods=['GET'])
def registro():
    """
    Muestra la ruta para el registro de un administrador para el parqueadero.
    """
    roles = Rol.query.all()
    return render_template('registro.html', titulo='Registro', roles=roles)


@app.route('/registro', methods=['POST'])
def registro_crear():
    """
    Crea un nuevo usuario administrador para el parqueadero.

    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()

        hashed_password = generate_password_hash(data.get('password'), method='pbkdf2:sha256')

        entidad = Usuario(
            documento=data.get('documento'),
            nombres=data.get('nombres'),
            apellidos=data.get('apellidos'),
            telefono=data.get('telefono'),
            email=data.get('email'),
            rol_id=data.get('rolId'),
            password=hashed_password
        )

        db.session.add(entidad)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Usuario creado', 'data': {
            'id': entidad.id,
            'documento': entidad.documento,
            'nombres': entidad.nombres,
            'apellidos': entidad.apellidos,
            'telefono': entidad.telefono,
            'email': entidad.email,
            'rol_id': entidad.rol_id
        }}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
