from flask import jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash

from app import app, db

from app.forms import UsuarioForm
from app.models import Cliente, MedioPago, Pais, Parqueadero, Rol, TarifaTipo, Usuario, VehiculoTipo


@app.route("/")
def index():
    return render_template("login.html", titulo='Inicio', nombre='Alex')


@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    Muestra el dashboard de la aplicación.

    :return: Plantilla HTML.
    """
    return render_template('dashboard.html', titulo='Dashboard')


@app.route("/vehiculo-tipo", methods=['GET'])
@login_required
def vehiculo_tipo():
    tipos_vehiculo = VehiculoTipo.query.all()
    return render_template("vehiculo-tipo.html", titulo='Tipo de Vehículo', tipos_vehiculo=tipos_vehiculo)


@app.route('/vehiculo-tipo/<int:id>', methods=['DELETE'])
@login_required
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
@login_required
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
@login_required
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
@login_required
def tarifa_tipo():
    """
    Muestra la lista de tipos de tarifa.
    """
    entidades = TarifaTipo.query.all()
    return render_template("tarifa-tipo.html", titulo='Tipo de Tarifa', entidades=entidades)


@app.route('/tarifa-tipo', methods=['POST'])
@login_required
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
@login_required
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
@login_required
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
@login_required
def medio_pago():
    """
    Muestra la lista de tipos de tarifa.
    """
    entidades = MedioPago.query.all()
    return render_template('medio-pago.html', titulo='Medios de Pago', entidades=entidades)


@app.route('/medio-pago', methods=['POST'])
@login_required
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
@login_required
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
@login_required
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
@login_required
def cliente():
    """
    Muestra la lista de tipos de tarifa.
    """
    entidades = Cliente.query.all()
    return render_template('cliente.html', titulo='Clientes', entidades=entidades)


@app.route('/cliente', methods=['POST'])
@login_required
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
@login_required
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
@login_required
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
@login_required
def rol():
    """
    Muestra la lista de roles.
    """
    entidades = Rol.query.all()
    return render_template('rol.html', titulo='Roles', entidades=entidades)


@app.route("/usuario", methods=['GET'])
@login_required
def usuario():
    """
    Muestra la lista de usuarios.
    """
    entidades = Usuario.query.all()
    roles = Rol.query.all()
    return render_template('usuario.html', titulo='Usuarios', entidades=entidades, roles=roles)


@app.route('/usuario', methods=['POST'])
@login_required
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
@login_required
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
@login_required
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
@login_required
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
    paises = Pais.query.all()
    return render_template('registro.html', titulo='Registro', paises=paises)


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
            rol_id=1,
            password=hashed_password,
            es_propietario=True
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


@app.route("/parqueadero", methods=['POST'])
@login_required
def parqueadero():
    """
    Crea un nuevo parqueadero.

    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()
        entidad = Parqueadero(
            rut=data.get('rut'),
            nombre=data.get('nombre'),
            direccion=data.get('direccion'),
            email=data.get('email'),
            ciudad=data.get('ciudad'),
            telefono=data.get('telefono'),
            usuario_id=data.get('usuarioId'),
            pais_id=data.get('paisId')
        )

        print('entidad', entidad)

        db.session.add(entidad)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Parqueadero creado', 'data': {
            'id': entidad.id,
            'nombre': entidad.nombre,
            'direccion': entidad.direccion,
            'telefono': entidad.telefono,
            'email': entidad.email,
            'pais_id': entidad.pais_id,
            'usuario_id': entidad.usuario_id
        }}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route("/login", methods=['GET'])
def login():
    return render_template('login.html', titulo='Iniciar Sesión')


@app.route("/login", methods=['POST'])
def login_post():
    """
    Inicia sesión en la aplicación.

    :return: Redirección a la página de inicio.
    """
    if current_user.is_authenticated:
        return jsonify({"success": True, "redirect_url": url_for('dashboard')})
    
    data = request.get_json()
    email = data.get('email')

    usuario = Usuario.query.filter_by(email=email).first()

    if usuario is None or not usuario.check_password(data.get('password')):
        return jsonify({"success": False, "message": "Credenciales inválidas"}), 401

    login_user(usuario)

    next = request.args.get('next')
    print('next', next)

    if not next:
        return jsonify({"success": True, "redirect_url": url_for('dashboard')})
    else:
        return jsonify({"success": True, "redirect_url": next})


@app.route("/logout", methods=['GET'])
def logout():
    """
    Cierra sesión en la aplicación.

    :return: Redirección a la página de inicio.
    """
    logout_user()
    return redirect(url_for('login'))


@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """
    Muestra el perfil del usuario.

    :return: Plantilla HTML.
    """
    form = UsuarioForm()

    if form.validate_on_submit():
        documento = form.documento.data
        nombres = form.nombres.data
        apellidos = form.apellidos.data
        telefono = form.telefono.data

        current_user.documento = documento
        current_user.nombres = nombres
        current_user.apellidos = apellidos
        current_user.telefono = telefono

        db.session.commit()

    return render_template('perfil.html', titulo='Perfil', form=form)
