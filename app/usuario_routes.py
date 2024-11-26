from flask import Blueprint, g, jsonify, render_template, request
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash

from app.models import Parqueadero, Rol, Sede, SedeUsuario, Usuario

from app import db
from app.routes import propietario_admin_permission, usuario_rol
from app.routes import todos_permiso


class UsuarioRoutes:
    """
    Clase que gestiona las rutas de los usuarios.
    """
    def __init__(self):
        """
        Constructor de la clase.
        """
        self.blueprint = Blueprint('usuario', __name__)
        self.add_routes()

    def add_routes(self):
        @self.blueprint.route("/usuario", methods=['GET'])
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


        @self.blueprint.route('/usuario', methods=['POST'])
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
                print('error crear usuario', e)
                db.session.rollback()
                return jsonify({'status': 'error', 'message': str(e)}), 500


        @self.blueprint.route('/usuario/<string:documento>', methods=['PUT'])
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


        @self.blueprint.route('/usuario/<string:documento>', methods=['DELETE'])
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


        @self.blueprint.route('/usuario/cambiar-password', methods=['PUT'])
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


        @self.blueprint.route('/usuario/<string:documento>', methods=['GET'])
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
