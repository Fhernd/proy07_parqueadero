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

from app.vehiculo_tipo_routes import VehiculoTipoRoutes
from app.tarifa_tipo_routes import TarifaTipoRoutes

app.register_blueprint(VehiculoTipoRoutes().blueprint)
app.register_blueprint(TarifaTipoRoutes().blueprint)


@app.route("/tarifas", methods=['GET'])
@login_required
@todos_permiso.require(http_exception=403)
def get_tarifas():
    """
    Recupera los tipos de tarifa.

    :return: Respuesta JSON.
    """
    entidades = Tarifa.query.all()
    
    return jsonify({'status': 'success', 'message': 'Consulta realizada de forma satisfactoria', 'data': [{
        'id': entidad.id,
        'costo': entidad.costo,
        'nombre': entidad.nombre,
    } for entidad in entidades]}), 200


@app.route("/medio-pago", methods=['GET'])
@login_required
@propietario_admin_permission.require(http_exception=403)
def medio_pago():
    """
    Muestra la lista de tipos de tarifa.
    """
    g.template_name = 'base.html'
    
    entidades = MedioPago.query.all()
    return render_template('medio-pago.html', titulo='Medios de Pago', entidades=entidades)


@app.route("/medios-pago", methods=['GET'])
@login_required
@todos_permiso.require(http_exception=403)
def get_medios_pago():
    """
    Recupera los medios de pago.

    :return: Respuesta JSON.
    """
    entidades = MedioPago.query.all()
    
    return jsonify({'status': 'success', 'message': 'Consulta realizada de forma satisfactoria', 'data': [{
        'id': entidad.id,
        'nombre': entidad.nombre,
        'activo': entidad.activo
    } for entidad in entidades]}), 200


@app.route('/medio-pago', methods=['POST'])
@login_required
@propietario_admin_permission.require(http_exception=403)
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
@propietario_admin_permission.require(http_exception=403)
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
@propietario_admin_permission.require(http_exception=403)
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
@propietario_admin_permission.require(http_exception=403)
def cliente():
    """
    Muestra la lista de tipos de tarifa.
    """
    g.template_name = 'base.html'
    entidades = Cliente.query.all()
    vehiculos_tipos = VehiculoTipo.query.all()

    return render_template('cliente.html', titulo='Clientes', entidades=entidades, vehiculos_tipos=vehiculos_tipos)


@app.route('/cliente', methods=['POST'])
@login_required
@todos_permiso.require(http_exception=403)
def cliente_crear():
    """
    Crea un nuevo cliente.

    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()
        print('data', data)

        if data.get('parqueadero_id') is None:
            data['parqueadero_id'] = current_user.parqueadero_id

        cliente = Cliente.query.filter_by(documento=data.get('documento')).first()

        if cliente is not None:
            return jsonify({'status': 'existente', 'message': 'Ya existe un cliente con el documento dado.'}), 200

        entidad = Cliente(documento=data.get('documento'), nombres=data.get('nombres'), apellidos=data.get('apellidos'), telefono=data.get('telefono'), email=data.get('email'), direccion=data.get('direccion'), parqueadero_id=data.get('parqueadero_id'))

        db.session.add(entidad)
        db.session.commit()

        if data.get('placa') is not None:
            vehiculo = Vehiculo.query.filter_by(placa=data.get('placa')).first()
            print('id cliente', entidad.id)
            vehiculo.cliente_id = entidad.id
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
@todos_permiso.require(http_exception=403)
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
        if data.get('parqueadero_id') is not None:
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
@propietario_admin_permission.require(http_exception=403)
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
@propietario_permission.require(http_exception=403)
def rol():
    """
    Muestra la lista de roles.
    """
    g.template_name = 'base.html'
    
    entidades = Rol.query.all()
    return render_template('rol.html', titulo='Roles', entidades=entidades)


@app.route("/usuario", methods=['GET'])
@login_required
@propietario_admin_permission.require(http_exception=403)
def usuario():
    """
    Muestra la lista de usuarios.
    """
    g.template_name = 'base.html'
    
    entidades = Usuario.query.all()
    for e in entidades:
        print(e)

    parqueadero = Parqueadero.query.filter_by(usuario_id=current_user.parqueadero_id).first()

    if parqueadero is not None:
        entidades = Usuario.query.filter_by(parqueadero_id=parqueadero.id).all()

    roles = Rol.query.all()
    sedes = Sede.query.all()

    roles_nombres = [r.nombre for r in current_user.roles]

    es_propietario = 'Propietario' in roles_nombres
    
    return render_template('usuario.html', titulo='Usuarios', entidades=entidades, roles=roles, sedes=sedes, es_propietario=es_propietario)


@app.route('/usuario', methods=['POST'])
@login_required
@propietario_admin_permission.require(http_exception=403)
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
            password=hashed_password,
            parqueadero_id=current_user.parqueadero_id
        )

        db.session.add(entidad)
        db.session.commit()

        rol = usuario_rol.insert().values(usuario_id=entidad.id, rol_id=data.get('rolId'))
        
        db.session.execute(rol)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Usuario creado', 'data': {
            'id': entidad.id,
            'documento': entidad.documento,
            'nombres': entidad.nombres,
            'apellidos': entidad.apellidos,
            'telefono': entidad.telefono,
            'email': entidad.email
        }}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/usuario/<string:documento>', methods=['PUT'])
@login_required
@propietario_admin_permission.require(http_exception=403)
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
@propietario_admin_permission.require(http_exception=403)
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
        
        # Eliminar de la tabla de relación sede_usuario:
        sede_usuario = SedeUsuario.query.filter_by(usuario_id=entidad.id).first()

        if sede_usuario is not None:
            db.session.delete(sede_usuario)
            db.session.commit()

        db.session.delete(entidad)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Usuario eliminado'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/usuario/cambiar-password', methods=['PUT'])
@login_required
@propietario_admin_permission.require(http_exception=403)
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


@app.route('/usuario/<string:documento>', methods=['GET'])
@login_required
@todos_permiso.require(http_exception=403)
def usuario_obtener(documento):
    """
    Obtiene un usuario.

    :param id: Identificador del usuario.
    :return: Respuesta JSON.
    """
    entidad = Usuario.query.filter_by(documento=documento).first()

    if entidad is not None:
        return jsonify({'status': 'existente', 'message': 'Ya existe un usuario con el documento dado.'}), 200

    return jsonify({'status': 'faile', 'message': 'Usuario encontrado', 'data': {}}), 200


@app.route("/registro", methods=['GET'])
@propietario_admin_permission.require(http_exception=403)
def registro():
    """
    Muestra la ruta para el registro de un administrador para el parqueadero.
    """
    g.template_name = 'base.html'
    
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
            rol_id=2,
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
@propietario_permission.require(http_exception=403)
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
    """
    Muestra la página de inicio de sesión.

    :return: Plantilla HTML.
    """
    return render_template('login.html', titulo='Iniciar Sesión')


@app.route("/login", methods=['POST'])
def login_post():
    """
    Inicia sesión en la aplicación.

    :return: Redirección a la página de inicio.
    """
    if current_user.is_authenticated:
        identity_changed.send(current_app._get_current_object(), identity=Identity(current_user.id))
        return jsonify({"success": True, "redirect_url": url_for('dashboard')})
    
    data = request.get_json()
    email = data.get('email')

    usuario = Usuario.query.filter_by(email=email).first()

    if usuario is None or not usuario.check_password(data.get('password')) or not usuario.activo:
        return jsonify({"success": False, "message": "Credenciales inválidas"}), 401

    login_user(usuario)
    identity_changed.send(current_app._get_current_object(), identity=Identity(usuario.id))

    next = request.args.get('next')

    if not next:
        roles = [rol.nombre for rol in usuario.roles]
        if tiene_rol(current_user.roles, [Roles.OPERARIO.value]):
            return jsonify({"success": True, "redirect_url": url_for('parqueos')})
        else:
            return jsonify({"success": True, "redirect_url": url_for('dashboard')})
    else:
        return jsonify({"success": True, "redirect_url": next})


@app.route("/logout", methods=['GET'])
@login_required
def logout():
    """
    Cierra sesión en la aplicación.

    :return: Redirección a la página de inicio.
    """
    logout_user()
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())

    return redirect(url_for('login'))


@app.route('/perfil', methods=['GET', 'POST'])
@login_required
@todos_permiso.require(http_exception=403)
def perfil():
    """
    Muestra el perfil del usuario.

    :return: Plantilla HTML.
    """
    g.template_name = 'base.html'
    
    form = UsuarioForm()
    cambiar_clave_form = CambiarClaveForm()

    if form.submit.data and form.validate_on_submit():
        current_user.documento = form.documento.data
        current_user.nombres = form.nombres.data
        current_user.apellidos = form.apellidos.data
        current_user.telefono = form.telefono.data

        db.session.commit()
        flash('Perfil actualizado correctamente.', 'perfil-success')
        return redirect(url_for('perfil'))

    if cambiar_clave_form.submit.data and cambiar_clave_form.validate_on_submit():
        clave_actual = cambiar_clave_form.clave_actual.data

        if not current_user.check_password(clave_actual):
            flash('La contraseña actual es incorrecta', 'cambio-clave-danger')
        else:
            current_user.set_password(cambiar_clave_form.clave_nueva.data)
            db.session.commit()
            flash('Contraseña cambiada correctamente.', 'cambio-clave-success')
            return redirect(url_for('perfil'))

    return render_template('perfil.html', titulo='Perfil', form=form, cambiar_clave_form=cambiar_clave_form)


@app.route('/parqueadero-informacion', methods=['GET', 'POST'])
@login_required
@propietario_admin_permission.require(http_exception=403)
def parqueadero_informacion():
    """
    Muestra la información del parqueadero.

    :return: Plantilla HTML.
    """
    g.template_name = 'base.html'
    
    parqueadero = Parqueadero.query.filter_by(usuario_id=current_user.parqueadero_id).first()

    form = ParqueaderoInformacionForm(obj=parqueadero)

    if form.validate_on_submit():
        form.populate_obj(parqueadero)
        db.session.commit()
        flash('Información del parqueadero actualizada correctamente.', 'parqueadero-informacion-success')
        return redirect(url_for('parqueadero_informacion'))
    
    return render_template('parqueadero-informacion.html', titulo='Información del Parqueadero', form=form)


@app.route('/sedes', methods=['GET'])
@login_required
@propietario_admin_permission.require(http_exception=403)
def sedes():
    """
    Función de vista para mostrar la página de sedes.
    """
    g.template_name = 'base.html'
    
    parqueadero = Parqueadero.query.filter_by(usuario_id=current_user.parqueadero_id).first()
    sedes = Sede.query.filter_by(parqueadero_id=parqueadero.id).all()

    return render_template('sedes.html', titulo='Sedes', entidades=sedes)


@app.route('/sede', methods=['POST'])
@login_required
@propietario_admin_permission.require(http_exception=403)
def sede_crear():
    """
    Crea una nueva sede.

    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()
        parqueadero = Parqueadero.query.filter_by(usuario_id=current_user.parqueadero_id).first()
        entidad = Sede(
            nombre=data.get('nombre'),
            direccion=data.get('direccion'),
            telefono=data.get('telefono'),
            email=data.get('email'),
            parqueadero_id=parqueadero.id
        )

        db.session.add(entidad)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Sede creada', 'data': {
            'id': entidad.id,
            'nombre': entidad.nombre,
            'direccion': entidad.direccion,
            'telefono': entidad.telefono,
            'email': entidad.email,
            'parqueadero_id': entidad.parqueadero_id
        }}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/sede/<int:id>', methods=['PUT'])
@login_required
@propietario_admin_permission.require(http_exception=403)
def sede_actualizar(id):
    """
    Actualiza una sede.

    :param id: Identificador de la sede.
    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()
        entidad = Sede.query.get(id)

        if entidad is None:
            return jsonify({'status': 'failure', 'message': 'Sede encontrada'}), 404

        entidad.nombre = data.get('nombre')
        entidad.direccion = data.get('direccion')
        entidad.telefono = data.get('telefono')
        entidad.email = data.get('email')
        entidad.updated_at = db.func.current_timestamp()

        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Sede actualizada', 'data': {
            'id': entidad.id,
            'nombre': entidad.nombre,
            'direccion': entidad.direccion,
            'telefono': entidad.telefono,
            'email': entidad.email,
            'parqueadero_id': entidad.parqueadero_id
        }}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/sede/<int:id>', methods=['DELETE'])
@login_required
@propietario_admin_permission.require(http_exception=403)
def sede_eliminar(id):
    """
    Elimina una sede.

    :param id: Identificador de la sede.
    :return: Respuesta JSON.
    """
    try:
        entidad = Sede.query.get(id)

        if entidad is None:
            return jsonify({'status': 'failure', 'message': 'Sede no encontrada'}), 404

        db.session.delete(entidad)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Sede eliminada'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/sede/<int:id>/modulos', methods=['GET'])
@login_required
@todos_permiso.require(http_exception=403)
def sede_modulos(id):
    """
    Muestra los módulos de una sede.

    :param id: Identificador de la sede.
    :return: Plantilla HTML.
    """
    sede = Sede.query.get(id)
    modulos = sede.modulos

    return jsonify({'status': 'success', 'message': 'Consulta realizada de forma satisfactoria', 'data': [{
        'id': modulo.id,
        'nombre': modulo.nombre,
        'habilitado': modulo.habilitado,
        'descripcion': modulo.descripcion,
        'disponible': not bool(Parqueo.query.filter_by(modulo_id=modulo.id, fecha_hora_salida=None).count())
    } for modulo in modulos]}), 200


@app.route('/sede/<int:id>/modulo', methods=['POST'])
@login_required
@propietario_admin_permission.require(http_exception=403)
def sede_modulo_crear(id):
    """
    Crea un nuevo módulo en una sede.

    :param id: Identificador de la sede.
    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()
        entidad = Modulo(
            nombre=data.get('moduloNombre'),
            habilitado=data.get('moduloHabilitado'),
            descripcion=data.get('moduloDescripcion'),
            sede_id=id
        )

        db.session.add(entidad)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Módulo creado', 'data': {
            'id': entidad.id,
            'nombre': entidad.nombre,
            'descripcion': entidad.descripcion,
            'habilitado': entidad.habilitado,
            'sede_id': entidad.sede_id
        }}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/sede/<int:id>/modulo/<int:modulo_id>', methods=['PUT'])
@login_required
@propietario_admin_permission.require(http_exception=403)
def sede_modulo_actualizar(id, modulo_id):
    """
    Actualiza un módulo en una sede.

    :param id: Identificador de la sede.
    :param modulo_id: Identificador del módulo.
    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()
        entidad = Modulo.query.get(modulo_id)

        if entidad is None:
            return jsonify({'status': 'failure', 'message': 'Módulo no encontrado'}), 404

        entidad.nombre = data.get('moduloNombre')
        entidad.habilitado = data.get('moduloHabilitado')
        entidad.descripcion = data.get('moduloDescripcion')
        entidad.updated_at = db.func.current_timestamp()

        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Módulo actualizado', 'data': {
            'id': entidad.id,
            'nombre': entidad.nombre,
            'descripcion': entidad.descripcion,
            'habilitado': entidad.habilitado,
            'sede_id': entidad.sede_id
        }}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/sede/<int:id>/modulo/<int:modulo_id>', methods=['DELETE'])
@login_required
@propietario_admin_permission.require(http_exception=403)
def sede_modulo_eliminar(id, modulo_id):
    """
    Elimina un módulo en una sede.

    :param id: Identificador de la sede.
    :param modulo_id: Identificador del módulo.
    :return: Respuesta JSON.
    """
    try:
        entidad = Modulo.query.get(modulo_id)

        if entidad is None:
            return jsonify({'status': 'failure', 'message': 'Módulo no encontrado'}), 404

        db.session.delete(entidad)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Módulo eliminado'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/sede/asignar-usuario', methods=['POST'])
@login_required
@propietario_admin_permission.require(http_exception=403)
def sede_asignar_usuario():
    """
    Asigna un usuario a una sede.

    :param id: Identificador de la sede.
    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()
        documento = data.get('documento')
        sede_id = data.get('sedeId')
        usuario = Usuario.query.filter_by(documento=documento).first()

        if usuario is None:
            return jsonify({'status': 'failure', 'message': 'Usuario no encontrado'}), 404
        
        asignacion = SedeUsuario.query.filter_by(sede_id=sede_id, usuario_id=usuario.id).first()
        if asignacion is not None:
            return jsonify({'status': 'existente', 'message': 'Usuario ya asignado a la sede seleccionada.'}), 200

        asignacion = SedeUsuario(sede_id=sede_id, usuario_id=usuario.id)
        db.session.add(asignacion)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Usuario asignado a la sede'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/sede/sede-asignada/<int:documento>', methods=['GET'])
@login_required
@propietario_admin_permission.require(http_exception=403)
def sede_asignada(documento):
    """
    Muestra los usuarios asignados a una sede.

    :param id: Identificador de la sede.
    :return: Respuesta JSON.
    """
    usuario = Usuario.query.filter_by(documento=documento).first()
    asignaciones = usuario.sedes

    return jsonify({'status': 'success', 'message': 'Consulta realizada de forma satisfactoria', 'data': [{
        'id': asignacion.id,
        'sede_id': asignacion.sede_id,
        'usuario_id': asignacion.usuario_id
    } for asignacion in asignaciones]}), 200


@app.route('/cliente/<string:documento>/vehiculos', methods=['GET'])
@login_required
@todos_permiso.require(http_exception=403)
def cliente_vehiculos(documento):
    """
    Muestra los vehículos de un cliente.

    :param documento: Documento del cliente.
    :return: Respuesta JSON.
    """
    cliente = Cliente.query.filter_by(documento=documento).first()
    vehiculos = cliente.vehiculos

    return jsonify({'status': 'success', 'message': 'Consulta realizada de forma satisfactoria', 'data': [{
        'id': vehiculo.id,
        'placa': vehiculo.placa,
        'marca': vehiculo.marca,
        'modelo': vehiculo.modelo,
        'tipo': vehiculo.vehiculo_tipo.nombre,
        'disponible': vehiculo.disponible
    } for vehiculo in vehiculos]}), 200


@app.route('/cliente/crear-vehiculo', methods=['POST'])
@login_required
@todos_permiso.require(http_exception=403)
def cliente_crear_vehiculo():
    """
    Crea un nuevo vehículo para un cliente.

    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()

        cliente = Cliente.query.filter_by(documento=data.get('clienteDocumento')).first()
        vehiculo_tipo_id = data.get('vehiculoTipoId')

        entidad = Vehiculo(
            placa=data.get('vehiculoPlaca'),
            marca=data.get('vehiculoMarca'),
            modelo=data.get('vehiculoModelo'),
            cliente_id=cliente.id,
            vehiculo_tipo_id=vehiculo_tipo_id,
        )

        db.session.add(entidad)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Vehículo creado', 'data': {
            'id': entidad.id,
            'placa': entidad.placa,
            'marca': entidad.marca,
            'modelo': entidad.modelo,
            'cliente_id': entidad.cliente_id,
            'vehiculo_tipo_id': entidad.vehiculo_tipo_id,
            'vehiculo_tipo': entidad.vehiculo_tipo.nombre,
            'disponible': entidad.disponible
        }}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/cliente/editar-vehiculo/<int:vehiculo_id>', methods=['PUT'])
@login_required
@todos_permiso.require(http_exception=403)
def cliente_editar_vehiculo(vehiculo_id):
    """
    Edita un vehículo de un cliente.

    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()

        vehiculo = Vehiculo.query.get(vehiculo_id)

        if vehiculo is None:
            return jsonify({'status': 'failure', 'message': 'Vehículo no encontrado'}), 404

        vehiculo.placa = data.get('vehiculoPlaca')
        vehiculo.marca = data.get('vehiculoMarca')
        vehiculo.modelo = data.get('vehiculoModelo')
        vehiculo.vehiculo_tipo_id = data.get('vehiculoTipoId')
        vehiculo.updated_at = db.func.current_timestamp()

        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Vehículo actualizado', 'data': {
            'id': vehiculo.id,
            'placa': vehiculo.placa,
            'marca': vehiculo.marca,
            'modelo': vehiculo.modelo,
            'cliente_id': vehiculo.cliente_id,
            'vehiculo_tipo_id': vehiculo.vehiculo_tipo_id,
            'vehiculo_tipo': vehiculo.vehiculo_tipo.nombre,
            'disponible': vehiculo.disponible
        }}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/cliente/vehiculo/<int:vehiculo_id>/cambiar-disponibilidad', methods=['DELETE'])
@login_required
@todos_permiso.require(http_exception=403)
def cliente_eliminar_vehiculo(vehiculo_id):
    """
    Elimina un vehículo de un cliente.

    :return: Respuesta JSON.
    """
    try:
        vehiculo = Vehiculo.query.get(vehiculo_id)

        if vehiculo is None:
            return jsonify({'status': 'failure', 'message': 'Vehículo no encontrado'}), 404

        vehiculo.disponible = not vehiculo.disponible

        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Vehículo eliminado'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/cliente/vehiculo/<int:vehiculo_id>/arrendamientos', methods=['GET'])
@login_required
@todos_permiso.require(http_exception=403)
def cliente_vehiculo_arrendamientos(vehiculo_id):
    """
    Muestra los arrendamientos de un vehículo.

    :param vehiculo_id: Identificador del vehículo.
    :return: Respuesta JSON.
    """
    vehiculo = Vehiculo.query.get(vehiculo_id)
    arrendamientos = vehiculo.arrendamientos

    return jsonify({'status': 'success', 'message': 'Consulta realizada de forma satisfactoria', 'data': [{
        'id': arrendamiento.id,
        'vehiculoId': arrendamiento.vehiculo_id,
        'periodicidadId': arrendamiento.periodicidad_id,
        'tarifaId': arrendamiento.tarifa_id,
        'medioPagoId': arrendamiento.medio_pago_id,
        'periodicidad': arrendamiento.periodicidad.nombre,
        'medioPago': arrendamiento.medio_pago.nombre,
        'tarifa': arrendamiento.tarifa.nombre,
        'tarifa_costo': arrendamiento.tarifa.costo,
        'descripcion': arrendamiento.descripcion,
        'fecha_inicio': arrendamiento.fecha_inicio,
        'fecha_fin': arrendamiento.fecha_fin,
        'ha_sido_pausado': arrendamiento.ha_sido_pausado,
        'tiempo_pausa': arrendamiento.tiempo_pausa,
    } for arrendamiento in arrendamientos]}), 200


@app.route('/periodicidades', methods=['GET'])
@login_required
@todos_permiso.require(http_exception=403)
def periodicidades():
    """
    Muestra las periodicidades.

    :return: Respuesta JSON.
    """
    parqueadero_id = current_user.parqueadero_id
    parqueadero = Parqueadero.query.filter_by(id=parqueadero_id).first()
    periodicidades = Periodicidad.query.filter_by(parqueadero_id=parqueadero.id).all()

    return jsonify({'status': 'success', 'message': 'Consulta realizada de forma satisfactoria', 'data': [{
        'id': entidad.id,
        'nombre': entidad.nombre,
        'dias': entidad.dias
    } for entidad in periodicidades]}), 200


@app.route('/cliente/vehiculo/arrendamiento', methods=['POST'])
@login_required
@todos_permiso.require(http_exception=403)
def cliente_vehiculo_arrendamiento():
    """
    Crea un arrendamiento de un vehículo.

    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()

        descripcion = data.get('descripcion')
        vehiculo_id = data.get('vehiculoId')
        periodicidad_id = data.get('periodicidadId')
        medio_pago_id = data.get('medioPagoId')
        tarifa_id = data.get('tarifaId')
        fecha_inicio = data.get('fechaInicio')
        fecha_inicio += ' ' + data.get('horaInicio')
        fecha_fin = data.get('fechaFin')
        fecha_fin += ' ' + data.get('horaFin')

        fecha_inicio = datetime.strptime(fecha_inicio, '%Y/%m/%d %H:%M')
        fecha_fin = datetime.strptime(fecha_fin, '%Y/%m/%d %H:%M')

        entidad = Arrendamiento(
            descripcion=descripcion,
            vehiculo_id=vehiculo_id,
            periodicidad_id=periodicidad_id,
            medio_pago_id=medio_pago_id,
            tarifa_id=tarifa_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        db.session.add(entidad)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Arrendamiento creado', 'data': {
            'id': entidad.id,
            'vehiculoId': entidad.vehiculo_id,
            'periodicidadId': entidad.periodicidad_id,
            'tarifaId': entidad.tarifa_id,
            'medioPagoId': entidad.medio_pago_id,
            'periodicidad': entidad.periodicidad.nombre,
            'medioPago': entidad.medio_pago.nombre,
            'tarifa': entidad.tarifa.nombre,
            'tarifa_costo': entidad.tarifa.costo,
            'descripcion': entidad.descripcion,
            'fecha_inicio': entidad.fecha_inicio,
            'fecha_fin': entidad.fecha_fin,
            'ha_sido_pausado': entidad.ha_sido_pausado,
            'tiempo_pausa': entidad.tiempo_pausa
        }}), 201

    except Exception as e:
        print('e', e)
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    

@app.route('/cliente/vehiculo/arrendamiento/<int:id>', methods=['PUT'])
@login_required
@todos_permiso.require(http_exception=403)
def cliente_vehiculo_arrendamiento_actualizar(id):
    """
    Actualiza un arrendamiento de un vehículo.

    :param id: Identificador del arrendamiento.
    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()
        entidad = Arrendamiento.query.get(id)

        if entidad is None:
            return jsonify({'status': 'failure', 'message': 'Arrendamiento no encontrado'}), 404

        entidad.descripcion = data.get('descripcion')
        entidad.periodicidad_id = data.get('periodicidadId')
        entidad.medio_pago_id = data.get('medioPagoId')
        entidad.tarifa_id = data.get('tarifaId')

        fecha_inicio = data.get('fechaInicio')
        fecha_inicio += ' ' + data.get('horaInicio')
        fecha_fin = data.get('fechaFin')
        fecha_fin += ' ' + data.get('horaFin')

        fecha_inicio = datetime.strptime(fecha_inicio, '%Y/%m/%d %H:%M')
        fecha_fin = datetime.strptime(fecha_fin, '%Y/%m/%d %H:%M')

        entidad.fecha_inicio = fecha_inicio
        entidad.fecha_fin = fecha_fin
        entidad.hora_inicio = data.get('horaInicio')
        entidad.hora_fin = data.get('horaFin')

        entidad.updated_at = db.func.current_timestamp()

        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Arrendamiento actualizado', 'data': {
            'id': entidad.id,
            'vehiculoId': entidad.vehiculo_id,
            'periodicidadId': entidad.periodicidad_id,
            'tarifaId': entidad.tarifa_id,
            'medioPagoId': entidad.medio_pago_id,
            'periodicidad': entidad.periodicidad.nombre,
            'medioPago': entidad.medio_pago.nombre,
            'tarifa': entidad.tarifa.nombre,
            'tarifa_costo': entidad.tarifa.costo,
            'descripcion': entidad.descripcion,
            'fecha_inicio': entidad.fecha_inicio,
            'fecha_fin': entidad.fecha_fin,
            'ha_sido_pausado': entidad.ha_sido_pausado,
            'tiempo_pausa': entidad.tiempo_pausa
        }}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/cliente/vehiculo/arrendamiento/<int:id>', methods=['DELETE'])
@login_required
@todos_permiso.require(http_exception=403)
def cliente_vehiculo_arrendamiento_eliminar(id):
    """
    Elimina un arrendamiento de un vehículo.

    :param id: Identificador del arrendamiento.
    :return: Respuesta JSON.
    """
    try:
        entidad = Arrendamiento.query.get(id)

        if entidad is None:
            return jsonify({'status': 'failure', 'message': 'Arrendamiento no encontrado'}), 404

        db.session.delete(entidad)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Arrendamiento eliminado'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/cliente/<string:documento>/puntos', methods=['GET'])
@login_required
@todos_permiso.require(http_exception=403)
def get_cliente_puntos(documento):
    """
    Obtiene los puntos de un cliente.

    :param documento: Documento del cliente.

    :return: Respuesta JSON.
    """
    cliente = Cliente.query.filter_by(documento=documento).first()
    puntos = cliente.puntos

    total_puntos = sum([punto.cantidad for punto in puntos])
    
    puntos = {
        'data': {
            'documento': documento,
            'puntos': total_puntos,
        },
        'status': 'success',
    }

    return jsonify(puntos)


@app.route('/parqueos', methods=['GET'])
@login_required
@operario_permission.require(http_exception=403)
def parqueos():
    """
    Muestra la lista de parqueos.
    """
    g.template_name = 'base.html'
    sedes = [sede.sede for sede in current_user.sedes]
    tipos_vehiculos = VehiculoTipo.query.all()
    tipos_vehiculos_json = [to_json(tipo_vehiculo) for tipo_vehiculo in tipos_vehiculos]
    medios_pago = MedioPago.query.all()
    medios_pago = [to_json(medio_pago) for medio_pago in medios_pago]
    tarifas = Tarifa.query.all()
    tarifas = [to_json(tarifa) for tarifa in tarifas]

    return render_template('parqueos.html', titulo='Parqueos', sedes=sedes, tipos_vehiculos=tipos_vehiculos_json, medios_pago=medios_pago, tarifas=tarifas)


@app.route('/vehiculo/buscar/<placa>', methods=['GET'])
@login_required
def buscar_vehiculo(placa):
    """
    Busca un vehículo por placa.

    :param placa: Placa del vehículo.

    :return: Respuesta JSON.
    """
    vehiculo = Vehiculo.query.filter_by(placa=placa).first()

    if vehiculo is None:
        return jsonify({'status': 'failure', 'message': 'No existe un vehículo con la placa indicada.'}), 200

    return jsonify({
        'status': 'success',
        'data': {
            'id': vehiculo.id,
            'placa': vehiculo.placa,
            'marca': vehiculo.marca,
            'modelo': vehiculo.modelo,
            'tipo': vehiculo.vehiculo_tipo.nombre,
            'vehiculoTipoId': vehiculo.vehiculo_tipo.id,
            'disponible': vehiculo.disponible
        }
    })


@app.route('/parqueo/ingresar', methods=['POST'])
@login_required
@operario_permission.require(http_exception=403)
def ingresar_parqueo():
    """
    Ingresa un vehículo al parqueadero.

    :return: Respuesta JSON.
    """
    try:
        data = request.get_json()
        modulo_id = data.get('moduloId')

        modulo_ocupado = Parqueo.query.filter_by(modulo_id=modulo_id, fecha_hora_salida=None).first()

        if modulo_ocupado is not None:
            return jsonify({'status': 'warning', 'message': 'El módulo seleccionado se encuentra ocupado'}), 200

        modulo = Modulo.query.get(modulo_id)
        placa = data.get('placa')
        vehiculo = Vehiculo.query.filter_by(placa=placa).first()

        tipo_vehiculo = VehiculoTipo.query.get(data.get('vehiculoTipoId'))
        tipo_vehiculo = {
            'id': tipo_vehiculo.id,
            'nombre': tipo_vehiculo.nombre
        }

        if vehiculo is not None:

            tarifa = Tarifa.query.get(vehiculo.tarifa_id)
            tipo_vehiculo['tarifa'] = {
                'id': tarifa.id,
                'nombre': tarifa.nombre,
                'costo': tarifa.costo
            }

            parqueo = Parqueo.query.filter_by(vehiculo_id=vehiculo.id, fecha_hora_salida=None).first()

            if parqueo is not None:
                return jsonify({'status': 'warning', 'message': 'El vehículo ya se encuentra en el parqueadero'}), 200
            
        if vehiculo is not None:
            fecha_actual = datetime.now()
            
            arrendamiento = Arrendamiento.query.filter_by(vehiculo_id=vehiculo.id).order_by(Arrendamiento.fecha_fin.desc()).first()

            if arrendamiento is not None:
                if fecha_actual > arrendamiento.fecha_fin:
                    return jsonify({'status': 'warning', 'message': 'El arrendamiento del vehículo ha finalizado'}), 200
                
                if arrendamiento.ha_sido_pausado:
                    return jsonify({'status': 'warning', 'message': 'El arrendamiento del vehículo se encuentra en pausa'}), 200
                
                parqueo = Parqueo(
                    vehiculo_id=vehiculo.id,
                    modulo_id=modulo.id,
                )

                tarifa = Tarifa.query.get(arrendamiento.tarifa_id)

                db.session.add(parqueo)
                db.session.commit()

                return jsonify({'status': 'arrendamiento', 'message': 'El vehículo cuenta con un arrendamiento activo. Puede ingresar al parqueadero.', 'tipoVehiculo': tipo_vehiculo, 'tarifa': tarifa}), 200


        if vehiculo is None:
            vehiculo_tipo_id = data.get('vehiculoTipoId')
            vehiculo = Vehiculo(
                placa=placa,
                vehiculo_tipo_id=vehiculo_tipo_id,
                tarifa_id=data.get('tarifaId'),
            )

            tarifa = Tarifa.query.get(data.get('tarifaId'))
            tipo_vehiculo['tarifa'] = {
                'id': tarifa.id,
                'nombre': tarifa.nombre,
                'costo': tarifa.costo
            }

            db.session.add(vehiculo)
            db.session.flush()
        
        parqueo = Parqueo(
            vehiculo_id=vehiculo.id,
            modulo_id=modulo.id,
        )

        db.session.add(parqueo)

        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Vehículo ingresado al parqueadero', 'data': {
            'tipoVehiculo': tipo_vehiculo
        }}), 200
    except Exception as e:
        print('Error:', e)
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/sede/<int:sede_id>/parqueos-activos', methods=['GET'])
@login_required
@operario_permission.require(http_exception=403)
def parqueos_activos(sede_id):
    """
    Obtiene los parqueos activos de una sede.

    :param sede_id: Identificador de la sede.

    :return: Respuesta JSON.
    """
    parqueos = (
        Parqueo.query
        .join(Modulo, Parqueo.modulo_id == Modulo.id)
        .filter(Modulo.sede_id == sede_id, Parqueo.fecha_hora_salida == None)
        .all()
    )

    return jsonify({
        'status': 'success',
        'message': 'Consulta realizada de forma satisfactoria',
        'data': [
            {
                'id': parqueo.id,
                'vehiculo': {
                    'id': parqueo.vehiculo_id,
                    'placa': parqueo.vehiculo.placa,
                    'marca': parqueo.vehiculo.marca,
                    'modelo': parqueo.vehiculo.modelo,
                    'tipo': parqueo.vehiculo.vehiculo_tipo.nombre,
                    'tarifa': determinar_tarifa(parqueo)
                },
                'modulo': {
                    'id': parqueo.modulo_id,
                    'nombre': parqueo.modulo.nombre,
                    'habilitado': parqueo.modulo.habilitado,
                    'descripcion': parqueo.modulo.descripcion
                },
                'fechaHoraEntrada': parqueo.fecha_hora_entrada,
                'fechaHoraSalida': parqueo.fecha_hora_salida,
                'esArrendamiento': Arrendamiento.query.filter_by(vehiculo_id=parqueo.vehiculo_id).first() is not None
            }
            for parqueo in parqueos
        ]
    }), 200


def determinar_tarifa(parqueo):
    """
    Determina la tarifa de un parqueo.

    :param parqueo: Parqueo.
    :return: Tarifa.
    """
    fecha_actual = datetime.now()

    arrendamiento = Arrendamiento.query.filter(
        Arrendamiento.vehiculo_id == parqueo.vehiculo_id,
        Arrendamiento.fecha_inicio <= fecha_actual,
        Arrendamiento.fecha_fin >= fecha_actual
    ).first()

    if arrendamiento:
        return {
            'id': arrendamiento.tarifa_id,
            'nombre': arrendamiento.tarifa.nombre,
            'costo': arrendamiento.tarifa.costo
        }
    
    return {
        'id': parqueo.vehiculo.tarifa_id,
        'nombre': parqueo.vehiculo.tarifa.nombre,
        'costo': parqueo.vehiculo.tarifa.costo
    }


@app.route('/parqueo/vehiculo/retirar', methods=['POST'])
def retirar_vehiculo():
    data = request.get_json()
    placa = data.get('placa')
    total_pagado = data.get('totalPagado')
    medio_pago_id = data.get('metodoPagoId')
    es_arrendamiento = data.get('esArrendamiento')

    vehiculo = Vehiculo.query.filter_by(placa=placa).first()
    if not vehiculo:
        return jsonify({'status': 'error', 'message': 'Vehículo no encontrado'}), 404

    parqueo = Parqueo.query.filter_by(vehiculo_id=vehiculo.id, fecha_hora_salida=None).first()
    if not parqueo:
        return jsonify({'status': 'error', 'message': 'Parqueo no encontrado o ya retirado'}), 404

    parqueo.fecha_hora_salida = datetime.now()
    if not es_arrendamiento:
        parqueo.total_pagado = total_pagado
        parqueo.metodo_pago_id = medio_pago_id

    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Vehículo retirado exitosamente'}), 200


@app.route('/cliente/vehiculo/arrendamiento/<int:arrendamiento_id>/cambiar-estado-pausa', methods=['PUT'])
@login_required
@todos_permiso.require(http_exception=403)
def cambiar_estado_pausa(arrendamiento_id):
    data = request.get_json()
    tiempo_pausa = data.get('tiempoPausa')

    arrendamiento = Arrendamiento.query.get(arrendamiento_id)
    if not arrendamiento:
        return jsonify({'status': 'error', 'message': 'Arrendamiento no encontrado'}), 404
    
    fecha_actual = datetime.now()
    fecha_actual += timedelta(days=tiempo_pausa)
    fecha_fin = arrendamiento.fecha_fin
    diferencia = (fecha_fin - fecha_actual).days

    if diferencia < tiempo_pausa:
        return jsonify({'status': 'tiempoMenor', 'message': 'El tiempo de pausa no puede ser mayor al tiempo restante del arrendamiento.'}), 200

    arrendamiento.tiempo_pausa = tiempo_pausa
    arrendamiento.ha_sido_pausado = True
    arrendamiento.fecha_fin += timedelta(days=tiempo_pausa)
    arrendamiento.fecha_pausa = fecha_actual

    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Estado de pausa cambiado exitosamente'}), 200


@app.route('/medio-pago/<int:medioPagoId>/activar-desactivar', methods=['PUT'])
@login_required
@propietario_admin_permission.require(http_exception=403)
def activar_desactivar_medio_pago(medioPagoId):
    medio_pago = MedioPago.query.get(medioPagoId)
    if not medio_pago:
        return jsonify({'status': 'error', 'message': 'Medio de pago no encontrado'}), 404

    medio_pago.activo = not medio_pago.activo

    db.session.commit()

    estado = 'activado' if medio_pago.activo else 'desactivado'
    return jsonify({'status': 'success', 'message': f'Medio de pago {estado} exitosamente'}), 200


@app.route('/usuario/activar-desactivar/<documento>', methods=['PUT'])
@login_required
@propietario_admin_permission.require(http_exception=403)
def activar_desactivar_usuario(documento):
    """
    Activa o desactiva un usuario.

    :param documento: Documento del usuario.
    :return: Respuesta JSON.
    """
    usuario = Usuario.query.filter_by(documento=documento).first()
    if not usuario:
        return jsonify({'status': 'error', 'message': 'Usuario no encontrado'}), 404

    usuario.activo = not usuario.activo

    db.session.commit()

    estado = 'activado' if usuario.activo else 'desactivado'
    return jsonify({'status': 'success', 'message': f'Usuario {estado} exitosamente'}), 200


@app.route('/cliente/activar-desactivar/<documento>', methods=['PUT'])
@login_required
@propietario_admin_permission.require(http_exception=403)
def activar_desactivar_cliente(documento):
    """
    Activa o desactiva un cliente.

    :param documento: Documento del cliente.
    :return: Respuesta JSON.
    """
    cliente = Cliente.query.filter_by(documento=documento).first()
    if not cliente:
        return jsonify({'status': 'error', 'message': 'Cliente no encontrado'}), 404

    cliente.activo = not cliente.activo

    db.session.commit()

    estado = 'activado' if cliente.activo else 'desactivado'
    return jsonify({'status': 'success', 'message': f'Cliente {estado} exitosamente'}), 200


@app.route('/vehiculo/<string:placa>/cliente', methods=['GET'])
@login_required
@todos_permiso.require(http_exception=403)
def buscar_cliente_por_placa(placa):
    """
    Busca un cliente por placa de vehículo.

    :param placa: Placa del vehículo.
    :return: Respuesta JSON.
    """
    vehiculo = Vehiculo.query.filter_by(placa=placa).first()
    if not vehiculo:
        return jsonify({'status': 'error', 'message': 'Vehículo no encontrado'}), 404

    cliente = vehiculo.cliente
    if not cliente:
        return jsonify({'status': 'error', 'message': 'Cliente no encontrado'}), 404

    return jsonify({
        'status': 'success',
        'data': {
            'documento': cliente.documento,
            'nombres': cliente.nombres,
            'apellidos': cliente.apellidos,
            'email': cliente.email,
            'telefono': cliente.telefono,
            'direccion': cliente.direccion,
            'activo': cliente.activo
        }
    })


@app.route('/vehiculo/<string:placa>', methods=['PUT'])
@login_required
@todos_permiso.require(http_exception=403)
def editar_vehiculo(placa):
    """
    Edita un vehículo.

    :param placa: Placa del vehículo.
    :return: Respuesta JSON.
    """
    data = request.get_json()
    vehiculo = Vehiculo.query.filter_by(placa=placa).first()
    if not vehiculo:
        return jsonify({'status': 'error', 'message': 'Vehículo no encontrado'}), 404

    vehiculo.marca = data.get('marca')
    vehiculo.modelo = data.get('modelo')
    vehiculo.vehiculo_tipo_id = data.get('vehiculoTipoId')

    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Vehículo editado exitosamente'}), 200


@app.route('/generar_ticket/<string:placa>', methods=['GET'])
def generar_ticket(placa):
    """
    Genera un ticket de parqueadero.
    """
    
    parqueadero = Parqueadero.query.filter_by(usuario_id=current_user.parqueadero_id).first()
    vehiculo = Vehiculo.query.filter_by(placa=placa).first()

    tarifa = vehiculo.tarifa
    tarifa_costo = tarifa.costo
    tarifa_unidad_tiempo = tarifa.tarifa_tipo.nombre

    nombre_parqueadero = parqueadero.nombre
    registro_comercial = f'Registro comercial: {parqueadero.rut}'
    costo_servicio = f'{tarifa_costo} por {tarifa_unidad_tiempo}'
    nombre_atendedor = f'{current_user.nombres} {current_user.apellidos}'
    condiciones_servicio = "Este servicio no se hace responsable por objetos dejados dentro del vehículo."

    ticket_width = 8 * cm
    ticket_height = 12 * cm

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=(ticket_width, ticket_height))
    ancho, alto = ticket_width, ticket_height

    logo_path = os.path.join('app', 'static', 'images', 'logo-generico.png')
    c.drawImage(logo_path, (ancho - 64) / 2, alto - 64, width=64, height=64, mask='auto')

    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(ancho / 2, alto - 85, nombre_parqueadero)

    c.setFont("Helvetica", 9)
    y_position = alto - 100
    line_spacing = 12

    c.drawString(0.5 * cm, y_position, f"Registro Comercial: {registro_comercial}")
    y_position -= line_spacing
    c.drawString(0.5 * cm, y_position, f"Fecha/Hora de Ingreso: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y_position -= line_spacing
    c.drawString(0.5 * cm, y_position, f"Placa del Vehículo: {placa}")

    y_position -= line_spacing * 1.5
    c.setFont("Helvetica-Bold", 9)
    c.drawString(0.5 * cm, y_position, "Detalles del Servicio")
    y_position -= line_spacing
    c.setFont("Helvetica", 9)
    c.drawString(0.5 * cm, y_position, f"Costo: ${costo_servicio}")
    y_position -= line_spacing
    c.drawString(0.5 * cm, y_position, f"Atendido por: {nombre_atendedor}")

    qr_data = f"""
    Nombre del Parqueadero: {nombre_parqueadero}
    Registro Comercial: {registro_comercial}
    Fecha/Hora de Ingreso: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Placa del Vehículo: {placa}
    Costo por unidad de tiempo: $ {costo_servicio}
    Atendido por: {nombre_atendedor}
    Condiciones: {condiciones_servicio}
    """
    qr = qrcode.make(qr_data)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_qr_file:
        qr.save(temp_qr_file.name)
        qr_path = temp_qr_file.name

    c.drawImage(qr_path, ancho - 2.5 * cm, alto - 11.5 * cm, width=2 * cm, height=2 * cm)

    # Condiciones del servicio
    y_position -= line_spacing * 2
    c.setFont("Helvetica-Bold", 9)
    c.drawString(0.5 * cm, y_position, "Condiciones del Servicio:")
    y_position -= line_spacing

    styles = getSampleStyleSheet()
    style = styles['Normal']
    style.fontName = 'Helvetica'
    style.fontSize = 7
    style.leading = 10

    paragraph = Paragraph(condiciones_servicio, style)

    width, height = paragraph.wrap(ticket_width - 20, 0)

    c.setFont("Helvetica", 7)
    text = c.beginText(0.5 * cm, y_position)
    text.setTextOrigin(0.5 * cm, y_position)
    text.setLeading(10)
    text.setFont("Helvetica", 7)

    paragraph.drawOn(c, 0.5 * cm, y_position - height)

    c.showPage()
    c.save()

    pdf_buffer.seek(0)
    os.remove(qr_path)

    fecha_hora = datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre_archivo = f"ticket_parqueadero_{fecha_hora}.pdf"

    return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=nombre_archivo)
