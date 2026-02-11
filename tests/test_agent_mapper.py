"""
Testes unitários para AgentMapper
Camada: Mapper (Unit - No Mocks)
Estratégia: Testes puros de transformação de dados sem dependências externas

Testa os novos métodos adicionados na refatoração:
- to_document()
- to_document_list()
- to_document_delete()
- to_upload_response()
"""
import pytest
from datetime import datetime
from typing import Dict, Any, List

from mappers.agent_mapper import AgentMapper
from schemas.agents.responses import (
    AgentDocumentResponse,
    AgentDocumentListResponse,
    AgentDocumentDeleteResponse
)


class TestAgentMapperToDocument:
    """Testes para AgentMapper.to_document()"""

    def test_should_convert_dict_to_agent_document_response(
        self, document_dict: Dict[str, Any], agent_id: str, user_id: str
    ):
        """Deve converter dict de documento para AgentDocumentResponse com todos os campos"""
        # Act
        result = AgentMapper.to_document(document_dict, agent_id, user_id)

        # Assert
        assert isinstance(result, AgentDocumentResponse)
        assert result.id == "doc-789"
        assert result.agent_id == agent_id
        assert result.user_id == user_id
        assert result.file_name == "documento.pdf"
        assert result.metadata == {"author": "Test Author", "category": "test"}
        assert result.vector_response == {"status": "success", "vectors_stored": 150}
        assert result.created_at == datetime(2025, 1, 1, 10, 0, 0)
        assert result.updated_at == datetime(2025, 1, 2, 15, 30, 0)
        assert result.mongo_error is False

    def test_should_use_provided_agent_id_when_missing_in_dict(
        self, agent_id: str, user_id: str
    ):
        """Deve usar agent_id fornecido quando ausente no dict"""
        # Arrange
        doc_without_agent_id = {
            "id": "doc-123",
            "file_name": "test.pdf",
            "created_at": datetime(2025, 1, 1, 10, 0, 0)
        }

        # Act
        result = AgentMapper.to_document(doc_without_agent_id, agent_id, user_id)

        # Assert
        assert result.agent_id == agent_id

    def test_should_use_provided_user_id_when_missing_in_dict(
        self, agent_id: str, user_id: str
    ):
        """Deve usar user_id fornecido quando ausente no dict"""
        # Arrange
        doc_without_user_id = {
            "id": "doc-123",
            "file_name": "test.pdf",
            "created_at": datetime(2025, 1, 1, 10, 0, 0)
        }

        # Act
        result = AgentMapper.to_document(doc_without_user_id, agent_id, user_id)

        # Assert
        assert result.user_id == user_id

    def test_should_extract_id_from_mongodb_underscore_id_when_id_missing(
        self, agent_id: str, user_id: str
    ):
        """Deve extrair ID do campo _id do MongoDB quando id não estiver presente"""
        # Arrange
        doc_with_only_underscore_id = {
            "_id": "mongodb-id-123",
            "file_name": "test.pdf",
            "created_at": datetime(2025, 1, 1, 10, 0, 0)
        }

        # Act
        result = AgentMapper.to_document(doc_with_only_underscore_id, agent_id, user_id)

        # Assert
        assert result.id == "mongodb-id-123"

    def test_should_use_empty_string_for_id_when_both_missing(
        self, agent_id: str, user_id: str
    ):
        """Deve usar string vazia quando id e _id estiverem ausentes"""
        # Arrange
        doc_without_ids = {
            "file_name": "test.pdf",
            "created_at": datetime(2025, 1, 1, 10, 0, 0)
        }

        # Act
        result = AgentMapper.to_document(doc_without_ids, agent_id, user_id)

        # Assert
        assert result.id == ""

    def test_should_use_current_time_when_created_at_missing(
        self, agent_id: str, user_id: str
    ):
        """Deve usar datetime atual quando created_at não estiver presente"""
        # Arrange
        doc_without_created_at = {
            "id": "doc-123",
            "file_name": "test.pdf"
        }

        # Act
        before = datetime.utcnow()
        result = AgentMapper.to_document(doc_without_created_at, agent_id, user_id)
        after = datetime.utcnow()

        # Assert
        assert before <= result.created_at <= after

    def test_should_handle_none_created_at(
        self, agent_id: str, user_id: str
    ):
        """Deve usar datetime atual quando created_at for None"""
        # Arrange
        doc_with_none_created_at = {
            "id": "doc-123",
            "file_name": "test.pdf",
            "created_at": None
        }

        # Act
        before = datetime.utcnow()
        result = AgentMapper.to_document(doc_with_none_created_at, agent_id, user_id)
        after = datetime.utcnow()

        # Assert
        assert before <= result.created_at <= after

    def test_should_use_empty_dict_for_metadata_when_missing(
        self, agent_id: str, user_id: str
    ):
        """Deve usar dict vazio quando metadata não estiver presente"""
        # Arrange
        doc_without_metadata = {
            "id": "doc-123",
            "file_name": "test.pdf",
            "created_at": datetime(2025, 1, 1, 10, 0, 0)
        }

        # Act
        result = AgentMapper.to_document(doc_without_metadata, agent_id, user_id)

        # Assert
        assert result.metadata == {}

    def test_should_set_mongo_error_to_false_by_default(
        self, agent_id: str, user_id: str
    ):
        """Deve definir mongo_error como False quando não estiver presente"""
        # Arrange
        doc_without_mongo_error = {
            "id": "doc-123",
            "file_name": "test.pdf",
            "created_at": datetime(2025, 1, 1, 10, 0, 0)
        }

        # Act
        result = AgentMapper.to_document(doc_without_mongo_error, agent_id, user_id)

        # Assert
        assert result.mongo_error is False

    def test_should_preserve_mongo_error_true(
        self, document_dict_with_mongo_error: Dict[str, Any], agent_id: str, user_id: str
    ):
        """Deve preservar mongo_error=True quando presente"""
        # Act
        result = AgentMapper.to_document(document_dict_with_mongo_error, agent_id, user_id)

        # Assert
        assert result.mongo_error is True


class TestAgentMapperToDocumentList:
    """Testes para AgentMapper.to_document_list()"""

    def test_should_convert_list_of_dicts_to_document_list_response(
        self, agent_id: str, user_id: str
    ):
        """Deve converter lista de dicts para AgentDocumentListResponse"""
        # Arrange
        documents = [
            {
                "id": "doc-1",
                "file_name": "doc1.pdf",
                "created_at": datetime(2025, 1, 1, 10, 0, 0)
            },
            {
                "id": "doc-2",
                "file_name": "doc2.pdf",
                "created_at": datetime(2025, 1, 2, 11, 0, 0)
            },
            {
                "id": "doc-3",
                "file_name": "doc3.pdf",
                "created_at": datetime(2025, 1, 3, 12, 0, 0)
            }
        ]

        # Act
        result = AgentMapper.to_document_list(documents, agent_id, user_id)

        # Assert
        assert isinstance(result, AgentDocumentListResponse)
        assert len(result.documents) == 3
        assert result.total == 3
        assert result.agent_id == agent_id

    def test_should_convert_each_document_correctly(
        self, agent_id: str, user_id: str
    ):
        """Deve converter cada documento corretamente"""
        # Arrange
        documents = [
            {
                "id": "doc-1",
                "file_name": "doc1.pdf",
                "metadata": {"key": "value1"},
                "created_at": datetime(2025, 1, 1, 10, 0, 0)
            },
            {
                "id": "doc-2",
                "file_name": "doc2.pdf",
                "metadata": {"key": "value2"},
                "created_at": datetime(2025, 1, 2, 11, 0, 0)
            }
        ]

        # Act
        result = AgentMapper.to_document_list(documents, agent_id, user_id)

        # Assert
        assert result.documents[0].id == "doc-1"
        assert result.documents[0].file_name == "doc1.pdf"
        assert result.documents[0].metadata == {"key": "value1"}
        assert result.documents[0].agent_id == agent_id
        assert result.documents[0].user_id == user_id

        assert result.documents[1].id == "doc-2"
        assert result.documents[1].file_name == "doc2.pdf"
        assert result.documents[1].metadata == {"key": "value2"}

    def test_should_handle_empty_list(
        self, agent_id: str, user_id: str
    ):
        """Deve lidar corretamente com lista vazia"""
        # Arrange
        documents: List[Dict[str, Any]] = []

        # Act
        result = AgentMapper.to_document_list(documents, agent_id, user_id)

        # Assert
        assert isinstance(result, AgentDocumentListResponse)
        assert result.documents == []
        assert result.total == 0
        assert result.agent_id == agent_id

    def test_should_handle_single_document(
        self, document_dict: Dict[str, Any], agent_id: str, user_id: str
    ):
        """Deve lidar corretamente com lista contendo um único documento"""
        # Arrange
        documents = [document_dict]

        # Act
        result = AgentMapper.to_document_list(documents, agent_id, user_id)

        # Assert
        assert len(result.documents) == 1
        assert result.total == 1
        assert result.documents[0].id == "doc-789"


class TestAgentMapperToDocumentDelete:
    """Testes para AgentMapper.to_document_delete()"""

    def test_should_convert_delete_result_to_response(
        self, delete_result_success: Dict[str, Any]
    ):
        """Deve converter resultado de deleção para AgentDocumentDeleteResponse"""
        # Act
        result = AgentMapper.to_document_delete(delete_result_success, "doc-789")

        # Assert
        assert isinstance(result, AgentDocumentDeleteResponse)
        assert result.success is True
        assert result.document_id == "doc-789"
        assert result.file_name == "documento.pdf"
        assert result.vector_db_response == {"deleted": True, "vectors_deleted": 150}
        assert result.mongo_deleted is True
        assert result.message == "Documento removido com sucesso"

    def test_should_use_provided_document_id_when_missing_in_result(self):
        """Deve usar document_id fornecido quando ausente no resultado"""
        # Arrange
        result_without_document_id = {
            "success": True,
            "file_name": "test.pdf",
            "mongo_deleted": True
        }

        # Act
        result = AgentMapper.to_document_delete(result_without_document_id, "doc-provided")

        # Assert
        assert result.document_id == "doc-provided"

    def test_should_default_success_to_true_when_missing(self):
        """Deve definir success como True quando não estiver presente"""
        # Arrange
        result_without_success = {
            "document_id": "doc-123",
            "mongo_deleted": True
        }

        # Act
        result = AgentMapper.to_document_delete(result_without_success, "doc-123")

        # Assert
        assert result.success is True

    def test_should_default_mongo_deleted_to_true_when_missing(self):
        """Deve definir mongo_deleted como True quando não estiver presente"""
        # Arrange
        result_without_mongo_deleted = {
            "success": True,
            "document_id": "doc-123"
        }

        # Act
        result = AgentMapper.to_document_delete(result_without_mongo_deleted, "doc-123")

        # Assert
        assert result.mongo_deleted is True

    def test_should_handle_none_file_name(self):
        """Deve lidar com file_name ausente (None)"""
        # Arrange
        result_without_file_name = {
            "success": True,
            "document_id": "doc-123",
            "mongo_deleted": True
        }

        # Act
        result = AgentMapper.to_document_delete(result_without_file_name, "doc-123")

        # Assert
        assert result.file_name is None

    def test_should_handle_none_vector_db_response(self):
        """Deve lidar com vector_db_response ausente (None)"""
        # Arrange
        result_without_vector_response = {
            "success": True,
            "document_id": "doc-123",
            "mongo_deleted": True
        }

        # Act
        result = AgentMapper.to_document_delete(result_without_vector_response, "doc-123")

        # Assert
        assert result.vector_db_response is None

    def test_should_always_include_success_message(self):
        """Deve sempre incluir mensagem de sucesso"""
        # Arrange
        minimal_result = {}

        # Act
        result = AgentMapper.to_document_delete(minimal_result, "doc-123")

        # Assert
        assert result.message == "Documento removido com sucesso"


class TestAgentMapperToUploadResponse:
    """Testes para AgentMapper.to_upload_response()"""

    def test_should_format_successful_upload_without_mongo_error(
        self, upload_result_success: Dict[str, Any]
    ):
        """Deve formatar upload bem-sucedido sem erro do MongoDB"""
        # Act
        result = AgentMapper.to_upload_response(upload_result_success)

        # Assert
        assert "message" in result
        assert result["message"] == "Documento enviado com sucesso"
        assert "document" in result
        assert result["document"]["id"] == "doc-789"
        assert result["document"]["file_name"] == "documento.pdf"
        assert "vector_db_response" in result
        assert result["vector_db_response"]["status"] == "success"
        assert "warning" not in result

    def test_should_format_upload_with_mongo_error_and_warning(
        self, upload_result_with_mongo_error: Dict[str, Any]
    ):
        """Deve formatar upload com erro do MongoDB incluindo aviso"""
        # Act
        result = AgentMapper.to_upload_response(upload_result_with_mongo_error)

        # Assert
        assert "message" in result
        assert "Aviso" in result["message"]
        assert "falha ao registrar no MongoDB" in result["message"]
        assert "document" in result
        assert result["document"]["mongo_error"] is True
        assert "vector_db_response" in result
        assert "warning" in result
        assert result["warning"] == "MongoDB indisponível, mas documento está no Vector DB"

    def test_should_handle_missing_document_field(self):
        """Deve lidar com campo document ausente"""
        # Arrange
        result_without_document = {
            "vector_db_response": {"status": "success"}
        }

        # Act
        result = AgentMapper.to_upload_response(result_without_document)

        # Assert
        assert "message" in result
        assert result["message"] == "Documento enviado com sucesso"
        assert "document" in result
        assert result["document"] == {}

    def test_should_handle_document_without_mongo_error_field(self):
        """Deve tratar documento sem campo mongo_error como sucesso"""
        # Arrange
        result_without_mongo_error_field = {
            "document": {
                "id": "doc-123",
                "file_name": "test.pdf"
            },
            "vector_db_response": {"status": "success"}
        }

        # Act
        result = AgentMapper.to_upload_response(result_without_mongo_error_field)

        # Assert
        assert result["message"] == "Documento enviado com sucesso"
        assert "warning" not in result

    def test_should_detect_mongo_error_false_as_success(self):
        """Deve detectar mongo_error=False como sucesso (sem aviso)"""
        # Arrange
        result_with_mongo_error_false = {
            "document": {
                "id": "doc-123",
                "file_name": "test.pdf",
                "mongo_error": False
            },
            "vector_db_response": {"status": "success"}
        }

        # Act
        result = AgentMapper.to_upload_response(result_with_mongo_error_false)

        # Assert
        assert result["message"] == "Documento enviado com sucesso"
        assert "warning" not in result

    def test_should_preserve_vector_db_response(self):
        """Deve preservar resposta completa do Vector DB"""
        # Arrange
        result_with_detailed_vector_response = {
            "document": {"id": "doc-123", "mongo_error": False},
            "vector_db_response": {
                "status": "success",
                "vectors_stored": 250,
                "chunks": 10,
                "processing_time": 2.5
            }
        }

        # Act
        result = AgentMapper.to_upload_response(result_with_detailed_vector_response)

        # Assert
        assert result["vector_db_response"]["vectors_stored"] == 250
        assert result["vector_db_response"]["chunks"] == 10
        assert result["vector_db_response"]["processing_time"] == 2.5

    def test_should_handle_missing_vector_db_response(self):
        """Deve lidar com vector_db_response ausente"""
        # Arrange
        result_without_vector_response = {
            "document": {"id": "doc-123", "mongo_error": False}
        }

        # Act
        result = AgentMapper.to_upload_response(result_without_vector_response)

        # Assert
        assert "vector_db_response" in result
        assert result["vector_db_response"] is None
