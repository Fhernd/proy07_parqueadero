from flask import Blueprint, g, jsonify, render_template, request
from flask_login import login_required

from app.models import MedioPago, Tarifa

from app import db
from app.routes import propietario_admin_permission
from app.routes import todos_permiso


class MedioPagoRoutes:
    """
    Clase que gestiona las rutas de los medios de pago.
    """
    def __init__(self):
        """
        Constructor de la clase.
        """
        self.blueprint = Blueprint('medio_pago', __name__)
        self.add_routes()

    def add_routes(self):
        @self.blueprint.route("/medio-pago", methods=['GET'])
        @login_required
        @propietario_admin_permission.require(http_exception=403)
        def medio_pago():
            """
            Muestra la lista de tipos de tarifa.
            """
            g.template_name = 'base.html'
            
            entidades = MedioPago.query.all()
            return render_template('medio-pago.html', titulo='Medios de Pago', entidades=entidades)


        @self.blueprint.route("/medios-pago", methods=['GET'])
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


        @self.blueprint.route('/medio-pago', methods=['POST'])
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
                    'nombre': entidad.nombre,
                    'activo': entidad.activo
                }}), 201

            except Exception as e:
                db.session.rollback()
                return jsonify({'status': 'error', 'message': str(e)}), 500


        @self.blueprint.route('/medio-pago/<int:id>', methods=['PUT'])
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


        @self.blueprint.route('/medio-pago/<int:id>', methods=['DELETE'])
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

        @self.blueprint.route('/medio-pago/<int:medioPagoId>/activar-desactivar', methods=['PUT'])
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

        @self.blueprint.route("/tarifas", methods=['GET'])
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
