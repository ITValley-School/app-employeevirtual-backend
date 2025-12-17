"""
Middleware de autenticação simples via API Key fixa
Para backends dedicados a um único cliente
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, List
from config.settings import settings


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Middleware para verificação de API Key fixa via header
    
    O frontend deve enviar o token no header:
    - X-API-Key: <token>
    ou
    - Authorization: Bearer <token>
    """
    
    def __init__(self, app, excluded_paths: List[str] = None):
        super().__init__(app)
        self.api_key = settings.api_key
        
        # Caminhos que não precisam de autenticação
        if excluded_paths is None:
            excluded_paths = [
                "/docs",
                "/openapi.json",
                "/redoc",
                "/health",
                "/favicon.ico"
            ]
        
        self.excluded_paths = excluded_paths
    
    async def dispatch(self, request: Request, call_next: Callable):
        """
        Verifica API Key antes de processar request
        
        Args:
            request: Request HTTP
            call_next: Próximo middleware/handler
            
        Returns:
            Response HTTP
            
        Raises:
            HTTPException: Se API Key inválida ou não fornecida
        """
        # Verificar se path está excluído
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Verificar se API Key está configurada
        if not self.api_key:
            # Se não estiver configurada, permite acesso (modo desenvolvimento)
            return await call_next(request)
        
        # Tentar obter token do header X-API-Key
        api_key = request.headers.get("X-API-Key")
        
        # Se não encontrar, tentar Authorization Bearer
        if not api_key:
            authorization = request.headers.get("Authorization", "")
            if authorization.startswith("Bearer "):
                api_key = authorization.replace("Bearer ", "").strip()
        
        # Verificar se token foi fornecido
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API Key não fornecida. Envie no header 'X-API-Key' ou 'Authorization: Bearer <token>'",
                headers={"WWW-Authenticate": "ApiKey"},
            )
        
        # Verificar se token é válido
        if api_key != self.api_key:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="API Key inválida",
                headers={"WWW-Authenticate": "ApiKey"},
            )
        
        # Token válido, continuar
        return await call_next(request)

