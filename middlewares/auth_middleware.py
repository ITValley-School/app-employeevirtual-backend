"""
Middleware de autenticação para o sistema EmployeeVirtual


***** ---> Nao estamos usando este middleware atualmente. Manter este código apenas para referência 

ou casos específicos onde autenticação por regras de negócio seja necessária.

"""



from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, List
import jwt
import os

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware para verificação de autenticação"""
    
    def __init__(self, app, secret_key: str = None, excluded_paths: List[str] = None):
        super().__init__(app)
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY", "your-secret-key")
        
        # Configuração flexível dos caminhos excluídos
        if excluded_paths is None:
            # Primeiro tenta ler do .env
            env_excluded = os.getenv("AUTH_EXCLUDED_PATHS", "")
            if env_excluded:
                excluded_paths = [path.strip() for path in env_excluded.split(",")]
            else:
                # Fallback para valores padrão
                excluded_paths = [
                    "/docs",
                    "/openapi.json",
                    "/health",
                    "/auth/login",
                    "/auth/register",
                    "/favicon.ico"
                ]
        
        self.excluded_paths = excluded_paths
    
    async def dispatch(self, request: Request, call_next: Callable):
        """
        Verifica autenticação antes de processar request
        
        Args:
            request: Request HTTP
            call_next: Próximo middleware/handler
            
        Returns:
            Response HTTP
            
        Raises:
            HTTPException: Se não autenticado
        """
        # Verificar se path está excluído
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Verificar token de autorização
        authorization = request.headers.get("Authorization")
        
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de autorização não fornecido"
            )
        
        try:
            # Extrair token
            scheme, token = authorization.split()
            
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Esquema de autorização inválido"
                )
            
            # Verificar token
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            # Adicionar dados do usuário ao request
            request.state.user_id = payload.get("user_id")
            request.state.user_email = payload.get("email")
            request.state.token = token
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Formato de autorização inválido"
            )
        
        return await call_next(request)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware para rate limiting
    
    NOTA: Este middleware não está sendo usado na aplicação.
    Rate limiting deve ser implementado na camada de infraestrutura:
    - Azure Application Gateway
    - Azure Front Door
    - Nginx/Apache (proxy reverso)
    - API Gateway services
    
    Manter este código apenas para referência ou casos específicos
    onde rate limiting por regras de negócio seja necessário.
    """
    
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # Em produção, usar Redis
    
    async def dispatch(self, request: Request, call_next: Callable):
        """
        Verifica rate limit antes de processar request
        
        Args:
            request: Request HTTP
            call_next: Próximo middleware/handler
            
        Returns:
            Response HTTP
            
        Raises:
            HTTPException: Se rate limit excedido
        """
        import time
        
        # Obter IP do cliente
        client_ip = request.client.host if request.client else "unknown"
        
        # Verificar rate limit
        current_time = time.time()
        window_start = current_time - self.window_seconds
        
        # Limpar requests antigos
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if req_time > window_start
            ]
        else:
            self.requests[client_ip] = []
        
        # Verificar se excedeu limite
        if len(self.requests[client_ip]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit excedido. Tente novamente mais tarde."
            )
        
        # Adicionar request atual
        self.requests[client_ip].append(current_time)
        
        # Processar request
        response = await call_next(request)
        
        # Adicionar headers de rate limit
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(
            self.max_requests - len(self.requests[client_ip])
        )
        response.headers["X-RateLimit-Reset"] = str(
            int(current_time + self.window_seconds)
        )
        
        return response

