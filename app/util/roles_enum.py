from enum import Enum

class Roles(Enum):
    """
    Enumeración de roles de usuario en la aplicación.
    """
    PROPIETARIO = "Propietario"
    ADMINISTRADOR = "Administrador"
    OPERARIO = "Operario"
