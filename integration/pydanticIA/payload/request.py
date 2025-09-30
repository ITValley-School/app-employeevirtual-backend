# Um DTO com um unico campo que e o texto do usuario de forma de string
from pydantic import BaseModel, Field
from typing import Optional

class MetadataRequest(BaseModel):
    """
    Request de metadados.
    """
    # nao e opcional e obrigatorio recebe o texto em string 
    trecho_pdf_em_string: str = Field(..., description="Texto extraído do PDF para análise de metadados")
