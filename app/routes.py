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

from app.cliente_vehiculo_routes import ClienteVehiculoRoutes
from app.cliente_vehiculo_arrendamiento_routes import ClienteVehiculoArrendamientoRoutes
from app.vehiculo_tipo_routes import VehiculoTipoRoutes
from app.tarifa_tipo_routes import TarifaTipoRoutes
from app.medio_pago_routes import MedioPagoRoutes
from app.cliente_routes import ClienteRoutes
from app.sede_routes import SedeRoutes
from app.usuario_routes import UsuarioRoutes

app.register_blueprint(ClienteRoutes().blueprint)
app.register_blueprint(ClienteVehiculoRoutes().blueprint)
app.register_blueprint(ClienteVehiculoArrendamientoRoutes().blueprint)
app.register_blueprint(MedioPagoRoutes().blueprint)
app.register_blueprint(SedeRoutes().blueprint)
app.register_blueprint(TarifaTipoRoutes().blueprint)
app.register_blueprint(UsuarioRoutes().blueprint)
app.register_blueprint(VehiculoTipoRoutes().blueprint)


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
