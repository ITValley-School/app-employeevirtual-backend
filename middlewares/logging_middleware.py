"""
Middleware de logging para o sistema EmployeeVirtual
"""
import time
import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import logging

# Configurar logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de requests e responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Processa request e response com logging
        
        Args:
            request: Request HTTP
            call_next: Próximo middleware/handler
            
        Returns:
            Response HTTP
        """
        start_time = time.time()
        
        # Log do request
        logger.info(f"Request: {request.method} {request.url}")
        
        # Processar request
        response = await call_next(request)
        
        # Calcular tempo de processamento
        process_time = time.time() - start_time
        
        # Log do response
        logger.info(
            f"Response: {response.status_code} - "
            f"Time: {process_time:.4f}s - "
            f"Path: {request.url.path}"
        )
        
        # Adicionar header com tempo de processamento
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging detalhado de requests"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Processa request com logging detalhado
        
        Args:
            request: Request HTTP
            call_next: Próximo middleware/handler
            
        Returns:
            Response HTTP
        """
        start_time = time.time()
        
        # Capturar dados do request
        request_data = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "timestamp": time.time()
        }
        
        # Processar request
        try:
            response = await call_next(request)
            
            # Calcular tempo de processamento
            process_time = time.time() - start_time
            
            # Log de sucesso
            log_data = {
                **request_data,
                "status_code": response.status_code,
                "process_time": process_time,
                "success": True
            }
            
            # Log apenas para endpoints importantes
            if should_log_request(request.url.path):
                logger.info(f"API Request: {json.dumps(log_data)}")
            
            # Adicionar headers de resposta
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = str(int(start_time * 1000000))
            
            return response
            
        except Exception as e:
            # Log de erro
            process_time = time.time() - start_time
            
            log_data = {
                **request_data,
                "error": str(e),
                "process_time": process_time,
                "success": False
            }
            
            logger.error(f"API Error: {json.dumps(log_data)}")
            raise

def should_log_request(path: str) -> bool:
    """
    Determina se deve fazer log do request
    
    Args:
        path: Caminho da URL
        
    Returns:
        True se deve fazer log
    """
    # Não fazer log de endpoints de health check e estáticos
    skip_paths = ["/health", "/docs", "/openapi.json", "/favicon.ico"]
    
    return not any(path.startswith(skip_path) for skip_path in skip_paths)

