# IT Valley Tester - Agent Memory

## Projeto: employeevirtual_backend

### Tech Stack Identificado
- **Framework**: FastAPI + SQLAlchemy + Pydantic
- **Testing**: pytest (não estava instalado, configurado agora)
- **Estrutura**: Clean Architecture / IT Valley Pattern
- **Python**: 3.11+ (baseado em type hints modernos)

### Padrões de Teste Implementados

#### Estrutura de Diretórios
```
tests/
├── __init__.py
├── conftest.py          # Fixtures compartilhadas
├── test_agent_mapper.py # Mapper tests (no mocks)
├── test_agent_service.py # Service tests (repo mocked)
└── test_agents_api.py   # API tests (service mocked)
```

#### Nomenclatura de Testes
- Padrão: `test_should_<ação>_when_<condição>()`
- Classes: `TestNomeDoMetodo` ou `TestFuncionalidade`
- Docstrings em português: `"""Deve fazer X quando Y"""`

#### Fixtures Comuns (conftest.py)
- `agent_id`, `user_id` - IDs de exemplo
- `document_dict` - Dados de documento completo
- `upload_result_success` - Resultado de operação bem-sucedida
- `file_content`, `file_name` - Dados de arquivo
- Mock objects específicos por teste

#### Camadas e Estratégias

**Mapper (No Mocks)**:
- Testa transformações puras: Entity → Response, Dict → Response
- Valida campos opcionais, defaults, edge cases
- Sem dependências externas

**Service (Repository Mocked)**:
- Mock de: db, repository, vector_db_client, ai_service
- Testa orquestração, validações, chamadas corretas
- Valida tratamento de erros

**API (Service Mocked)**:
- Mock de: service, current_user (auth)
- Usa `TestClient` do FastAPI
- Valida: status codes, payloads, responses
- Testa multipart/form-data e JSON

#### Utilitários Encontrados
- `TestClient` do FastAPI para testes de API
- `unittest.mock.Mock` e `patch` para mocking
- `BytesIO` para simular uploads de arquivo
- Fixtures em pytest para reutilização

### Configuração do Projeto

#### pytest.ini
- testpaths = tests
- Marcadores: unit, integration, mapper, service, api
- Cobertura configurada para mappers, services, api

#### requirements-test.txt
- pytest==7.4.3
- pytest-asyncio, pytest-cov, pytest-mock
- httpx (para TestClient)
- faker, coverage

### Padrões Específicos deste Projeto

1. **Autenticação mockada via patch**:
```python
with patch("api.agents_api.get_current_user", return_value=mock_user):
    # testes aqui
```

2. **Service injetado via dependency**:
```python
with patch("api.agents_api.get_agent_service", return_value=mock_service):
```

3. **Estrutura de documento MongoDB**:
- Usa `_id` e `id` (conversão necessária)
- Campo `mongo_error` para indicar falhas parciais
- Campo `created_at` pode ser None (usar default)

4. **Responses sempre via Mapper**:
- API nunca monta dict manualmente
- Sempre chama `AgentMapper.to_*()` methods

5. **Upload de arquivos**:
- Multipart com campo `filepdf` (documentos)
- Multipart com campo `file` (system agent execute)
- Metadados em `metadone` (Form field, JSON string)

### Lições Aprendidas

1. FastAPI TestClient requer httpx instalado
2. Mock deve ser onde função é **usada**, não onde é **definida**
3. UserEntity tem campos específicos: id, email, name, password_hash, is_active, created_at
4. Service.build_execute_request_from_file() encapsula lógica de processamento de arquivo
5. Content-type deve ser tratado em lowercase (.lower())
6. Base64 encoding: `base64.b64encode(content).decode('utf-8')`

### Edge Cases Importantes

- Content-type em maiúsculas/minúsculas
- Arquivo vazio (size=0)
- Arquivo grande (1MB+)
- Campos None vs ausentes no dict
- MongoDB _id vs id
- Timestamps None (usar datetime.utcnow())
- Lista vazia vs lista com elementos
- mongo_error=True (warning no response)

### Comandos de Teste

```bash
# Instalação
pip install -r requirements-test.txt

# Execução
pytest                              # Todos
pytest tests/test_agent_mapper.py -v  # Camada específica
pytest -k "upload"                   # Por keyword
pytest --cov --cov-report=html      # Com cobertura

# Debug
pytest --pdb                         # Breakpoint on failure
pytest -s                            # Show prints
pytest -vv                           # Extra verbose
```

### Métricas deste Projeto

- 81 testes implementados
- 2635 linhas de código/documentação
- 3 camadas cobertas (Mapper, Service, API)
- ~1500 linhas de código de teste puro
