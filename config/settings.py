"""
Configurações do sistema
Seguindo padrão IT Valley Architecture
"""
import os
from typing import Optional, Union
from dotenv import load_dotenv

# Carrega o arquivo .env
load_dotenv()


class Settings:
    """
    Configurações do sistema
    """
    
    # Aplicação
    app_name: str = "EmployeeVirtual"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    fastapi_debug: bool = os.getenv("FASTAPI_DEBUG", "false").lower() == "true"
    fastapi_env: str = os.getenv("FASTAPI_ENV", "development")
    port: int = int(os.getenv("PORT", "8000"))
    
    # Banco de dados
    database_url: str = os.getenv("AZURE_SQL_CONNECTION_STRING", "sqlite:///./employeevirtual.db")
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    mongodb_database: str = os.getenv("MONGODB_DATABASE", "mongoemploye")
    
    # JWT
    secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
    algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_expire_days: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    jwt_issuer: str = os.getenv("JWT_ISSUER", "EmployeeVirtual")
    
    # IA
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    orion_api_key: Optional[str] = os.getenv("ORION_API_KEY")
    
    # Integrações
    ai_service_url: str = os.getenv("AI_SERVICE_URL", "https://api.ai-service.com")
    ai_service_api_key: Optional[str] = os.getenv("AI_SERVICE_API_KEY")
    orion_api_url: str = os.getenv("ORION_API_URL", "http://localhost:8001")
    orion_api_key: Optional[str] = os.getenv("ORION_API_KEY")
    
    # CORS
    cors_origins: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(',')
    
    # ITValleySecurity SDK
    ev_token_source: str = os.getenv("EV_TOKEN_SOURCE", "auto")
    ev_cookie_access: str = os.getenv("EV_COOKIE_ACCESS", "access_token")
    ev_cookie_refresh: str = os.getenv("EV_COOKIE_REFRESH", "refresh_token")
    ev_sub_policy: str = os.getenv("EV_SUB_POLICY", "uuid")
    
    # Limites
    max_users_per_page: int = 100
    max_agents_per_user: int = 50
    max_flows_per_user: int = 100


# Instância global
settings = Settings()
