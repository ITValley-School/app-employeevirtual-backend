# Guia de Instalação - EmployeeVirtual Backend

Este guia fornece instruções detalhadas para instalar e configurar o backend do sistema EmployeeVirtual.

## 📋 Pré-requisitos

### Sistema Operacional
- Windows 10/11, macOS 10.15+, ou Linux (Ubuntu 18.04+)
- Python 3.11 ou superior

### Banco de Dados
- **SQL Server/Azure SQL Database** (obrigatório)
- **MongoDB** (opcional, para cache e logs)

### Drivers e Ferramentas
- ODBC Driver 17 for SQL Server
- Git (para clonar o repositório)

## 🔧 Instalação Passo a Passo

### 1. Preparação do Ambiente

#### 1.1 Instalar Python 3.11+
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv

# macOS (com Homebrew)
brew install python@3.11

# Windows
# Baixe e instale do site oficial: https://python.org
```

#### 1.2 Instalar ODBC Driver para SQL Server
```bash
# Ubuntu/Debian
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/msprod.list
sudo apt update
sudo apt install msodbcsql17 unixodbc-dev

# macOS
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql17 mssql-tools

# Windows
# Baixe e instale: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
```

### 2. Configuração do Projeto

#### 2.1 Clonar o Repositório
```bash
git clone <repository-url>
cd employeevirtual_backend
```

#### 2.2 Criar Ambiente Virtual
```bash
python3.11 -m venv venv

# Ativar ambiente virtual
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 2.3 Instalar Dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configuração do Banco de Dados

#### 3.1 SQL Server/Azure SQL Database

1. **Criar banco de dados**
```sql
CREATE DATABASE EmployeeVirtual;
```

2. **Criar schema**
```sql
USE EmployeeVirtual;
CREATE SCHEMA empl;
```

3. **Configurar usuário** (se necessário)
```sql
CREATE LOGIN employeevirtual_user WITH PASSWORD = 'SuaSenhaSegura123!';
USE EmployeeVirtual;
CREATE USER employeevirtual_user FOR LOGIN employeevirtual_user;
ALTER ROLE db_owner ADD MEMBER employeevirtual_user;
```

#### 3.2 MongoDB (Opcional)

1. **Instalar MongoDB**
```bash
# Ubuntu
sudo apt install mongodb

# macOS
brew install mongodb-community

# Windows
# Baixe e instale: https://www.mongodb.com/try/download/community
```

2. **Iniciar serviço**
```bash
# Ubuntu
sudo systemctl start mongodb

# macOS
brew services start mongodb-community

# Windows
# Inicie o serviço MongoDB pelo Services.msc
```

### 4. Configuração de Variáveis de Ambiente

#### 4.1 Copiar arquivo de exemplo
```bash
cp .env.example .env
```

#### 4.2 Editar configurações
```bash
nano .env  # ou use seu editor preferido
```

#### 4.3 Configurações obrigatórias

**Banco de dados SQL Azure:**
```env
DATABASE_URL=mssql+pyodbc://username:password@server.database.windows.net:1433/EmployeeVirtual?driver=ODBC+Driver+17+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no&Connection+Timeout=30
```

**Autenticação:**
```env
JWT_SECRET_KEY=sua-chave-secreta-muito-segura-aqui-com-pelo-menos-32-caracteres
```

**Servidor:**
```env
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

#### 4.4 Configurações opcionais

**MongoDB:**
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=employeevirtual
```

**Orion (serviços de IA):**
```env
ORION_BASE_URL=https://sua-instancia-orion.com
ORION_API_KEY=sua-chave-api-orion
```

### 5. Inicialização

#### 5.1 Verificar configuração
```bash
python -c "from data.database import get_connection_info; print(get_connection_info())"
```

#### 5.2 Criar tabelas
```bash
python -c "from data.database import create_tables; create_tables(); print('Tabelas criadas com sucesso!')"
```

#### 5.3 Iniciar aplicação
```bash
python main.py
```

A aplicação estará disponível em:
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs

## 🧪 Verificação da Instalação

### 1. Health Check
```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "services": {
    "sql_database": {"status": "connected"},
    "mongodb": {"status": "connected"}
  }
}
```

### 2. Criar usuário de teste
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Usuário Teste",
    "email": "teste@example.com",
    "password": "senha123"
  }'
```

### 3. Fazer login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "password": "senha123"
  }'
```

## 🚀 Deploy em Produção

### 1. Azure App Service

#### 1.1 Preparar aplicação
```bash
# Criar arquivo startup.txt
echo "python -m uvicorn main:app --host 0.0.0.0 --port 8000" > startup.txt
```

#### 1.2 Configurar variáveis de ambiente no Azure
- Acesse o portal do Azure
- Vá para Configuration > Application settings
- Adicione todas as variáveis do arquivo .env

#### 1.3 Deploy
```bash
# Usando Azure CLI
az webapp up --name sua-app --resource-group seu-grupo
```

### 2. Docker

#### 2.1 Criar Dockerfile
```dockerfile
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar ODBC Driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2.2 Build e run
```bash
docker build -t employeevirtual-backend .
docker run -p 8000:8000 --env-file .env employeevirtual-backend
```

### 3. Kubernetes

#### 3.1 Criar deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: employeevirtual-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: employeevirtual-backend
  template:
    metadata:
      labels:
        app: employeevirtual-backend
    spec:
      containers:
      - name: backend
        image: employeevirtual-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: connection-string
---
apiVersion: v1
kind: Service
metadata:
  name: employeevirtual-service
spec:
  selector:
    app: employeevirtual-backend
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 🔧 Solução de Problemas

### Erro de conexão com SQL Server

**Problema:** `pyodbc.Error: ('01000', "[01000] [unixODBC][Driver Manager]Can't open lib 'ODBC Driver 17 for SQL Server'"`

**Solução:**
```bash
# Verificar drivers instalados
odbcinst -q -d

# Reinstalar driver
sudo apt-get purge msodbcsql17
sudo apt-get install msodbcsql17
```

### Erro de permissão no banco

**Problema:** `Login failed for user`

**Solução:**
1. Verificar credenciais no .env
2. Verificar permissões do usuário no banco
3. Verificar firewall do Azure SQL

### Erro de porta em uso

**Problema:** `OSError: [Errno 98] Address already in use`

**Solução:**
```bash
# Encontrar processo usando a porta
sudo lsof -i :8000

# Matar processo
sudo kill -9 <PID>

# Ou usar porta diferente
PORT=8001 python main.py
```

### Erro de dependências

**Problema:** `ModuleNotFoundError`

**Solução:**
```bash
# Verificar ambiente virtual ativo
which python

# Reinstalar dependências
pip install --force-reinstall -r requirements.txt
```

## 📞 Suporte

Para problemas não cobertos neste guia:

1. **Verifique os logs** da aplicação
2. **Consulte a documentação** em /docs
3. **Abra uma issue** no repositório
4. **Entre em contato** com o suporte técnico

## 🔄 Atualizações

Para atualizar o sistema:

```bash
# Parar aplicação
# Fazer backup do banco de dados
# Atualizar código
git pull origin main

# Atualizar dependências
pip install -r requirements.txt

# Executar migrações (se houver)
python -c "from data.database import create_tables; create_tables()"

# Reiniciar aplicação
python main.py
```

