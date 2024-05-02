from datetime import datetime

from sqlalchemy import event

from app import app, db


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

    parqueadero = db.relationship("Parqueadero", back_populates="sedes")
    modulos = db.relationship("Modulo", back_populates="sede")

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
    telefono = db.Column(db.String(16), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    pais_id = db.Column(db.Integer, db.ForeignKey('pais.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    clientes = db.relationship("Cliente", back_populates="parqueadero")
    periodicidades = db.relationship("Periodicidad", back_populates="parqueadero")
    sedes = db.relationship("Sede", back_populates="parqueadero")

    def __repr__(self):
        return f'<Parqueadero {self.vehiculo_placa}>'


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


class Usuario(db.Model):
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
    rol_id = db.Column(db.Integer, db.ForeignKey('rol.id'), nullable=False)  # Asume que la tabla 'rol' y su columna 'id' existen
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    rol = db.relationship("Rol", back_populates="usuarios")

    def __repr__(self):
        return f"<Usuario(documento='{self.documento}', nombres='{self.nombres}', apellidos='{self.apellidos}')>"


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

    usuarios = db.relationship('Usuario', back_populates='rol', lazy='dynamic')

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
    parqueos = db.relationship("Parqueo", back_populates="tarifa")

    def __repr__(self):
        return f"<Tarifa(id={self.id}, nombre='{self.nombre}', costo={self.costo})>"


class Parqueo(db.Model):
    __tablename__ = 'parqueo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_hora_entrada = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    fecha_hora_salida = db.Column(db.DateTime)
    modulo_id = db.Column(db.Integer, db.ForeignKey('modulo.id'), nullable=False)
    vehiculo_placa = db.Column(db.String(12), db.ForeignKey('vehiculo.placa'), nullable=False)
    medio_pago_id = db.Column(db.Integer, db.ForeignKey('medio_pago.id'), nullable=False)
    tarifa_id = db.Column(db.Integer, db.ForeignKey('tarifa.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    
    modulo = db.relationship("Modulo", back_populates="parqueos")
    vehiculo = db.relationship("Vehiculo", back_populates="parqueos")
    medio_pago = db.relationship("MedioPago", back_populates="parqueos")
    tarifa = db.relationship("Tarifa", back_populates="parqueos")

    def __repr__(self):
        return f"<Parqueo(id={self.id}, fecha_hora_entrada='{self.fecha_hora_entrada}', fecha_hora_salida='{self.fecha_hora_salida}')>"


class VehiculoTipo(db.Model):
    __tablename__ = 'vehiculo_tipo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    vehiculos = db.relationship("Vehiculo", back_populates="vehiculo_tipo")

    def __repr__(self):
        return f"<VehiculoTipo(id={self.id}, nombre='{self.nombre}')>"


class Vehiculo(db.Model):
    __tablename__ = 'vehiculo'
    placa = db.Column(db.String(12), primary_key=True)
    marca = db.Column(db.String(32))
    modelo = db.Column(db.String(4))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    vehiculo_tipo_id = db.Column(db.Integer, db.ForeignKey('vehiculo_tipo.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)

    parqueos = db.relationship('Parqueo', back_populates='vehiculo')
    cliente = db.relationship("Cliente", back_populates="vehiculos")
    vehiculo_tipo = db.relationship("VehiculoTipo", back_populates="vehiculos")

    def __repr__(self):
        return f"<Vehiculo(placa='{self.placa}', marca='{self.marca}', modelo='{self.modelo}')>"


class MedioPago(db.Model):
    __tablename__ = 'medio_pago'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    parqueos = db.relationship("Parqueo", back_populates="medio_pago")

    def __repr__(self):
        return f"<MedioPago(nombre='{self.nombre}')>"


def insert_initial_values():
    if not VehiculoTipo.query.first():
        data = [
            VehiculoTipo(id=1, nombre='Motocicleta', created_at=datetime(2024, 4, 17), updated_at=datetime(2024, 4, 17)),
            VehiculoTipo(id=2, nombre='Automóvil', created_at=datetime(2024, 4, 17), updated_at=datetime(2024, 4, 17)),
            VehiculoTipo(id=3, nombre='Camioneta', created_at=datetime(2024, 4, 17), updated_at=datetime(2024, 4, 17)),
            VehiculoTipo(id=4, nombre='Camión', created_at=datetime(2024, 4, 17), updated_at=datetime(2024, 4, 17)),
            VehiculoTipo(id=5, nombre='Bus', created_at=datetime(2024, 4, 17), updated_at=datetime(2024, 4, 17)),
            VehiculoTipo(id=6, nombre='Bicicleta', created_at=datetime(2024, 4, 17), updated_at=datetime(2024, 4, 17)),
            VehiculoTipo(id=7, nombre='Motocicleta Deportiva', created_at=datetime(2024, 4, 17), updated_at=datetime(2024, 4, 17)),
            VehiculoTipo(id=8, nombre='Automóvil Familiar', created_at=datetime(2024, 4, 17), updated_at=datetime(2024, 4, 17)),
            VehiculoTipo(id=9, nombre='Camioneta SUV', created_at=datetime(2024, 4, 17), updated_at=datetime(2024, 4, 17)),
            VehiculoTipo(id=10, nombre='Camión Articulado', created_at=datetime(2024, 4, 17), updated_at=datetime(2024, 4, 17))
        ]
        
        db.session.bulk_save_objects(data)
        db.session.commit()

with app.app_context():
    db.create_all()

    insert_initial_values()
