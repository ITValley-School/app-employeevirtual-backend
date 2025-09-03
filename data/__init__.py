"""
Camada Data - inicialização leve do pacote.

Evita reexports pesados para não causar import circular quando
`data.base` é importado dentro dos modelos.
"""

from .database import get_db, SessionLocal, engine

__all__ = [
    'get_db',
    'SessionLocal',
    'engine',
]