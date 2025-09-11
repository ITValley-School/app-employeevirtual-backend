"""
Configuração de UUIDs para o sistema EmployeeVirtual - SQL Server
"""
import uuid
from typing import Union
from sqlalchemy import TypeDecorator, String
from pydantic import Field

class UUIDString(str):
    """Tipo personalizado para UUIDs como string"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, str):
            try:
                uuid.UUID(v)
                return v
            except ValueError:
                raise ValueError('Invalid UUID string')
        elif isinstance(v, uuid.UUID):
            return str(v)
        else:
            raise ValueError('Invalid UUID type')
    
    @classmethod
    def generate(cls) -> str:
        """Gera um novo UUID como string"""
        return str(uuid.uuid4())

class UUIDColumn(TypeDecorator):
    """Coluna SQLAlchemy para UUIDs no SQL Server"""
    
    impl = String(36)
    cache_ok = True
    
    def __init__(self, *args, **kwargs):
        # Remover default se existir para evitar conflito com SQL Server
        if 'default' in kwargs:
            del kwargs['default']
        
        # Inicializar o TypeDecorator
        super().__init__()
    
    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(String(36))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return str(value)
    
    def copy(self, **kw):
        """Cria uma cópia do tipo para o SQLAlchemy"""
        return UUIDColumn()
    
    def __repr__(self):
        return "UUIDColumn()"

def generate_uuid() -> str:
    """Função para gerar UUIDs"""
    return str(uuid.uuid4())

def validate_uuid(uuid_str: str) -> bool:
    """Valida se uma string é um UUID válido"""
    try:
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        return False

# Tipos Pydantic para UUIDs
class UUIDField:
    """Campo Pydantic para UUIDs"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, str):
            if not validate_uuid(v):
                raise ValueError('Invalid UUID format')
            return v
        elif isinstance(v, uuid.UUID):
            return str(v)
        else:
            raise ValueError('UUID must be string or UUID object')
    
    @classmethod
    def generate(cls) -> str:
        """Gera um novo UUID"""
        return generate_uuid()

# Função para criar campos UUID em modelos Pydantic
def uuid_field(description: str = "UUID único do registro", **kwargs):
    """Cria um campo UUID para modelos Pydantic"""
    return Field(
        default_factory=generate_uuid,
        description=description,
        **kwargs
    )

# Função para criar campos UUID obrigatórios
def required_uuid_field(description: str = "UUID único do registro", **kwargs):
    """Cria um campo UUID obrigatório para modelos Pydantic"""
    return Field(
        ...,
        description=description,
        **kwargs
    )
