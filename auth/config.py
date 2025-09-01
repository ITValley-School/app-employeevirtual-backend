"""
Configurações de segurança - EmployeeVirtual
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Validações
if not JWT_SECRET_KEY or len(JWT_SECRET_KEY) < 32:
    raise ValueError("JWT_SECRET_KEY deve ter pelo menos 32 caracteres!")

# Configurações de cookies
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "True").lower() == "true"
COOKIE_SAMESITE = "strict"
COOKIE_HTTPONLY = True

# Constantes
JWT_ISSUER = "EmployeeVirtual"
JWT_TYPE_ACCESS = "access"
JWT_TYPE_REFRESH = "refresh"

# Ambiente
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

if ENVIRONMENT == "development":
    COOKIE_SECURE = False
    COOKIE_SAMESITE = "lax"

# Mensagens de erro
ERROR_MESSAGES = {
    "TOKEN_NOT_PROVIDED": "Token de acesso não fornecido",
    "TOKEN_INVALID": "Token inválido, expirado ou revogado", 
    "TOKEN_MALFORMED": "Token malformado",
    "USER_NOT_FOUND": "Usuário não encontrado ou inativo",
    "PREMIUM_REQUIRED": "Este recurso requer plano Premium ou Enterprise",
    "ADMIN_REQUIRED": "Acesso restrito a administradores"
}