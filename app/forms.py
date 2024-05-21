from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import Usuario


class UsuarioForm(FlaskForm):
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


class CambiarClaveForm(FlaskForm):
    """
    Formulario para cambiar la clave de un usuario.
    """
    clave_actual = PasswordField('Clave actual', validators=[DataRequired()])
    clave_nueva = PasswordField('Clave nueva', validators=[DataRequired()])
    confirmar_clave = PasswordField('Confirmar clave nueva', validators=[DataRequired(), EqualTo('clave_nueva')])
    submit = SubmitField('Cambiar clave')
