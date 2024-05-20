from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import Usuario


class UsuarioForm(FlaskForm):
    documento = StringField('Documento', validators=[DataRequired(), Length(max=16)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(max=256)])
    nombres = StringField('Nombres', validators=[DataRequired(), Length(max=32)])
    apellidos = StringField('Apellidos', validators=[DataRequired(), Length(max=32)])
    telefono = StringField('Teléfono', validators=[DataRequired(), Length(max=16)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=64)])
    rol_id = IntegerField('ID del Rol', validators=[DataRequired()])
    es_propietario = BooleanField('Es Propietario')
    
    submit = SubmitField('Registrar')

    def validate_documento(self, documento):
        user = Usuario.query.filter_by(documento=documento.data).first()
        if user:
            raise ValidationError('El documento ya está registrado. Por favor, usa uno diferente.')

    def validate_email(self, email):
        user = Usuario.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('El email ya está registrado. Por favor, usa uno diferente.')
