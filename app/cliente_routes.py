from flask import Blueprint, g, jsonify, render_template, request
from flask_login import current_user, login_required

from app.models import Cliente, Vehiculo, VehiculoTipo

from app import db
from app.routes import propietario_admin_permission
from app.routes import todos_permiso


class ClienteRoutes:
    """
    Clase que gestiona las rutas de los clientes.
    """
    def __init__(self):
        """
        Constructor de la clase.
        """
        self.blueprint = Blueprint('cliente', __name__)
        self.add_routes()

    def add_routes(self):
        @self.blueprint.route("/cliente", methods=['GET'])
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


        @self.blueprint.route('/cliente', methods=['POST'])
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


        @self.blueprint.route('/cliente/<string:documento>', methods=['PUT'])
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


        @self.blueprint.route('/cliente/<string:documento>', methods=['DELETE'])
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
            
        @self.blueprint.route('/cliente/<string:documento>/puntos', methods=['GET'])
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

        @self.blueprint.route('/cliente/activar-desactivar/<documento>', methods=['PUT'])
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
