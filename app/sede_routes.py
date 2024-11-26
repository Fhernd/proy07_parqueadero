from flask import Blueprint, g, jsonify, render_template, request
from flask_login import current_user, login_required

from app.models import Modulo, Parqueadero, Parqueo, Sede, SedeUsuario, Usuario

from app import db
from app.routes import propietario_admin_permission, usuario_rol
from app.routes import todos_permiso


class SedeRoutes:
    """
    Clase que gestiona las rutas de las sedes.
    """
    def __init__(self):
        """
        Constructor de la clase.
        """
        self.blueprint = Blueprint('sede', __name__)
        self.add_routes()

    def add_routes(self):
        @self.blueprint.route('/sedes', methods=['GET'])
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


        @self.blueprint.route('/sede', methods=['POST'])
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


        @self.blueprint.route('/sede/<int:id>', methods=['PUT'])
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


        @self.blueprint.route('/sede/<int:id>', methods=['DELETE'])
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


        @self.blueprint.route('/sede/<int:id>/modulos', methods=['GET'])
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


        @self.blueprint.route('/sede/<int:id>/modulo', methods=['POST'])
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


        @self.blueprint.route('/sede/<int:id>/modulo/<int:modulo_id>', methods=['PUT'])
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


        @self.blueprint.route('/sede/<int:id>/modulo/<int:modulo_id>', methods=['DELETE'])
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


        @self.blueprint.route('/sede/asignar-usuario', methods=['POST'])
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


        @self.blueprint.route('/sede/sede-asignada/<int:documento>', methods=['GET'])
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
