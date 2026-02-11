"""
Testes unitários para AgentService
Camada: Service (Unit - Repository Mocked)
Estratégia: Testa lógica de orquestração com mocks de todos os repositories

Testa o novo método adicionado na refatoração:
- build_execute_request_from_file()
"""
import pytest
from unittest.mock import Mock, MagicMock
import base64
from typing import Optional

from services.agent_service import AgentService
from schemas.agents.requests import AgentExecuteRequest


class TestBuildExecuteRequestFromFile:
    """Testes para AgentService.build_execute_request_from_file()"""

    @pytest.fixture
    def mock_db(self):
        """Mock da sessão do banco de dados"""
        return Mock()

    @pytest.fixture
    def mock_ai_service(self):
        """Mock do AIService"""
        return Mock()

    @pytest.fixture
    def mock_vector_db_client(self):
        """Mock do VectorDBClient"""
        return Mock()

    @pytest.fixture
    def agent_service(self, mock_db, mock_ai_service, mock_vector_db_client):
        """Instância do AgentService com dependências mockadas"""
        return AgentService(
            db=mock_db,
            ai_service=mock_ai_service,
            vector_db_client=mock_vector_db_client
        )

    def test_should_build_request_for_audio_file_with_default_message(
        self, agent_service: AgentService, file_content: bytes, file_name: str
    ):
        """Deve construir request para arquivo de áudio com mensagem padrão"""
        # Arrange
        content_type = "audio/mpeg"

        # Act
        result = agent_service.build_execute_request_from_file(
            file_content=file_content,
            file_name=file_name,
            content_type=content_type,
            message=None,
            session_id=None
        )

        # Assert
        assert isinstance(result, AgentExecuteRequest)
        assert result.message == "Transcreva este áudio"
        assert result.session_id is None
        assert result.context is not None
        assert result.context["file_name"] == file_name
        assert result.context["file_content_type"] == content_type
        assert result.context["file_size"] == len(file_content)
        assert result.context["has_file"] is True
        assert "file_content_base64" in result.context

    def test_should_build_request_for_video_file_with_default_message(
        self, agent_service: AgentService, file_content: bytes, file_name: str
    ):
        """Deve construir request para arquivo de vídeo com mensagem padrão"""
        # Arrange
        content_type = "video/mp4"

        # Act
        result = agent_service.build_execute_request_from_file(
            file_content=file_content,
            file_name=file_name,
            content_type=content_type
        )

        # Assert
        assert result.message == "Transcreva este vídeo"
        assert result.context["file_content_type"] == content_type

    def test_should_build_request_for_image_file_with_default_message(
        self, agent_service: AgentService, file_content: bytes, file_name: str
    ):
        """Deve construir request para arquivo de imagem com mensagem padrão"""
        # Arrange
        content_type = "image/png"

        # Act
        result = agent_service.build_execute_request_from_file(
            file_content=file_content,
            file_name=file_name,
            content_type=content_type
        )

        # Assert
        assert result.message == "Extraia o texto desta imagem"
        assert result.context["file_content_type"] == content_type

    def test_should_build_request_for_pdf_file_with_default_message(
        self, agent_service: AgentService, file_content: bytes, file_name: str
    ):
        """Deve construir request para arquivo PDF com mensagem padrão"""
        # Arrange
        content_type = "application/pdf"

        # Act
        result = agent_service.build_execute_request_from_file(
            file_content=file_content,
            file_name=file_name,
            content_type=content_type
        )

        # Assert
        assert result.message == "Processe este PDF"
        assert result.context["file_content_type"] == content_type

    def test_should_use_generic_message_for_unknown_content_type(
        self, agent_service: AgentService, file_content: bytes, file_name: str
    ):
        """Deve usar mensagem genérica para tipo de arquivo desconhecido"""
        # Arrange
        content_type = "application/octet-stream"

        # Act
        result = agent_service.build_execute_request_from_file(
            file_content=file_content,
            file_name=file_name,
            content_type=content_type
        )

        # Assert
        assert result.message == "Processe este arquivo"

    def test_should_use_generic_message_when_content_type_is_none(
        self, agent_service: AgentService, file_content: bytes, file_name: str
    ):
        """Deve usar mensagem genérica quando content_type for None"""
        # Act
        result = agent_service.build_execute_request_from_file(
            file_content=file_content,
            file_name=file_name,
            content_type=None
        )

        # Assert
        assert result.message == "Processe este arquivo"

    def test_should_use_generic_message_when_content_type_is_empty(
        self, agent_service: AgentService, file_content: bytes, file_name: str
    ):
        """Deve usar mensagem genérica quando content_type for string vazia"""
        # Act
        result = agent_service.build_execute_request_from_file(
            file_content=file_content,
            file_name=file_name,
            content_type=""
        )

        # Assert
        assert result.message == "Processe este arquivo"

    def test_should_use_custom_message_when_provided(
        self, agent_service: AgentService, file_content: bytes, file_name: str
    ):
        """Deve usar mensagem customizada quando fornecida"""
        # Arrange
        custom_message = "Analise este documento e extraia insights"
        content_type = "application/pdf"

        # Act
        result = agent_service.build_execute_request_from_file(
            file_content=file_content,
            file_name=file_name,
            content_type=content_type,
            message=custom_message
        )

        # Assert
        assert result.message == custom_message

    def test_should_encode_file_content_to_base64(
        self, agent_service: AgentService, file_content: bytes, file_name: str
    ):
        """Deve codificar conteúdo do arquivo em base64"""
        # Act
        result = agent_service.build_execute_request_from_file(
            file_content=file_content,
            file_name=file_name,
            content_type="application/pdf"
        )

        # Assert
        expected_base64 = base64.b64encode(file_content).decode('utf-8')
        assert result.context["file_content_base64"] == expected_base64

    def test_should_calculate_file_size_correctly(
        self, agent_service: AgentService, file_name: str
    ):
        """Deve calcular tamanho do arquivo corretamente"""
        # Arrange
        file_content = b"This is a test file with some content"

        # Act
        result = agent_service.build_execute_request_from_file(
            file_content=file_content,
            file_name=file_name,
            content_type="application/pdf"
        )

        # Assert
        assert result.context["file_size"] == len(file_content)
        assert result.context["file_size"] == 38

    def test_should_include_session_id_when_provided(
        self, agent_service: AgentService, file_content: bytes, file_name: str
    ):
        """Deve incluir session_id quando fornecido"""
        # Arrange
        session_id = "session-abc-123"

        # Act
        result = agent_service.build_execute_request_from_file(
            file_content=file_content,
            file_name=file_name,
            content_type="application/pdf",
            session_id=session_id
        )

        # Assert
        assert result.session_id == session_id

    def test_should_set_session_id_to_none_when_not_provided(
        self, agent_service: AgentService, file_content: bytes, file_name: str
    ):
        """Deve definir session_id como None quando não fornecido"""
        # Act
        result = agent_service.build_execute_request_from_file(
            file_content=file_content,
            file_name=file_name,
            content_type="application/pdf"
        )

        # Assert
        assert result.session_id is None

    def test_should_set_has_file_flag_to_true(
        self, agent_service: AgentService, file_content: bytes, file_name: str
    ):
        """Deve definir flag has_file como True"""
        # Act
        result = agent_service.build_execute_request_from_file(
            file_content=file_content,
            file_name=file_name,
            content_type="application/pdf"
        )

        # Assert
        assert result.context["has_file"] is True

    def test_should_handle_audio_subtypes_correctly(
        self, agent_service: AgentService, file_content: bytes, file_name: str
    ):
        """Deve lidar corretamente com subtipos de áudio"""
        # Arrange
        audio_types = ["audio/mpeg", "audio/wav", "audio/ogg", "audio/mp3"]

        for content_type in audio_types:
            # Act
            result = agent_service.build_execute_request_from_file(
                file_content=file_content,
                file_name=file_name,
                content_type=content_type
            )

            # Assert
            assert result.message == "Transcreva este áudio", f"Failed for {content_type}"

    def test_should_handle_video_subtypes_correctly(
        self, agent_service: AgentService, file_content: bytes, file_name: str
    ):
        """Deve lidar corretamente com subtipos de vídeo"""
        # Arrange
        video_types = ["video/mp4", "video/mpeg", "video/avi", "video/quicktime"]

        for content_type in video_types:
            # Act
            result = agent_service.build_execute_request_from_file(
                file_content=file_content,
                file_name=file_name,
                content_type=content_type
            )

            # Assert
            assert result.message == "Transcreva este vídeo", f"Failed for {content_type}"

    def test_should_handle_image_subtypes_correctly(
        self, agent_service: AgentService, file_content: bytes, file_name: str
    ):
        """Deve lidar corretamente com subtipos de imagem"""
        # Arrange
        image_types = ["image/png", "image/jpeg", "image/gif", "image/webp"]

        for content_type in image_types:
            # Act
            result = agent_service.build_execute_request_from_file(
                file_content=file_content,
                file_name=file_name,
                content_type=content_type
            )

            # Assert
            assert result.message == "Extraia o texto desta imagem", f"Failed for {content_type}"

    def test_should_handle_uppercase_content_type(
        self, agent_service: AgentService, file_content: bytes, file_name: str
    ):
        """Deve lidar com content_type em maiúsculas"""
        # Arrange
        content_type = "AUDIO/MPEG"

        # Act
        result = agent_service.build_execute_request_from_file(
            file_content=file_content,
            file_name=file_name,
            content_type=content_type
        )

        # Assert
        assert result.message == "Transcreva este áudio"

    def test_should_handle_mixed_case_content_type(
        self, agent_service: AgentService, file_content: bytes, file_name: str
    ):
        """Deve lidar com content_type em caixa mista"""
        # Arrange
        content_type = "Image/PNG"

        # Act
        result = agent_service.build_execute_request_from_file(
            file_content=file_content,
            file_name=file_name,
            content_type=content_type
        )

        # Assert
        assert result.message == "Extraia o texto desta imagem"

    def test_should_handle_empty_file_content(
        self, agent_service: AgentService, file_name: str
    ):
        """Deve lidar com conteúdo de arquivo vazio"""
        # Arrange
        empty_content = b""

        # Act
        result = agent_service.build_execute_request_from_file(
            file_content=empty_content,
            file_name=file_name,
            content_type="application/pdf"
        )

        # Assert
        assert result.context["file_size"] == 0
        assert result.context["file_content_base64"] == ""

    def test_should_handle_large_file_content(
        self, agent_service: AgentService, file_name: str
    ):
        """Deve lidar com arquivos grandes"""
        # Arrange
        large_content = b"x" * (1024 * 1024)  # 1MB

        # Act
        result = agent_service.build_execute_request_from_file(
            file_content=large_content,
            file_name=file_name,
            content_type="application/pdf"
        )

        # Assert
        assert result.context["file_size"] == 1024 * 1024
        expected_base64 = base64.b64encode(large_content).decode('utf-8')
        assert result.context["file_content_base64"] == expected_base64

    def test_should_preserve_file_name_in_context(
        self, agent_service: AgentService, file_content: bytes
    ):
        """Deve preservar nome do arquivo no contexto"""
        # Arrange
        file_name = "documento_importante.pdf"

        # Act
        result = agent_service.build_execute_request_from_file(
            file_content=file_content,
            file_name=file_name,
            content_type="application/pdf"
        )

        # Assert
        assert result.context["file_name"] == file_name

    def test_should_create_valid_agent_execute_request(
        self, agent_service: AgentService, file_content: bytes, file_name: str
    ):
        """Deve criar um AgentExecuteRequest válido"""
        # Act
        result = agent_service.build_execute_request_from_file(
            file_content=file_content,
            file_name=file_name,
            content_type="application/pdf",
            message="Analise este documento",
            session_id="session-123"
        )

        # Assert - Validação Pydantic passa sem exceções
        assert result.message == "Analise este documento"
        assert result.session_id == "session-123"
        assert isinstance(result.context, dict)
        assert len(result.context) == 5  # Deve ter exatamente 5 campos no contexto
