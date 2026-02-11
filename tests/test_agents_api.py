"""
Testes de integração para API de Agentes
Camada: API (Integration - Service Mocked)
Estratégia: Testa endpoints HTTP com mock do service

Testa os endpoints refatorados:
- POST /agents/{agent_id}/documents (upload_agent_document)
- GET /agents/{agent_id}/documents (list_agent_documents)
- DELETE /agents/{agent_id}/documents/{document_id} (delete_agent_document)
- PATCH /agents/{agent_id}/documents/{document_id}/metadata (update_agent_document_metadata)
- POST /agents/system/{agent_id}/execute (execute_system_agent com arquivo)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import status
from datetime import datetime
from io import BytesIO

from main import app  # Assumindo que o app FastAPI está em main.py
from data.entities.user_entities import UserEntity
from schemas.agents.requests import AgentExecuteRequest


@pytest.fixture
def client():
    """Cliente de teste do FastAPI"""
    return TestClient(app)


@pytest.fixture
def mock_current_user():
    """Mock do usuário autenticado"""
    user = UserEntity(
        id="user-456",
        email="test@example.com",
        name="Test User",
        password_hash="hashed_password",
        is_active=True,
        created_at=datetime.utcnow()
    )
    return user


@pytest.fixture
def mock_agent_service():
    """Mock do AgentService"""
    return Mock()


class TestUploadAgentDocument:
    """Testes para POST /agents/{agent_id}/documents"""

    @pytest.fixture(autouse=True)
    def setup(self, mock_current_user, mock_agent_service):
        """Setup para cada teste"""
        with patch("api.agents_api.get_current_user", return_value=mock_current_user), \
             patch("api.agents_api.get_agent_service", return_value=mock_agent_service):
            yield

    def test_should_return_201_when_document_uploaded_successfully(
        self, client: TestClient, mock_agent_service: Mock
    ):
        """Deve retornar 201 quando documento for enviado com sucesso"""
        # Arrange
        agent_id = "agent-123"
        file_content = b"fake pdf content"
        mock_agent_service.upload_agent_document.return_value = {
            "vector_db_response": {"status": "success"},
            "document": {
                "id": "doc-789",
                "agent_id": agent_id,
                "user_id": "user-456",
                "file_name": "test.pdf",
                "metadata": {},
                "created_at": datetime(2025, 1, 1, 10, 0, 0),
                "mongo_error": False
            }
        }

        # Act
        response = client.post(
            f"/agents/{agent_id}/documents",
            files={"filepdf": ("test.pdf", BytesIO(file_content), "application/pdf")}
        )

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert "message" in response.json()
        assert response.json()["message"] == "Documento enviado com sucesso"
        assert "document" in response.json()
        assert response.json()["document"]["id"] == "doc-789"

    def test_should_call_service_with_correct_parameters(
        self, client: TestClient, mock_agent_service: Mock, mock_current_user: UserEntity
    ):
        """Deve chamar service com parâmetros corretos"""
        # Arrange
        agent_id = "agent-123"
        file_content = b"fake pdf content"
        metadata = '{"author": "Test Author"}'
        mock_agent_service.upload_agent_document.return_value = {
            "vector_db_response": {"status": "success"},
            "document": {"id": "doc-789", "mongo_error": False}
        }

        # Act
        client.post(
            f"/agents/{agent_id}/documents",
            files={"filepdf": ("test.pdf", BytesIO(file_content), "application/pdf")},
            data={"metadone": metadata}
        )

        # Assert
        mock_agent_service.upload_agent_document.assert_called_once()
        call_args = mock_agent_service.upload_agent_document.call_args
        assert call_args.kwargs["agent_id"] == agent_id
        assert call_args.kwargs["user_id"] == mock_current_user.id
        assert call_args.kwargs["file_content"] == file_content
        assert call_args.kwargs["file_name"] == "test.pdf"
        assert call_args.kwargs["content_type"] == "application/pdf"
        assert call_args.kwargs["metadata_raw"] == metadata

    def test_should_return_400_when_service_raises_value_error(
        self, client: TestClient, mock_agent_service: Mock
    ):
        """Deve retornar 400 quando service lança ValueError"""
        # Arrange
        agent_id = "agent-123"
        mock_agent_service.upload_agent_document.side_effect = ValueError("Agente não encontrado")

        # Act
        response = client.post(
            f"/agents/{agent_id}/documents",
            files={"filepdf": ("test.pdf", BytesIO(b"content"), "application/pdf")}
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Agente não encontrado" in response.json()["detail"]

    def test_should_return_warning_when_mongo_error_occurs(
        self, client: TestClient, mock_agent_service: Mock
    ):
        """Deve retornar aviso quando houver erro no MongoDB"""
        # Arrange
        agent_id = "agent-123"
        mock_agent_service.upload_agent_document.return_value = {
            "vector_db_response": {"status": "success"},
            "document": {"id": "doc-789", "mongo_error": True}
        }

        # Act
        response = client.post(
            f"/agents/{agent_id}/documents",
            files={"filepdf": ("test.pdf", BytesIO(b"content"), "application/pdf")}
        )

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert "warning" in response.json()
        assert "MongoDB indisponível" in response.json()["warning"]


class TestListAgentDocuments:
    """Testes para GET /agents/{agent_id}/documents"""

    @pytest.fixture(autouse=True)
    def setup(self, mock_current_user, mock_agent_service):
        """Setup para cada teste"""
        with patch("api.agents_api.get_current_user", return_value=mock_current_user), \
             patch("api.agents_api.get_agent_service", return_value=mock_agent_service):
            yield

    def test_should_return_200_with_document_list(
        self, client: TestClient, mock_agent_service: Mock
    ):
        """Deve retornar 200 com lista de documentos"""
        # Arrange
        agent_id = "agent-123"
        mock_agent_service.list_agent_documents.return_value = [
            {
                "id": "doc-1",
                "file_name": "doc1.pdf",
                "created_at": datetime(2025, 1, 1, 10, 0, 0)
            },
            {
                "id": "doc-2",
                "file_name": "doc2.pdf",
                "created_at": datetime(2025, 1, 2, 11, 0, 0)
            }
        ]

        # Act
        response = client.get(f"/agents/{agent_id}/documents")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "documents" in data
        assert len(data["documents"]) == 2
        assert data["total"] == 2
        assert data["agent_id"] == agent_id

    def test_should_call_service_with_correct_parameters(
        self, client: TestClient, mock_agent_service: Mock, mock_current_user: UserEntity
    ):
        """Deve chamar service com parâmetros corretos"""
        # Arrange
        agent_id = "agent-123"
        mock_agent_service.list_agent_documents.return_value = []

        # Act
        client.get(f"/agents/{agent_id}/documents")

        # Assert
        mock_agent_service.list_agent_documents.assert_called_once_with(
            agent_id, mock_current_user.id
        )

    def test_should_return_404_when_agent_not_found(
        self, client: TestClient, mock_agent_service: Mock
    ):
        """Deve retornar 404 quando agente não for encontrado"""
        # Arrange
        agent_id = "nonexistent-agent"
        mock_agent_service.list_agent_documents.side_effect = ValueError("Agente não encontrado")

        # Act
        response = client.get(f"/agents/{agent_id}/documents")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_should_return_empty_list_when_no_documents(
        self, client: TestClient, mock_agent_service: Mock
    ):
        """Deve retornar lista vazia quando não houver documentos"""
        # Arrange
        agent_id = "agent-123"
        mock_agent_service.list_agent_documents.return_value = []

        # Act
        response = client.get(f"/agents/{agent_id}/documents")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["documents"] == []
        assert data["total"] == 0


class TestDeleteAgentDocument:
    """Testes para DELETE /agents/{agent_id}/documents/{document_id}"""

    @pytest.fixture(autouse=True)
    def setup(self, mock_current_user, mock_agent_service):
        """Setup para cada teste"""
        with patch("api.agents_api.get_current_user", return_value=mock_current_user), \
             patch("api.agents_api.get_agent_service", return_value=mock_agent_service):
            yield

    def test_should_return_200_when_document_deleted_successfully(
        self, client: TestClient, mock_agent_service: Mock
    ):
        """Deve retornar 200 quando documento for deletado com sucesso"""
        # Arrange
        agent_id = "agent-123"
        document_id = "doc-789"
        mock_agent_service.delete_agent_document.return_value = {
            "success": True,
            "document_id": document_id,
            "file_name": "documento.pdf",
            "vector_db_response": {"deleted": True},
            "mongo_deleted": True
        }

        # Act
        response = client.delete(f"/agents/{agent_id}/documents/{document_id}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["document_id"] == document_id
        assert data["message"] == "Documento removido com sucesso"

    def test_should_call_service_with_correct_parameters(
        self, client: TestClient, mock_agent_service: Mock, mock_current_user: UserEntity
    ):
        """Deve chamar service com parâmetros corretos"""
        # Arrange
        agent_id = "agent-123"
        document_id = "doc-789"
        mock_agent_service.delete_agent_document.return_value = {
            "success": True,
            "document_id": document_id,
            "mongo_deleted": True
        }

        # Act
        client.delete(f"/agents/{agent_id}/documents/{document_id}")

        # Assert
        mock_agent_service.delete_agent_document.assert_called_once_with(
            agent_id=agent_id,
            document_id=document_id,
            user_id=mock_current_user.id
        )

    def test_should_return_404_when_document_not_found(
        self, client: TestClient, mock_agent_service: Mock
    ):
        """Deve retornar 404 quando documento não for encontrado"""
        # Arrange
        agent_id = "agent-123"
        document_id = "nonexistent-doc"
        mock_agent_service.delete_agent_document.side_effect = ValueError("Documento não encontrado")

        # Act
        response = client.delete(f"/agents/{agent_id}/documents/{document_id}")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_should_return_404_when_agent_not_found(
        self, client: TestClient, mock_agent_service: Mock
    ):
        """Deve retornar 404 quando agente não for encontrado"""
        # Arrange
        agent_id = "nonexistent-agent"
        document_id = "doc-789"
        mock_agent_service.delete_agent_document.side_effect = ValueError("Agente não encontrado")

        # Act
        response = client.delete(f"/agents/{agent_id}/documents/{document_id}")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateAgentDocumentMetadata:
    """Testes para PATCH /agents/{agent_id}/documents/{document_id}/metadata"""

    @pytest.fixture(autouse=True)
    def setup(self, mock_current_user, mock_agent_service):
        """Setup para cada teste"""
        with patch("api.agents_api.get_current_user", return_value=mock_current_user), \
             patch("api.agents_api.get_agent_service", return_value=mock_agent_service):
            yield

    def test_should_return_200_when_metadata_updated_successfully(
        self, client: TestClient, mock_agent_service: Mock
    ):
        """Deve retornar 200 quando metadados forem atualizados com sucesso"""
        # Arrange
        agent_id = "agent-123"
        document_id = "doc-789"
        metadata_updates = {"author": "Updated Author", "tags": ["ai", "ml"]}
        mock_agent_service.update_agent_document_metadata.return_value = {
            "success": True,
            "document": {
                "id": document_id,
                "file_name": "documento.pdf",
                "metadata": metadata_updates,
                "created_at": datetime(2025, 1, 1, 10, 0, 0)
            }
        }

        # Act
        response = client.patch(
            f"/agents/{agent_id}/documents/{document_id}/metadata",
            json={"metadata": metadata_updates}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == document_id
        assert data["metadata"] == metadata_updates

    def test_should_call_service_with_correct_parameters(
        self, client: TestClient, mock_agent_service: Mock, mock_current_user: UserEntity
    ):
        """Deve chamar service com parâmetros corretos"""
        # Arrange
        agent_id = "agent-123"
        document_id = "doc-789"
        metadata_updates = {"category": "research"}
        mock_agent_service.update_agent_document_metadata.return_value = {
            "success": True,
            "document": {"id": document_id, "metadata": metadata_updates}
        }

        # Act
        client.patch(
            f"/agents/{agent_id}/documents/{document_id}/metadata",
            json={"metadata": metadata_updates}
        )

        # Assert
        mock_agent_service.update_agent_document_metadata.assert_called_once_with(
            agent_id=agent_id,
            document_id=document_id,
            user_id=mock_current_user.id,
            metadata_updates=metadata_updates
        )

    def test_should_return_404_when_document_not_found(
        self, client: TestClient, mock_agent_service: Mock
    ):
        """Deve retornar 404 quando documento não for encontrado"""
        # Arrange
        agent_id = "agent-123"
        document_id = "nonexistent-doc"
        mock_agent_service.update_agent_document_metadata.side_effect = ValueError(
            "Documento não encontrado"
        )

        # Act
        response = client.patch(
            f"/agents/{agent_id}/documents/{document_id}/metadata",
            json={"metadata": {"key": "value"}}
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestExecuteSystemAgent:
    """Testes para POST /agents/system/{agent_id}/execute"""

    @pytest.fixture(autouse=True)
    def setup(self, mock_current_user, mock_agent_service):
        """Setup para cada teste"""
        with patch("api.agents_api.get_current_user", return_value=mock_current_user), \
             patch("api.agents_api.get_agent_service", return_value=mock_agent_service):
            yield

    def test_should_return_200_when_executed_with_json_payload(
        self, client: TestClient, mock_agent_service: Mock
    ):
        """Deve retornar 200 quando executado com payload JSON"""
        # Arrange
        agent_id = "system-agent-123"
        mock_agent_service.execute_system_agent.return_value = {
            "message": "Test message",
            "response": "Agent response",
            "execution_time": 1.5,
            "tokens_used": 100,
            "session_id": "session-abc"
        }

        # Act
        response = client.post(
            f"/agents/system/{agent_id}/execute",
            json={"message": "Test message", "session_id": "session-abc"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["agent_id"] == agent_id
        assert data["message"] == "Test message"
        assert data["response"] == "Agent response"

    def test_should_delegate_file_processing_to_service(
        self, client: TestClient, mock_agent_service: Mock
    ):
        """Deve delegar processamento de arquivo para o service"""
        # Arrange
        agent_id = "system-agent-123"
        file_content = b"audio file content"
        mock_execute_request = AgentExecuteRequest(
            message="Transcreva este áudio",
            session_id="session-123",
            context={
                "file_content_base64": "base64encodedcontent",
                "file_name": "audio.mp3",
                "file_content_type": "audio/mpeg",
                "file_size": len(file_content),
                "has_file": True
            }
        )
        mock_agent_service.build_execute_request_from_file.return_value = mock_execute_request
        mock_agent_service.execute_system_agent.return_value = {
            "message": "Transcreva este áudio",
            "response": "Transcription result",
            "execution_time": 2.0,
            "tokens_used": 150,
            "session_id": "session-123"
        }

        # Act
        response = client.post(
            f"/agents/system/{agent_id}/execute",
            files={"file": ("audio.mp3", BytesIO(file_content), "audio/mpeg")},
            data={"message": "Custom message", "session_id": "session-123"}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        mock_agent_service.build_execute_request_from_file.assert_called_once()
        call_args = mock_agent_service.build_execute_request_from_file.call_args
        assert call_args.kwargs["file_content"] == file_content
        assert call_args.kwargs["file_name"] == "audio.mp3"
        assert call_args.kwargs["content_type"] == "audio/mpeg"
        assert call_args.kwargs["message"] == "Custom message"
        assert call_args.kwargs["session_id"] == "session-123"

    def test_should_call_execute_system_agent_with_built_request(
        self, client: TestClient, mock_agent_service: Mock, mock_current_user: UserEntity
    ):
        """Deve chamar execute_system_agent com request construído"""
        # Arrange
        agent_id = "system-agent-123"
        file_content = b"file content"
        mock_execute_request = AgentExecuteRequest(
            message="Processe este arquivo",
            session_id=None,
            context={"has_file": True}
        )
        mock_agent_service.build_execute_request_from_file.return_value = mock_execute_request
        mock_agent_service.execute_system_agent.return_value = {
            "message": "Processe este arquivo",
            "response": "Processing result",
            "execution_time": 1.0,
            "tokens_used": 50,
            "session_id": None
        }

        # Act
        client.post(
            f"/agents/system/{agent_id}/execute",
            files={"file": ("document.pdf", BytesIO(file_content), "application/pdf")}
        )

        # Assert
        mock_agent_service.execute_system_agent.assert_called_once_with(
            agent_id, mock_execute_request, mock_current_user.id
        )

    def test_should_return_400_when_neither_json_nor_file_provided(
        self, client: TestClient, mock_agent_service: Mock
    ):
        """Deve retornar 400 quando nem JSON nem arquivo forem fornecidos"""
        # Arrange
        agent_id = "system-agent-123"

        # Act
        response = client.post(f"/agents/system/{agent_id}/execute")

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "message" in response.json()["detail"] or "file" in response.json()["detail"]

    def test_should_return_404_when_system_agent_not_found(
        self, client: TestClient, mock_agent_service: Mock
    ):
        """Deve retornar 404 quando agente de sistema não for encontrado"""
        # Arrange
        agent_id = "nonexistent-system-agent"
        mock_agent_service.execute_system_agent.side_effect = ValueError(
            "Agente de sistema não encontrado ou inativo"
        )

        # Act
        response = client.post(
            f"/agents/system/{agent_id}/execute",
            json={"message": "Test message"}
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_should_handle_audio_file_upload(
        self, client: TestClient, mock_agent_service: Mock
    ):
        """Deve lidar com upload de arquivo de áudio"""
        # Arrange
        agent_id = "system-agent-123"
        audio_content = b"audio data"
        mock_execute_request = AgentExecuteRequest(
            message="Transcreva este áudio",
            context={"has_file": True, "file_content_type": "audio/mpeg"}
        )
        mock_agent_service.build_execute_request_from_file.return_value = mock_execute_request
        mock_agent_service.execute_system_agent.return_value = {
            "message": "Transcreva este áudio",
            "response": "Audio transcription",
            "execution_time": 3.0,
            "tokens_used": 200,
            "session_id": None
        }

        # Act
        response = client.post(
            f"/agents/system/{agent_id}/execute",
            files={"file": ("audio.mp3", BytesIO(audio_content), "audio/mpeg")}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK

    def test_should_handle_image_file_upload(
        self, client: TestClient, mock_agent_service: Mock
    ):
        """Deve lidar com upload de arquivo de imagem"""
        # Arrange
        agent_id = "system-agent-123"
        image_content = b"image data"
        mock_execute_request = AgentExecuteRequest(
            message="Extraia o texto desta imagem",
            context={"has_file": True, "file_content_type": "image/png"}
        )
        mock_agent_service.build_execute_request_from_file.return_value = mock_execute_request
        mock_agent_service.execute_system_agent.return_value = {
            "message": "Extraia o texto desta imagem",
            "response": "Extracted text",
            "execution_time": 2.5,
            "tokens_used": 120,
            "session_id": None
        }

        # Act
        response = client.post(
            f"/agents/system/{agent_id}/execute",
            files={"file": ("image.png", BytesIO(image_content), "image/png")}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
