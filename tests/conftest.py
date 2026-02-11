"""
Configuração comum de fixtures para testes
"""
import pytest
from datetime import datetime
from typing import Dict, Any


@pytest.fixture
def agent_id() -> str:
    """Fixture de ID de agente para testes"""
    return "agent-123"


@pytest.fixture
def user_id() -> str:
    """Fixture de ID de usuário para testes"""
    return "user-456"


@pytest.fixture
def document_dict() -> Dict[str, Any]:
    """Fixture de documento para testes"""
    return {
        "_id": "doc-789",
        "id": "doc-789",
        "agent_id": "agent-123",
        "user_id": "user-456",
        "file_name": "documento.pdf",
        "metadata": {
            "author": "Test Author",
            "category": "test"
        },
        "vector_response": {
            "status": "success",
            "vectors_stored": 150
        },
        "created_at": datetime(2025, 1, 1, 10, 0, 0),
        "updated_at": datetime(2025, 1, 2, 15, 30, 0),
        "mongo_error": False
    }


@pytest.fixture
def document_dict_with_mongo_error() -> Dict[str, Any]:
    """Fixture de documento com erro do MongoDB"""
    return {
        "_id": "doc-error",
        "id": "doc-error",
        "agent_id": "agent-123",
        "user_id": "user-456",
        "file_name": "documento_erro.pdf",
        "metadata": {},
        "vector_response": {"status": "success"},
        "created_at": datetime(2025, 1, 1, 10, 0, 0),
        "mongo_error": True
    }


@pytest.fixture
def upload_result_success() -> Dict[str, Any]:
    """Fixture de resultado de upload bem-sucedido"""
    return {
        "vector_db_response": {
            "status": "success",
            "vectors_stored": 150
        },
        "document": {
            "id": "doc-789",
            "agent_id": "agent-123",
            "user_id": "user-456",
            "file_name": "documento.pdf",
            "metadata": {},
            "created_at": datetime(2025, 1, 1, 10, 0, 0),
            "mongo_error": False
        }
    }


@pytest.fixture
def upload_result_with_mongo_error() -> Dict[str, Any]:
    """Fixture de resultado de upload com erro do MongoDB"""
    return {
        "vector_db_response": {
            "status": "success",
            "vectors_stored": 150
        },
        "document": {
            "id": "doc-error",
            "agent_id": "agent-123",
            "user_id": "user-456",
            "file_name": "documento.pdf",
            "metadata": {},
            "created_at": datetime(2025, 1, 1, 10, 0, 0),
            "mongo_error": True
        }
    }


@pytest.fixture
def delete_result_success() -> Dict[str, Any]:
    """Fixture de resultado de deleção bem-sucedido"""
    return {
        "success": True,
        "document_id": "doc-789",
        "file_name": "documento.pdf",
        "vector_db_response": {
            "deleted": True,
            "vectors_deleted": 150
        },
        "mongo_deleted": True
    }


@pytest.fixture
def file_content() -> bytes:
    """Fixture de conteúdo de arquivo para testes"""
    return b"fake pdf content for testing"


@pytest.fixture
def file_name() -> str:
    """Fixture de nome de arquivo"""
    return "test_document.pdf"
