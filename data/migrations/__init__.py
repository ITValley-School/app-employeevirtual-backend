"""
Módulo de migrações automáticas do banco de dados
"""

from .auto_migrate import (
    AutoMigrator,
    auto_migrate,
    force_migrate,
    get_status,
    test_db,
    migrator
)

__all__ = [
    "AutoMigrator",
    "auto_migrate", 
    "force_migrate",
    "get_status",
    "test_db",
    "migrator"
]
