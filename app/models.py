from app import db


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

    def __repr__(self):
        return f'<Parqueadero {self.vehiculo_placa}>'


class Pais(db.Model):
    """
    Representa un país.
    """
    __tablename__ = 'pais'  # Nombre de la tabla en la base de datos
    
    # Definición de columnas
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
    __tablename__ = 'usuario'  # Nombre de la tabla en la base de datos

    # Definición de columnas
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
    __tablename__ = 'cliente'  # Nombre de la tabla en la base de datos

    # Definición de columnas
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

    # Relaciones
    parqueadero = db.relationship("Parqueadero", back_populates="clientes")

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
