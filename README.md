# EmployeeVirtual Backend

Sistema backend desenvolvido em Python com FastAPI para a plataforma EmployeeVirtual - Solução para criação e gerenciamento de agentes de IA, automações inteligentes e chat conversacional.

## Visão Geral

O EmployeeVirtual Backend é uma API REST que oferece funcionalidades para:

- **Agentes de IA Personalizados** - Criação, configuração e execução de agentes inteligentes
- **Automações (Flows)** - Sistema de workflows automatizados para processos complexos
- **Chat Inteligente** - Sistema de conversação com histórico e contexto
- **Dashboard e Métricas** - Análise de uso, produtividade e performance
- **Processamento de Arquivos** - Upload e processamento inteligente com IA
- **Integração Orion** - Serviços de IA prontos para uso empresarial
- **Autenticação JWT** - Sistema seguro de autenticação e autorização
- **Banco de Dados Híbrido** - Azure SQL + MongoDB para máxima flexibilidade

## Arquitetura IT Valley

Seguimos a **IT Valley Clean Architecture** com separação clara de responsabilidades:

### Estrutura de Camadas

```
api/           # Interface Externa (HTTP Controllers)
schemas/       # Contratos (DTOs de entrada e saída)
mappers/       # Tradutores (Entity -> Response)
services/      # Orquestradores (Business Logic)
factories/     # Fábricas (Criação de objetos)
domain/        # Coração do Sistema (Entidades + Regras)
data/          # Persistência (Repositories + Entities)
integrations/  # Integrações Externas (IA, APIs)
config/        # Configurações (Settings, Database)
```

### Estrutura de Pastas

```
employeevirtual_backend/
├── api/                    # Controllers HTTP (FastAPI)
│   ├── users_api.py       # API de usuários
│   ├── agents_api.py      # API de agentes
│   ├── flows_api.py       # API de flows
│   ├── chat_api.py        # API de chat
│   └── dashboard_api.py   # API de dashboard
├── schemas/               # Contratos de dados
│   ├── users/            # Schemas de usuários
│   ├── agents/           # Schemas de agentes
│   ├── flows/            # Schemas de flows
│   ├── chat/             # Schemas de chat
│   └── dashboard/        # Schemas de dashboard
├── mappers/              # Tradutores
│   ├── user_mapper.py    # User Entity -> User Response
│   ├── agent_mapper.py   # Agent Entity -> Agent Response
│   └── flow_mapper.py    # Flow Entity -> Flow Response
├── services/             # Lógica de negócio
│   ├── user_service.py   # Orquestração de usuários
│   ├── agent_service.py # Orquestração de agentes
│   └── flow_service.py   # Orquestração de flows
├── domain/               # Entidades do domínio
│   ├── users/           # Entidades de usuários
│   ├── agents/          # Entidades de agentes
│   └── flows/           # Entidades de flows
├── data/                # Acesso a dados
│   ├── entities/        # Entidades SQLAlchemy
│   ├── user_repository.py
│   ├── agent_repository.py
│   └── flow_repository.py
├── integrations/        # Integrações externas
│   └── ai/              # Integrações de IA
├── config/              # Configurações
│   ├── settings.py      # Configurações do sistema
│   └── database.py      # Configuração do banco
├── auth/                 # Autenticação
├── middlewares/         # Middlewares
└── main.py              # Aplicação principal
```

### Fluxo de Dados

**Requisição (de cima para baixo):**
1. API recebe requisição HTTP
2. Schemas validam dados de entrada
3. Service orquestra o processo
4. Factory cria objetos do domínio
5. Domain aplica regras de negócio
6. Repository salva no banco

**Resposta (de baixo para cima):**
1. Repository retorna dados
2. Domain processa regras
3. Service coordena retorno
4. Mapper converte para resposta
5. API retorna HTTP

## Tecnologias

### Core Framework
- **FastAPI** - Framework web moderno e rápido
- **Uvicorn** - Servidor ASGI de alta performance
- **Pydantic** - Validação de dados e serialização
- **PydanticAI** - Framework para agentes de IA

### Banco de Dados
- **SQLAlchemy** - ORM para Azure SQL
- **PyODBC** - Driver para SQL Server
- **PyMongo** - Driver para MongoDB
- **Motor** - Driver assíncrono para MongoDB

### Autenticação e Segurança
- **PyJWT** - Tokens JWT
- **Passlib** - Hash de senhas
- **Python-jose** - Criptografia JWT

## Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` com as seguintes configurações:

```bash
# Banco de Dados
AZURE_SQL_CONNECTION_STRING=mssql+pyodbc://user:pass@server:1433/database?driver=ODBC+Driver+18+for+SQL+Server
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=employeevirtual

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# IA
OPENAI_API_KEY=your-openai-key
ORION_API_KEY=your-orion-key
```

### Instalação

```bash
# Clone o repositório
git clone <repository-url>
cd employeevirtual_backend

# Crie um ambiente virtual
python -m venv env
source env/bin/activate  # Linux/Mac
# ou
env\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Execute o servidor
uvicorn main:app --reload
```

## Documentação da API

Após iniciar o servidor, acesse:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Módulos Implementados

### Usuários
- Registro e autenticação
- Gestão de perfis
- Controle de acesso

### Agentes
- Criação de agentes de IA
- Configuração de modelos
- Execução e monitoramento

### Flows (Em desenvolvimento)
- Criação de workflows
- Automação de processos
- Execução programada

### Chat (Em desenvolvimento)
- Sistema de conversação
- Histórico de mensagens
- Contexto de conversas

### Dashboard (Em desenvolvimento)
- Métricas de uso
- Análise de performance
- Relatórios gerenciais

## Desenvolvimento

### Estrutura de Commits

```
feat: nova funcionalidade
fix: correção de bug
docs: documentação
style: formatação
refactor: refatoração
test: testes
chore: tarefas de manutenção
```

### Padrões de Código

- Seguir a arquitetura IT Valley
- Usar type hints em todas as funções
- Documentar todas as funções públicas
- Escrever testes para novas funcionalidades
- Manter cobertura de testes acima de 80%

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.