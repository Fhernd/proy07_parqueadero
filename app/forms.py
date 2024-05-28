from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import Usuario


class CustomFlaskForm(FlaskForm):
    """
    Clase base para los formularios de la aplicación.
    """
    def hidden_tag(self, *fields):
        from markupsafe import Markup
        fields = fields or self._fields
        hidden_fields = [f for f in fields if self._fields[f].type == 'HiddenField' and f != 'csrf_token']
        csrf_token = '<input id="csrf_token_{}" name="csrf_token" type="hidden" value="{}">'.format(self.__class__.__name__, self.csrf_token.current_token)
        return Markup(''.join(str(self._fields[f]) for f in hidden_fields) + csrf_token)


class UsuarioForm(CustomFlaskForm):
    documento = StringField('Documento')
    nombres = StringField('Nombres', validators=[DataRequired(), Length(max=32)])
    apellidos = StringField('Apellidos', validators=[DataRequired(), Length(max=32)])
    telefono = StringField('Teléfono', validators=[DataRequired(), Length(max=16)])
    email = StringField('Email')
    rol = StringField('Rol')
    es_propietario = BooleanField('Es Propietario')
    
    submit = SubmitField('Registrar')

    def validate_documento(self, documento):
        if documento.data != current_user.documento:
            user = Usuario.query.filter_by(documento=documento.data).first()
            if user:
                raise ValidationError('El documento ya está registrado. Por favor, usa uno diferente.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = Usuario.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('El email ya está registrado. Por favor, usa uno diferente.')


class CambiarClaveForm(CustomFlaskForm):
    """
    Formulario para cambiar la clave de un usuario.
    """
    clave_actual = PasswordField('Clave actual', validators=[DataRequired()])
    clave_nueva = PasswordField('Clave nueva', validators=[DataRequired()])
    confirmar_clave = PasswordField('Confirmar clave nueva', validators=[DataRequired(), EqualTo('clave_nueva', message='Las contraseñas no coinciden.')])
    submit = SubmitField('Cambiar clave')


class ParqueaderoInformacionForm(CustomFlaskForm):
    """
    Formulario para actualizar la información de un parqueadero.
    """
    id = IntegerField('ID')
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=64)])
    direccion = StringField('Dirección', validators=[DataRequired(), Length(max=128)])
    telefono = StringField('Teléfono', validators=[DataRequired(), Length(max=16)])
    email = StringField('Email', validators=[DataRequired(), Email(message='Dirección de correo inválida.')])
    ciudad = StringField('Ciudad', validators=[DataRequired(), Length(max=32)])
    submit = SubmitField('Actualizar')
