from flask import Blueprint, g, jsonify, request
from flask_login import login_required

from app.models import Cliente, Vehiculo

from app import db
from app.routes import todos_permiso


class ClienteVehiculoRoutes:
    """
    Clase que gestiona las rutas de los vehículos de los clientes.
    """
    def __init__(self):
        """
        Constructor de la clase.
        """
        self.blueprint = Blueprint('cliente_vehiculo', __name__)
        self.add_routes()

    def add_routes(self):
        @self.blueprint.route('/cliente/<string:documento>/vehiculos', methods=['GET'])
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


        @self.blueprint.route('/cliente/crear-vehiculo', methods=['POST'])
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


        @self.blueprint.route('/cliente/editar-vehiculo/<int:vehiculo_id>', methods=['PUT'])
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


        @self.blueprint.route('/cliente/vehiculo/<int:vehiculo_id>/cambiar-disponibilidad', methods=['DELETE'])
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


        @self.blueprint.route('/cliente/vehiculo/<int:vehiculo_id>/arrendamientos', methods=['GET'])
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
