from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import event
from werkzeug.security import check_password_hash, generate_password_hash
from flask_principal import Principal, Permission, RoleNeed, UserNeed, Identity, AnonymousIdentity, identity_loaded, identity_changed

from app import login

from app import app, db

from flask_login import current_user



class SedeUsuario(db.Model):
    __tablename__ = 'sede_usuario'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sede_id = db.Column(db.Integer, db.ForeignKey('sede.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    habilitado = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    sede = db.relationship('Sede', back_populates='usuarios')
    usuario = db.relationship('Usuario', back_populates='sedes')

    def __repr__(self):
        return f"<SedeUsuario(sede_id='{self.sede_id}', usuario_id='{self.usuario_id}')>"


class Sede(db.Model):
    """
    Representa una sede.
    """
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(16), nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    parqueadero_id = db.Column(db.Integer, db.ForeignKey('parqueadero.id'), nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    parqueadero = db.relationship("Parqueadero", back_populates="sedes")
    modulos = db.relationship("Modulo", back_populates="sede")
    usuarios = db.relationship('SedeUsuario', back_populates='sede')

    def __repr__(self):
        return f'<Sede {self.nombre}>'


class Parqueadero(db.Model):
    """
    Representa un parqueadero.
    """
    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(32), unique=True, nullable=False)
    nombre = db.Column(db.String(64), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    ciudad = db.Column(db.String(64), nullable=False)
    telefono = db.Column(db.String(16), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    pais_id = db.Column(db.Integer, db.ForeignKey('pais.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    clientes = db.relationship("Cliente", back_populates="parqueadero")
    periodicidades = db.relationship("Periodicidad", back_populates="parqueadero")
    sedes = db.relationship("Sede", back_populates="parqueadero")

    def __repr__(self):
        return f'<Parqueadero {self.rut}>'


class Pais(db.Model):
    """
    Representa un país.
    """
    __tablename__ = 'pais'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    def __repr__(self):
        return f"<Pais(nombre='{self.nombre}')>"


usuario_rol = db.Table('usuario_rol',
    db.Column('id', db.Integer, primary_key=True, autoincrement=True),
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id')),
    db.Column('rol_id', db.Integer, db.ForeignKey('rol.id')),
    db.Column('created_at', db.DateTime, default=db.func.current_timestamp()),
    db.Column('updated_at', db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
)


class Usuario(UserMixin, db.Model):
    """
    Representa un usuario.
    """
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    documento = db.Column(db.String(16), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    nombres = db.Column(db.String(32), nullable=False)
    apellidos = db.Column(db.String(32), nullable=False)
    telefono = db.Column(db.String(16), nullable=False)
    email = db.Column(db.String(64), nullable=False)

    parqueadero_id = db.Column(db.Integer, db.ForeignKey('parqueadero.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    roles = db.relationship('Rol', secondary=usuario_rol, lazy='subquery',
                            backref=db.backref('usuarios', lazy=True))
    sedes = db.relationship('SedeUsuario', back_populates='usuario')

    def __repr__(self):
        return f"<Usuario(documento='{self.documento}', nombres='{self.nombres}', apellidos='{self.apellidos}')>"
    
    def set_password(self, password):
        """
        Establece la contraseña del usuario.

        :param password: Contraseña del usuario.
        """
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Verifica si la contraseña ingresada es correcta.

        :param password: Contraseña a verificar.
        :return: True si la contraseña es correcta, False en caso contrario.
        """
        return check_password_hash(self.password, password)
    
    def es_propietario(self):
        """
        Verifica si el usuario tiene el rol de propietario.

        :return: True si el usuario es propietario, False en caso contrario.
        """
        for role in self.roles:
            if role.nombre == 'Propietario':
                return True
        return False


@login.user_loader
def load_user(id):
    """
    Carga un usuario por su ID.

    :param id: ID del usuario.
    :return: Usuario con el ID especificado.
    """
    return Usuario.query.get(int(id))


class Cliente(db.Model):
    """
    Representa un cliente.
    """
    __tablename__ = 'cliente'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    documento = db.Column(db.String(16), nullable=False, unique=True)
    nombres = db.Column(db.String(32), nullable=False)
    apellidos = db.Column(db.String(32), nullable=False)
    telefono = db.Column(db.String(16), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)
    parqueadero_id = db.Column(db.Integer, db.ForeignKey('parqueadero.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    parqueadero = db.relationship("Parqueadero", back_populates="clientes")
    puntos = db.relationship("Punto", back_populates="cliente")
    vehiculos = db.relationship('Vehiculo', back_populates='cliente')

    def __repr__(self):
        return f"<Cliente(documento='{self.documento}', nombres='{self.nombres}', apellidos='{self.apellidos}')>"


class Rol(db.Model):
    """
    Representa un rol en el sistema.
    """
    __tablename__ = 'rol'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    def __repr__(self):
        return f"<Rol(nombre='{self.nombre}')>"


class Periodicidad(db.Model):
    """
    Representa la periodicidad de ciertos eventos o pagos en el sistema.
    """
    __tablename__ = 'periodicidad'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(64), nullable=False)
    dias = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    parqueadero_id = db.Column(db.Integer, db.ForeignKey('parqueadero.id'), nullable=False)

    parqueadero = db.relationship("Parqueadero", back_populates="periodicidades")
    arrendamientos = db.relationship("Arrendamiento", back_populates="periodicidad")

    def __repr__(self):
        return f"<Periodicidad(nombre='{self.nombre}', dias={self.dias})>"


class Redimir(db.Model):
    """
    Representa la acción de redimir puntos acumulados.
    """
    __tablename__ = 'redimir'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cantidad = db.Column(db.Integer, nullable=False)
    puntos_id = db.Column(db.Integer, db.ForeignKey('punto.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    punto = db.relationship("Punto", back_populates="redimidos")

    def __repr__(self):
        return f"<Redimir(cantidad={self.cantidad})>"


class Punto(db.Model):
    """
    Representa los puntos acumulados por un cliente.
    """
    __tablename__ = 'punto'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cantidad = db.Column(db.Integer, default=0, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    cliente = db.relationship("Cliente", back_populates="puntos")
    redimidos = db.relationship("Redimir", back_populates="punto")

    def __repr__(self):
        return f"<Punto(id={self.id}, cantidad={self.cantidad})>"


class Modulo(db.Model):
    __tablename__ = 'modulo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(32), nullable=False)
    habilitado = db.Column(db.Boolean, default=True, nullable=False)
    descripcion = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    sede_id = db.Column(db.Integer, db.ForeignKey('sede.id'), nullable=False)
    
    sede = db.relationship("Sede", back_populates="modulos")
    parqueos = db.relationship('Parqueo', back_populates='modulo')

    def __repr__(self):
        return f"<Modulo(id={self.id}, nombre='{self.nombre}', habilitado={self.habilitado})>"


class TarifaTipo(db.Model):
    __tablename__ = 'tarifa_tipo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(64), nullable=False)
    unidad = db.Column(db.SmallInteger, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    tarifas = db.relationship('Tarifa', back_populates='tarifa_tipo')

    def __repr__(self):
        return f"<TarifaTipo(id={self.id}, nombre='{self.nombre}', unidad={self.unidad})>"


class Tarifa(db.Model):
    __tablename__ = 'tarifa'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(128), nullable=False)
    costo = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    tarifa_tipo_id = db.Column(db.Integer, db.ForeignKey('tarifa_tipo.id'), nullable=False)
    
    tarifa_tipo = db.relationship("TarifaTipo", back_populates="tarifas")
    vehiculo_tipos = db.relationship("VehiculoTipo", back_populates="tarifa")
    arrendamientos = db.relationship("Arrendamiento", back_populates="tarifa")

    def __repr__(self):
        return f"<Tarifa(id={self.id}, nombre='{self.nombre}', costo={self.costo})>"


class Parqueo(db.Model):
    __tablename__ = 'parqueo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_hora_entrada = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    fecha_hora_salida = db.Column(db.DateTime)
    total_pagado = db.Column(db.Integer, default=0, nullable=False)
    modulo_id = db.Column(db.Integer, db.ForeignKey('modulo.id'), nullable=False)
    vehiculo_id = db.Column(db.String(12), db.ForeignKey('vehiculo.id'), nullable=False)
    medio_pago_id = db.Column(db.Integer, db.ForeignKey('medio_pago.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    
    modulo = db.relationship("Modulo", back_populates="parqueos")
    vehiculo = db.relationship("Vehiculo", back_populates="parqueos")
    medio_pago = db.relationship("MedioPago", back_populates="parqueos")

    def __repr__(self):
        return f"<Parqueo(id={self.id}, fecha_hora_entrada='{self.fecha_hora_entrada}', fecha_hora_salida='{self.fecha_hora_salida}')>"


class VehiculoTipo(db.Model):
    __tablename__ = 'vehiculo_tipo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(32), nullable=False)
    tarifa_id = db.Column(db.Integer, db.ForeignKey('tarifa.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    vehiculos = db.relationship("Vehiculo", back_populates="vehiculo_tipo")
    tarifa = db.relationship("Tarifa", back_populates="vehiculo_tipos")

    def __repr__(self):
        return f"<VehiculoTipo(id={self.id}, nombre='{self.nombre}')>"


class Vehiculo(db.Model):
    __tablename__ = 'vehiculo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    placa = db.Column(db.String(12))
    disponible = db.Column(db.Boolean, nullable=False, default=True)
    marca = db.Column(db.String(32))
    modelo = db.Column(db.String(4))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    vehiculo_tipo_id = db.Column(db.Integer, db.ForeignKey('vehiculo_tipo.id'), nullable=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=True)

    parqueos = db.relationship('Parqueo', back_populates='vehiculo')
    cliente = db.relationship("Cliente", back_populates="vehiculos")
    vehiculo_tipo = db.relationship("VehiculoTipo", back_populates="vehiculos")
    arrendamientos = db.relationship("Arrendamiento", back_populates="vehiculo")

    def __repr__(self):
        return f"<Vehiculo(placa='{self.placa}', marca='{self.marca}', modelo='{self.modelo}')>"


class MedioPago(db.Model):
    __tablename__ = 'medio_pago'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    parqueos = db.relationship("Parqueo", back_populates="medio_pago")
    arrendamientos = db.relationship("Arrendamiento", back_populates="medio_pago")

    def __repr__(self):
        return f"<MedioPago(nombre='{self.nombre}')>"


class Arrendamiento(db.Model):
    __tablename__ = 'arrendamiento'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(256), nullable=True)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculo.id'), nullable=False)
    periodicidad_id = db.Column(db.Integer, db.ForeignKey('periodicidad.id'), nullable=False)
    medio_pago_id = db.Column(db.Integer, db.ForeignKey('medio_pago.id'), nullable=False)
    tarifa_id = db.Column(db.Integer, db.ForeignKey('tarifa.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    vehiculo = db.relationship('Vehiculo', back_populates='arrendamientos')
    periodicidad = db.relationship('Periodicidad', back_populates='arrendamientos')
    medio_pago = db.relationship('MedioPago', back_populates='arrendamientos')
    tarifa = db.relationship('Tarifa', back_populates='arrendamientos')

    def __repr__(self):
        return f"<Arrendamiento(id='{self.id}', descripcion='{self.descripcion}')>"


def insert_initial_values():
    if not MedioPago.query.first():
        medios_pago = [
            {'id': 1, 'nombre': 'Efectivo', 'created_at': datetime(2024, 4, 15), 'updated_at': datetime(2024, 4, 15)},
            {'id': 2, 'nombre': 'Tarjeta de crédito', 'created_at': datetime(2024, 4, 15), 'updated_at': datetime(2024, 4, 15)},
            {'id': 3, 'nombre': 'Tarjeta débito', 'created_at': datetime(2024, 4, 15), 'updated_at': datetime(2024, 4, 15)},
            {'id': 4, 'nombre': 'Nequi', 'created_at': datetime(2024, 4, 15), 'updated_at': datetime(2024, 4, 15)},
            {'id': 5, 'nombre': 'DaviPlata', 'created_at': datetime(2024, 4, 15), 'updated_at': datetime(2024, 4, 15)},
            {'id': 6, 'nombre': 'Transferencia', 'created_at': datetime(2024, 4, 15), 'updated_at': datetime(2024, 4, 15)},
            {'id': 7, 'nombre': 'Otro', 'created_at': datetime(2024, 4, 15), 'updated_at': datetime(2024, 4, 15)}
        ]

        for medio in medios_pago:
            mp = MedioPago(**medio)
            db.session.add(mp)

        db.session.commit()

    if not Pais.query.first():
        paises = [
            {'nombre': 'Colombia', 'created_at': datetime(2024, 4, 15), 'updated_at': datetime(2024, 4, 15)},
            {'nombre': 'Argentina', 'created_at': datetime(2024, 4, 16, 23, 34, 17), 'updated_at': datetime(2024, 4, 16, 23, 34, 17)},
            {'nombre': 'Bolivia', 'created_at': datetime(2024, 4, 16, 23, 34, 17), 'updated_at': datetime(2024, 4, 16, 23, 34, 17)},
            {'nombre': 'Brasil', 'created_at': datetime(2024, 4, 16, 23, 34, 17), 'updated_at': datetime(2024, 4, 16, 23, 34, 17)},
            {'nombre': 'Chile', 'created_at': datetime(2024, 4, 16, 23, 34, 17), 'updated_at': datetime(2024, 4, 16, 23, 34, 17)},
            {'nombre': 'Costa Rica', 'created_at': datetime(2024, 4, 16, 23, 34, 17), 'updated_at': datetime(2024, 4, 16, 23, 34, 17)},
            {'nombre': 'Cuba', 'created_at': datetime(2024, 4, 16, 23, 34, 17), 'updated_at': datetime(2024, 4, 16, 23, 34, 17)},
            {'nombre': 'Ecuador', 'created_at': datetime(2024, 4, 16, 23, 34, 17), 'updated_at': datetime(2024, 4, 16, 23, 34, 17)},
            {'nombre': 'El Salvador', 'created_at': datetime(2024, 4, 16, 23, 34, 17), 'updated_at': datetime(2024, 4, 16, 23, 34, 17)},
            {'nombre': 'Guatemala', 'created_at': datetime(2024, 4, 16, 23, 34, 17), 'updated_at': datetime(2024, 4, 16, 23, 34, 17)},
            {'nombre': 'Honduras', 'created_at': datetime(2024, 4, 16, 23, 34, 17), 'updated_at': datetime(2024, 4, 16, 23, 34, 17)},
            {'nombre': 'México', 'created_at': datetime(2024, 4, 16, 23, 34, 17), 'updated_at': datetime(2024, 4, 16, 23, 34, 17)},
            {'nombre': 'Nicaragua', 'created_at': datetime(2024, 4, 16, 23, 34, 17), 'updated_at': datetime(2024, 4, 16, 23, 34, 17)},
            {'nombre': 'Panamá', 'created_at': datetime(2024, 4, 16, 23, 34, 17), 'updated_at': datetime(2024, 4, 16, 23, 34, 17)},
            {'nombre': 'Paraguay', 'created_at': datetime(2024, 4, 16, 23, 34, 17), 'updated_at': datetime(2024, 4, 16, 23, 34, 17)},
            {'nombre': 'Perú', 'created_at': datetime(2024, 4, 16, 23, 34, 17), 'updated_at': datetime(2024, 4, 16, 23, 34, 17)},
            {'nombre': 'Puerto Rico', 'created_at': datetime(2024, 4, 16, 23, 34, 17), 'updated_at': datetime(2024, 4, 16, 23, 34, 17)},
            {'nombre': 'República Dominicana', 'created_at': datetime(2024, 4, 16, 23, 34, 17), 'updated_at': datetime(2024, 4, 16, 23, 34, 17)},
            {'nombre': 'Uruguay', 'created_at': datetime(2024, 4, 16, 23, 34, 17), 'updated_at': datetime(2024, 4, 16, 23, 34, 17)},
            {'nombre': 'Venezuela', 'created_at': datetime(2024, 4, 16, 23, 34, 17), 'updated_at': datetime(2024, 4, 16, 23, 34, 17)},
            {'nombre': 'Canadá', 'created_at': datetime(2024, 4, 16, 23, 34, 17), 'updated_at': datetime(2024, 4, 16, 23, 34, 17)},
            {'nombre': 'Estados Unidos', 'created_at': datetime(2024, 4, 16, 23, 34, 17), 'updated_at': datetime(2024, 4, 16, 23, 34, 17)}
        ]

        for pais_info in paises:
            pais = Pais(**pais_info)
            db.session.add(pais)
        
        db.session.commit()

    if not Rol.query.first():
        roles = [
            Rol(id=1, nombre='Propietario', created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15)),
            Rol(id=2, nombre='Administrador', created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15)),
            Rol(id=3, nombre='Operario', created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15))
        ]

        for rol in roles:
            db.session.add(rol)

        db.session.commit()

    if not Usuario.query.first():
        usuarios = [
            Usuario(
                id=1,
                documento='2001',
                password='scrypt:32768:8:1$tokZ3wGBv3RBPtZm$4c1794f554745d39c482c0299cba11429cd1b2456ae3170980c3133416f686e61133de12d00e55dd90592c154f853828a3a3f7978c586bc72932d9cff0132912', # usuario123
                nombres='Pepé',
                apellidos='Pérez',
                telefono='3011001101',
                email='pepe.perez@superparking.co',
                parqueadero_id=1,
                created_at=datetime(2024, 4, 15),
                updated_at=datetime(2024, 4, 15)
            ),
            Usuario(
                id=2,
                documento='2002',
                password='scrypt:32768:8:1$tokZ3wGBv3RBPtZm$4c1794f554745d39c482c0299cba11429cd1b2456ae3170980c3133416f686e61133de12d00e55dd90592c154f853828a3a3f7978c586bc72932d9cff0132912', # usuario123
                nombres='Laura',
                apellidos='Gómez',
                telefono='3202020100',
                email='laura@superparking.co',
                parqueadero_id=1,
                created_at=datetime(2024, 4, 18),
                updated_at=datetime(2024, 4, 18)
            ),
            Usuario(
                id=3,
                documento='2003',
                password='scrypt:32768:8:1$wTvjmRz8VydEhUJP$079bf4fe8c6afb358c7b0a3497edc9db52c361ff4fe561a6be41a50b7d37f1d2f1689692e8fd343bae2cea0a0df4d50fb2881463f264aa0995a45e8162180e2d', # usuario123
                nombres='Bolívar',
                apellidos='Rosero',
                telefono='3011001102',
                email='bolivar.rosero@superparking.co',
                parqueadero_id=1,
                created_at=datetime(2024, 4, 15),
                updated_at=datetime(2024, 4, 15)
            ),
            Usuario(
                id=4,
                documento='2004',
                password='scrypt:32768:8:1$tokZ3wGBv3RBPtZm$4c1794f554745d39c482c0299cba11429cd1b2456ae3170980c3133416f686e61133de12d00e55dd90592c154f853828a3a3f7978c586bc72932d9cff0132912', # usuario123
                nombres='Patricia',
                apellidos='García',
                telefono='3202020111',
                email='patricia.garcia@parqueaderolosautos.co',
                parqueadero_id=2,
                created_at=datetime(2024, 4, 18),
                updated_at=datetime(2024, 4, 18)
            ),
        ]

        for usuario in usuarios:
            db.session.add(usuario)

    rol_propietario = Rol.query.filter_by(nombre='Propietario').first()
    rol_administrador = Rol.query.filter_by(nombre='Administrador').first()
    rol_operario = Rol.query.filter_by(nombre='Operario').first()

    usuario_pepe_perez = Usuario.query.filter_by(documento='2001').first()
    usuario_pepe_perez.roles.append(rol_propietario)
    db.session.add(usuario_pepe_perez)

    usuario_laura_gomez = Usuario.query.filter_by(documento='2002').first()
    usuario_laura_gomez.roles.append(rol_administrador)
    db.session.add(usuario_laura_gomez)

    usuario_bolivar_rosero = Usuario.query.filter_by(documento='2003').first()
    usuario_bolivar_rosero.roles.append(rol_operario)
    db.session.add(usuario_bolivar_rosero)

    usuario_patricia_garcia = Usuario.query.filter_by(documento='2004').first()
    usuario_patricia_garcia.roles.append(rol_propietario)
    db.session.add(usuario_patricia_garcia)

    if not Parqueadero.query.first():
        parqueaderos = [
            Parqueadero(
                id=1,
                rut='1001',
                nombre='SuperParking',
                direccion='Calle 1 # 3-45',
                telefono='3011001123',
                email='principal@superparking.co',
                ciudad='Bogotá',
                usuario_id=1,
                pais_id=1,
                created_at=datetime(2024, 4, 15),
                updated_at=datetime(2024, 4, 15)
            ),
            Parqueadero(
                id=2,
                rut='1002',
                nombre='Parqueadero Los Autos',
                direccion='Carrera 9 # 4-29',
                telefono='3021002789',
                email='contacto@parqueaderolosautos.co',
                ciudad='Neiva',
                usuario_id=4,
                pais_id=1,
                created_at=datetime(2024, 4, 18),
                updated_at=datetime(2024, 4, 18)
            )
        ]

        for parqueadero in parqueaderos:
            db.session.add(parqueadero)
        
        db.session.commit()

    if not Sede.query.first():
        sedes = [
            Sede(
                id=1,
                nombre='SuperParking Sede Norte',
                direccion='Calle 170 # 20-13',
                telefono='3011001123',
                email='norte@superparking.co',
                parqueadero_id=1,
                created_at=datetime(2024, 4, 15),
                updated_at=datetime(2024, 4, 15)
            ),
            Sede(
                id=2,
                nombre='SuperParking Sede Centro',
                direccion='Calle 19 # 2-29',
                telefono='30110001124',
                email='centro@superparking.co',
                parqueadero_id=1,
                created_at=datetime(2024, 4, 15),
                updated_at=datetime(2024, 4, 15)
            )
        ]

        for sede in sedes:
            db.session.add(sede)
        
        db.session.commit()

    if not Modulo.query.first():
        modulos = []

        for i in range(1, 21):
            modulos.append(Modulo(id=i, nombre=f'M{i}', habilitado=True, descripcion=f'Módulo {i}', sede_id=1, created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15)))
        
        for i in range(21, 41):
            modulos.append(Modulo(id=i, nombre=f'M{i}', habilitado=True, descripcion=f'Módulo {i}', sede_id=1, created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15)))
        
        for m in modulos:
            db.session.add(m)
        
        db.session.commit()
    
    if not Cliente.query.first():
        clientes = [
            Cliente(documento='123456789', nombres='Juan', apellidos='Perez', telefono='1234567890', email='juan.perez@example.com', direccion='Calle 123', parqueadero_id=1, created_at=datetime.now(), updated_at=datetime.now()),
            Cliente(documento='987654321', nombres='Maria', apellidos='Gonzalez', telefono='9876543210', email='maria.gonzalez@example.com', direccion='Carrera 456', parqueadero_id=1, created_at=datetime.now(), updated_at=datetime.now()),
            Cliente(documento='789012345', nombres='Pedro', apellidos='Lopez', telefono='7890123450', email='pedro.lopez@example.com', direccion='Avenida 789', parqueadero_id=1, created_at=datetime.now(), updated_at=datetime.now()),
            Cliente(documento='567890123', nombres='Ana', apellidos='Martin', telefono='5678901230', email='ana.martin@example.com', direccion='Calle 567', parqueadero_id=1, created_at=datetime.now(), updated_at=datetime.now()),
            Cliente(documento='345678901', nombres='Carlos', apellidos='Gomez', telefono='3456789010', email='carlos.gomez@example.com', direccion='Carrera 345', parqueadero_id=1, created_at=datetime.now(), updated_at=datetime.now()),
            Cliente(documento='1234567890', nombres='Sofia', apellidos='Garcia', telefono='12345678901', email='sofia.garcia@example.com', direccion='Avenida 123', parqueadero_id=1, created_at=datetime.now(), updated_at=datetime.now()),
            Cliente(documento='9876543210', nombres='David', apellidos='Rodriguez', telefono='98765432101', email='david.rodriguez@example.com', direccion='Carrera 987', parqueadero_id=1, created_at=datetime.now(), updated_at=datetime.now()),
            Cliente(documento='7890123450', nombres='Laura', apellidos='Flores', telefono='78901234501', email='laura.flores@example.com', direccion='Avenida 789', parqueadero_id=1, created_at=datetime.now(), updated_at=datetime.now())
        ]

        db.session.add_all(clientes)
        db.session.commit()
    
    if not TarifaTipo.query.first():
        tipos_tarifa = [
            TarifaTipo(id=1, nombre='Minutos', unidad=1, created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15)),
            TarifaTipo(id=2, nombre='Horas', unidad=2, created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15)),
            TarifaTipo(id=3, nombre='Días', unidad=3, created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15)),
            TarifaTipo(id=4, nombre='Semanas', unidad=4, created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15)),
            TarifaTipo(id=5, nombre='Meses', unidad=5, created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15)),
            TarifaTipo(id=6, nombre='Años', unidad=6, created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15))
        ]

        db.session.add_all(tipos_tarifa)

        db.session.commit()

    if not Tarifa.query.first():
        tarifas = [
            Tarifa(id=1, nombre='Tarifa por minuto', costo=100, tarifa_tipo_id=1, created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15)),
            Tarifa(id=2, nombre='Tarifa por hora', costo=2000, tarifa_tipo_id=2, created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15)),
            Tarifa(id=3, nombre='Tarifa por día', costo=15000, tarifa_tipo_id=3, created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15)),
            Tarifa(id=4, nombre='Tarifa por semana', costo=100000, tarifa_tipo_id=4, created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15)),
            Tarifa(id=5, nombre='Tarifa por mes', costo=300000, tarifa_tipo_id=5, created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15)),
            Tarifa(id=6, nombre='Tarifa por año', costo=2000000, tarifa_tipo_id=6, created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15))
        ]

        db.session.add_all(tarifas)

        db.session.commit()

    if not VehiculoTipo.query.first():
        data = [
            VehiculoTipo(id=1, nombre='Motocicleta', tarifa_id=1, created_at=datetime(2024, 4, 17), updated_at=datetime(2024, 4, 17)),
            VehiculoTipo(id=2, nombre='Automóvil', tarifa_id=1, created_at=datetime(2024, 4, 17), updated_at=datetime(2024, 4, 17)),
            VehiculoTipo(id=3, nombre='Camioneta', tarifa_id=1, created_at=datetime(2024, 4, 17), updated_at=datetime(2024, 4, 17)),
            VehiculoTipo(id=4, nombre='Camión', tarifa_id=1, created_at=datetime(2024, 4, 17), updated_at=datetime(2024, 4, 17)),
            VehiculoTipo(id=5, nombre='Bus', tarifa_id=1, created_at=datetime(2024, 4, 17), updated_at=datetime(2024, 4, 17)),
            VehiculoTipo(id=6, nombre='Bicicleta', tarifa_id=1, created_at=datetime(2024, 4, 17), updated_at=datetime(2024, 4, 17)),
            VehiculoTipo(id=7, nombre='Motocicleta Deportiva', tarifa_id=1, created_at=datetime(2024, 4, 17), updated_at=datetime(2024, 4, 17)),
            VehiculoTipo(id=8, nombre='Automóvil Familiar', tarifa_id=1, created_at=datetime(2024, 4, 17), updated_at=datetime(2024, 4, 17)),
            VehiculoTipo(id=9, nombre='Camioneta SUV', tarifa_id=1, created_at=datetime(2024, 4, 17), updated_at=datetime(2024, 4, 17)),
            VehiculoTipo(id=10, nombre='Camión Articulado', tarifa_id=1, created_at=datetime(2024, 4, 17), updated_at=datetime(2024, 4, 17))
        ]
        
        db.session.bulk_save_objects(data)
        db.session.commit()

    if not Vehiculo.query.first():
        vehiculos = [
            Vehiculo(placa='ABC123', disponible=True, marca='Chevrolet', modelo='2021', vehiculo_tipo_id=2, cliente_id=1, created_at=datetime.now(), updated_at=datetime.now()),
            Vehiculo(placa='DEF456', disponible=True, marca='Renault', modelo='2020', vehiculo_tipo_id=2, cliente_id=2, created_at=datetime.now(), updated_at=datetime.now()),
            Vehiculo(placa='GHI789', disponible=True, marca='Mazda', modelo='2019', vehiculo_tipo_id=2, cliente_id=3, created_at=datetime.now(), updated_at=datetime.now()),
            Vehiculo(placa='JKL012', disponible=True, marca='Toyota', modelo='2018', vehiculo_tipo_id=2, cliente_id=4, created_at=datetime.now(), updated_at=datetime.now()),
            Vehiculo(placa='MNO345', disponible=True, marca='Nissan', modelo='2017', vehiculo_tipo_id=2, cliente_id=5, created_at=datetime.now(), updated_at=datetime.now()),
            Vehiculo(placa='PQR678', disponible=True, marca='Ford', modelo='2016', vehiculo_tipo_id=2, cliente_id=6, created_at=datetime.now(), updated_at=datetime.now()),
            Vehiculo(placa='STU901', disponible=True, marca='Kia', modelo='2015', vehiculo_tipo_id=2, cliente_id=7, created_at=datetime.now(), updated_at=datetime.now()),
            Vehiculo(placa='VWX234', disponible=True, marca='Hyundai', modelo='2014', vehiculo_tipo_id=2, cliente_id=8, created_at=datetime.now(), updated_at=datetime.now())
        ]

        db.session.add_all(vehiculos)
        db.session.commit()

    if not Periodicidad.query.first():
        periodicidades = [
            Periodicidad(id=1, nombre='Diario', dias=1, parqueadero_id=1, created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15)),
            Periodicidad(id=2, nombre='Semanal', dias=7, parqueadero_id=1, created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15)),
            Periodicidad(id=3, nombre='Mensual', dias=30, parqueadero_id=1, created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15)),
            Periodicidad(id=4, nombre='Trimestral', dias=365, parqueadero_id=1, created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15)),
            Periodicidad(id=5, nombre='Semestral', dias=365, parqueadero_id=1, created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15)),
            Periodicidad(id=6, nombre='Anual', dias=365, parqueadero_id=1, created_at=datetime(2024, 4, 15), updated_at=datetime(2024, 4, 15))
        ]

        db.session.add_all(periodicidades)
        db.session.commit()

    if not SedeUsuario.query.first():
        sede_usuario = SedeUsuario(sede_id=1, usuario_id=3, created_at=datetime.now(), updated_at=datetime.now())
        db.session.add(sede_usuario)
        sede_usuario = SedeUsuario(sede_id=2, usuario_id=3, created_at=datetime.now(), updated_at=datetime.now())
        db.session.add(sede_usuario)
        db.session.commit()

with app.app_context():
    db.create_all()

    insert_initial_values()
