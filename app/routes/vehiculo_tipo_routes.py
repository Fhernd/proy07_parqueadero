from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required

from app.models import VehiculoTipo
from app.models import Tarifa

from app import app, db
from app.routes import propietario_admin_permission
from app.models import VehiculoTipo


class VehiculoTipoRoutes:
    def __init__(self):
        self.blueprint = Blueprint('vehicle', __name__)
        self.add_routes()

    def add_routes(self):
        @self.blueprint.route("/vehiculo-tipo", methods=['GET'])
        @login_required
        @propietario_admin_permission.require(http_exception=403)
        def vehiculo_tipo():
            """
            Muestra la lista de tipos de vehículo.
            """
            g.template_name = 'base.html'
            
            tipos_vehiculo = VehiculoTipo.query.all()
            tarifas = Tarifa.query.all()
            return render_template("vehiculo-tipo.html", titulo='Tipo de Vehículo', tipos_vehiculo=tipos_vehiculo, tarifas=tarifas)

        @self.blueprint.route('/vehiculo-tipo/<int:id>', methods=['DELETE'])
        @login_required
        @propietario_admin_permission.require(http_exception=403)
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


        @self.blueprint.route('/vehiculo-tipo', methods=['POST'])
        @login_required
        @propietario_admin_permission.require(http_exception=403)
        def vehiculo_tipo_crear():
            try:
                data = request.get_json()
                vehiculo_tipo = VehiculoTipo(nombre=data.get('nombre'), tarifa_id=data.get('tarifaId'))

                db.session.add(vehiculo_tipo)
                db.session.commit()

                tarifa = Tarifa.query.get(data.get('tarifaId'))

                return jsonify({'status': 'success', 'message': 'Tipo de vehículo creado', 'data': {
                    'id': vehiculo_tipo.id,
                    'nombre': vehiculo_tipo.nombre,
                    'tarifa': {
                        'id': tarifa.id,
                        'nombre': tarifa.nombre,
                        'costo': tarifa.costo
                    }
                }}), 201

            except Exception as e:
                db.session.rollback()
                return jsonify({'status': 'error', 'message': str(e)}), 500


        @self.blueprint.route('/vehiculo-tipo/<int:id>', methods=['PUT'])
        @login_required
        @propietario_admin_permission.require(http_exception=403)
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
