from integration.pydanticIA.repository.metadata_repository import PydanticAIRepository
from schemas.metadata.request import MetadataPDFRequest, MetadataStringRequest

class MetadataService:
    def __init__(self):
        # Inicializa o serviço PydanticAIRepository, que será usado para criar metadados
        self.pydantic_service = PydanticAIRepository()

    async def extract_metadata(self, trecho_pdf: MetadataPDFRequest):
        """
        Extrai metadados de um arquivo PDF.

        Args:
            trecho_pdf (MetadataPDFRequest): Objeto contendo os dados do PDF para extração de metadados.

        Returns:
            metadadosResponse: Resposta do serviço PydanticAI contendo os metadados extraídos.
        """
        # Lógica para processar o arquivo PDF e extrair metadados usando PydanticAI
        # Por exemplo, converter o PDF em texto e chamar o serviço PydanticAI
        metadadosResponse = await self.pydantic_service.create_metadata(trecho_pdf)

        return metadadosResponse
    
    async def extract_metadata(self, trecho_pdf: MetadataStringRequest):
        """
        Extrai metadados de uma string content

        Args:
            trecho_pdf (MetadataStringRequest): Objeto contendo os dados em formato de string para extração de metadados.

        Returns:
            metadadosResponse: Resposta do serviço PydanticAI contendo os metadados extraídos.
        """
        # Lógica para processar o arquivo PDF e extrair metadados usando PydanticAI
        # Por exemplo, converter o PDF em texto e chamar o serviço PydanticAI
        metadadosResponse = await self.pydantic_service.create_metadata(trecho_pdf)

        return metadadosResponse
