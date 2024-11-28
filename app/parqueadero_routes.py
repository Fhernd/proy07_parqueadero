from flask import Blueprint, g, flash, jsonify, render_template, request, url_for, redirect
from flask_login import current_user, login_required

from app.forms import ParqueaderoInformacionForm
from app.models import Parqueadero

from app import db
from app.routes import propietario_admin_permission
from app.routes import todos_permiso, propietario_permission


class ParqueaderoRoutes:
    """
    Clase que gestiona las rutas de los parqueaderos.
    """
    def __init__(self):
        """
        Constructor de la clase.
        """
        self.blueprint = Blueprint('parqueadero', __name__)
        self.add_routes()

    def add_routes(self):
        @self.blueprint.route("/parqueadero", methods=['POST'])
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


        @self.blueprint.route('/parqueadero-informacion', methods=['GET', 'POST'])
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
