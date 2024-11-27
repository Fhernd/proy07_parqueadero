from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import login_required

from app.models import Arrendamiento

from app import db
from app.routes import todos_permiso


class ClienteVehiculoArrendamientoRoutes:
    """
    Clase que gestiona las rutas de los vehículos de los clientes.
    """
    def __init__(self):
        """
        Constructor de la clase.
        """
        self.blueprint = Blueprint('cliente_vehiculo_arrendamiento', __name__)
        self.add_routes()

    def add_routes(self):
        @self.blueprint.route('/cliente/vehiculo/arrendamiento', methods=['POST'])
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
            

        @self.blueprint.route('/cliente/vehiculo/arrendamiento/<int:id>', methods=['PUT'])
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


        @self.blueprint.route('/cliente/vehiculo/arrendamiento/<int:id>', methods=['DELETE'])
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
