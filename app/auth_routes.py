from flask import Blueprint, g, jsonify, render_template, request, current_app, redirect, url_for, flash
from flask_login import current_user, login_required, login_user, logout_user
from flask_principal import Identity, AnonymousIdentity
from werkzeug.security import generate_password_hash

from app.forms import CambiarClaveForm, UsuarioForm
from app.models import Pais, Rol, Usuario

from app import db
from app.routes import identity_changed, propietario_admin_permission, propietario_permission, todos_permiso
from app.routes import tiene_rol
from app.util.roles_enum import Roles


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
        
        @self.blueprint.route("/login", methods=['GET'])
        def login():
            """
            Muestra la página de inicio de sesión.

            :return: Plantilla HTML.
            """
            return render_template('login.html', titulo='Iniciar Sesión')


        @self.blueprint.route("/login", methods=['POST'])
        def login_post():
            """
            Inicia sesión en la aplicación.

            :return: Redirección a la página de inicio.
            """
            if current_user.is_authenticated:
                identity_changed.send(current_app._get_current_object(), identity=Identity(current_user.id))
                return jsonify({"success": True, "redirect_url": url_for('dashboard')})
            
            data = request.get_json()
            email = data.get('email')

            usuario = Usuario.query.filter_by(email=email).first()

            if usuario is None or not usuario.check_password(data.get('password')) or not usuario.activo:
                return jsonify({"success": False, "message": "Credenciales inválidas"}), 401

            login_user(usuario)
            identity_changed.send(current_app._get_current_object(), identity=Identity(usuario.id))

            next = request.args.get('next')

            if not next:
                roles = [rol.nombre for rol in usuario.roles]
                if tiene_rol(current_user.roles, [Roles.OPERARIO.value]):
                    return jsonify({"success": True, "redirect_url": url_for('parqueadero.parqueos')})
                else:
                    return jsonify({"success": True, "redirect_url": url_for('dashboard')})
            else:
                return jsonify({"success": True, "redirect_url": next})


        @self.blueprint.route("/logout", methods=['GET'])
        @login_required
        def logout():
            """
            Cierra sesión en la aplicación.

            :return: Redirección a la página de inicio.
            """
            logout_user()
            identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())

            return redirect(url_for('auth.login'))

        @self.blueprint.route("/rol", methods=['GET'])
        @login_required
        @propietario_permission.require(http_exception=403)
        def rol():
            """
            Muestra la lista de roles.
            """
            g.template_name = 'base.html'
            
            entidades = Rol.query.all()
            return render_template('rol.html', titulo='Roles', entidades=entidades)

        @self.blueprint.route('/perfil', methods=['GET', 'POST'])
        @login_required
        @todos_permiso.require(http_exception=403)
        def perfil():
            """
            Muestra el perfil del usuario.

            :return: Plantilla HTML.
            """
            g.template_name = 'base.html'
            
            form = UsuarioForm()
            cambiar_clave_form = CambiarClaveForm()

            if form.submit.data and form.validate_on_submit():
                current_user.documento = form.documento.data
                current_user.nombres = form.nombres.data
                current_user.apellidos = form.apellidos.data
                current_user.telefono = form.telefono.data

                db.session.commit()
                flash('Perfil actualizado correctamente.', 'perfil-success')
                return redirect(url_for('auth.perfil'))

            if cambiar_clave_form.submit.data and cambiar_clave_form.validate_on_submit():
                clave_actual = cambiar_clave_form.clave_actual.data

                if not current_user.check_password(clave_actual):
                    flash('La contraseña actual es incorrecta', 'cambio-clave-danger')
                else:
                    current_user.set_password(cambiar_clave_form.clave_nueva.data)
                    db.session.commit()
                    flash('Contraseña cambiada correctamente.', 'cambio-clave-success')
                    return redirect(url_for('auth.perfil'))

            return render_template('perfil.html', titulo='Perfil', form=form, cambiar_clave_form=cambiar_clave_form)
