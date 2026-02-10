"""
Base declarativa para todos os modelos SQLAlchemy
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

# Configuração de metadados com schema padrão
metadata = MetaData(schema="empl")

# Base declarativa para todos os modelos
Base = declarative_base(metadata=metadata)

# Função para obter metadados de todos os modelos
def get_all_metadata():
    """
    Retorna metadados de todos os modelos registrados
    """
    return Base.metadata

# Função para verificar se um modelo está registrado
def is_model_registered(model_class):
    """
    Verifica se um modelo está registrado na base
    """
    return model_class in Base.metadata.tables.values()

# NOTA: Não importar entidades aqui para evitar importação circular
# As entidades devem ser importadas no ponto onde forem necessárias
# (ex: em arquivos como data/database.py ou data/migrations.py)
