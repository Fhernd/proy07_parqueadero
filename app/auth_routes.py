from flask import Blueprint, g, jsonify, render_template, request
from flask_login import login_required
from werkzeug.security import generate_password_hash

from app.models import Pais, Usuario

from app import db
from app.routes import propietario_admin_permission
from app.routes import todos_permiso


class AuthRoutes:
    """
    Clase que gestiona las rutas de autenticación.
    """
    def __init__(self):
        """
        Constructor de la clase.
        """
        self.blueprint = Blueprint('auth', __name__)
        self.add_routes()

    def add_routes(self):
        @self.blueprint.route("/registro", methods=['GET'])
        @propietario_admin_permission.require(http_exception=403)
        def registro():
            """
            Muestra la ruta para el registro de un administrador para el parqueadero.
            """
            g.template_name = 'base.html'
            
            paises = Pais.query.all()
            return render_template('registro.html', titulo='Registro', paises=paises)


        @self.blueprint.route('/registro', methods=['POST'])
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
