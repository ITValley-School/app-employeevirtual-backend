
from pydantic import BaseModel, Field



class MetadataPDFRequest(BaseModel):
    """
    Request de metadados.
    """
    arquio_pdf: bytes = Field(..., description="Arquivo PDF para extração de metadados")
    
class MetadataStringRequest(BaseModel):
    """
    Request de metadados.
    """
    arquio_pdf: str = Field(..., description="Arquivo PDF para extração de metadados")
    
  
