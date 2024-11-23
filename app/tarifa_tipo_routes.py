from flask import Blueprint, g, jsonify, render_template, request
from flask_login import login_required

from app.models import TarifaTipo

from app import db
from app.routes import propietario_admin_permission
from app.routes import todos_permiso


class TarifaTipoRoutes:
    """
    Clase que gestiona las rutas de los tipos de tarifa.
    """
    def __init__(self):
        """
        Constructor de la clase.
        """
        self.blueprint = Blueprint('tarifa_tipo', __name__)
        self.add_routes()

    def add_routes(self):
        """
        Agrega las rutas de los tipos de tarifa.
        """
        @self.blueprint.route("/tarifa-tipo", methods=['GET'])
        @login_required
        @todos_permiso.require(http_exception=403)
        def tarifa_tipo():
            """
            Muestra la lista de tipos de tarifa.
            """
            g.template_name = 'base.html'
            
            entidades = TarifaTipo.query.all()
            return render_template("tarifa-tipo.html", titulo='Tipo de Tarifa', entidades=entidades)

        @self.blueprint.route('/tarifa-tipo', methods=['POST'])
        @login_required
        @propietario_admin_permission.require(http_exception=403)
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


        @self.blueprint.route('/tarifa-tipo/<int:id>', methods=['PUT'])
        @login_required
        @propietario_admin_permission.require(http_exception=403)
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


        @self.blueprint.route('/tarifa-tipo/<int:id>', methods=['DELETE'])
        @login_required
        @propietario_admin_permission.require(http_exception=403)
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
    