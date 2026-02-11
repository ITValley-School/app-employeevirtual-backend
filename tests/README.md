# Testes - Metodologia IT Valley

Esta suíte de testes segue rigorosamente a **metodologia IT Valley de testes em camadas**, com estratégias específicas de isolamento para cada camada da arquitetura.

## Estrutura de Testes

### 1. Mapper Tests (Unit - No Mocks)
**Arquivo**: `test_agent_mapper.py`

**Objetivo**: Validar transformações puras de dados entre diferentes representações (Entity → Response, Dict → Response).

**Estratégia**:
- ❌ **SEM MOCKS** - Testes completamente isolados
- ✅ Validação de transformação de dados
- ✅ Validação de tratamento de campos opcionais/nulos
- ✅ Validação de defaults e fallbacks

**Cobertura**:
- `AgentMapper.to_document()` - Conversão de dict para AgentDocumentResponse
- `AgentMapper.to_document_list()` - Conversão de lista de dicts para AgentDocumentListResponse
- `AgentMapper.to_document_delete()` - Conversão de resultado de deleção para AgentDocumentDeleteResponse
- `AgentMapper.to_upload_response()` - Formatação de resultado de upload

**Casos de teste**:
- ✅ Happy path com todos os campos preenchidos
- ✅ Campos ausentes (None, missing)
- ✅ Valores padrão aplicados corretamente
- ✅ Edge cases (listas vazias, IDs do MongoDB, timestamps)

---

### 2. Service Tests (Unit - Repository Mocked)
**Arquivo**: `test_agent_service.py`

**Objetivo**: Validar lógica de orquestração de negócio sem dependências de banco de dados ou APIs externas.

**Estratégia**:
- ✅ **MOCK de TODOS os repositories** (AgentRepository, VectorDBClient, etc.)
- ✅ Validação de chamadas corretas aos repositories
- ✅ Validação de lógica de transformação e orquestração
- ✅ Validação de tratamento de erros

**Cobertura**:
- `AgentService.build_execute_request_from_file()` - Construção de request a partir de arquivo multipart

**Casos de teste**:
- ✅ Detecção correta de content-type (audio, video, image, pdf)
- ✅ Mensagens padrão baseadas em tipo de arquivo
- ✅ Codificação base64 do conteúdo
- ✅ Preservação de metadados (file_name, file_size, content_type)
- ✅ Mensagens customizadas do usuário
- ✅ Edge cases (content-type em maiúsculas, arquivo vazio, arquivos grandes)

---

### 3. API Tests (Integration - Service Mocked)
**Arquivo**: `test_agents_api.py`

**Objetivo**: Validar comportamento HTTP (rotas, status codes, validação de request/response) sem executar lógica de negócio real.

**Estratégia**:
- ✅ **MOCK de TODOS os services** (AgentService)
- ✅ Uso do `TestClient` do FastAPI
- ✅ Validação de status codes HTTP
- ✅ Validação de estrutura de request/response
- ✅ Validação de autenticação e autorização
- ✅ Validação de tratamento de erros HTTP

**Cobertura**:
- `POST /agents/{agent_id}/documents` - Upload de documento
- `GET /agents/{agent_id}/documents` - Listagem de documentos
- `DELETE /agents/{agent_id}/documents/{document_id}` - Deleção de documento
- `PATCH /agents/{agent_id}/documents/{document_id}/metadata` - Atualização de metadados
- `POST /agents/system/{agent_id}/execute` - Execução de agente de sistema com arquivo

**Casos de teste**:
- ✅ Status codes corretos (200, 201, 400, 404, 500)
- ✅ Chamadas corretas ao service com parâmetros esperados
- ✅ Validação de payloads de entrada (JSON, multipart/form-data)
- ✅ Formatação correta de responses via Mapper
- ✅ Tratamento de erros (ValueError → 404, Exception → 500)
- ✅ Upload de diferentes tipos de arquivo (audio, image, pdf)

---

## Como Executar os Testes

### Executar todos os testes
```bash
pytest
```

### Executar testes de uma camada específica
```bash
# Mapper tests
pytest tests/test_agent_mapper.py

# Service tests
pytest tests/test_agent_service.py

# API tests
pytest tests/test_agents_api.py
```

### Executar com cobertura
```bash
pytest --cov=mappers --cov=services --cov=api --cov-report=html
```

### Executar testes específicos
```bash
# Por classe
pytest tests/test_agent_mapper.py::TestAgentMapperToDocument

# Por método
pytest tests/test_agent_mapper.py::TestAgentMapperToDocument::test_should_convert_dict_to_agent_document_response

# Por palavra-chave
pytest -k "upload"
```

### Modo verbose
```bash
pytest -v
pytest -vv  # Extra verbose
```

---

## Princípios IT Valley Aplicados

### ✅ Separação por Camada
Cada camada tem sua própria estratégia de teste isolada:
- **Mapper**: Sem mocks (transformações puras)
- **Service**: Repositories mockados (orquestração isolada)
- **API**: Services mockados (HTTP isolado)

### ✅ Mock Estratégico
- **NUNCA** mockamos na camada Mapper
- **SEMPRE** mockamos repositories na camada Service
- **SEMPRE** mockamos services na camada API

### ✅ Testes Comportamentais
- Nomes descritivos em português (ou inglês conforme projeto)
- Padrão "should_do_something_when_condition"
- Foco no comportamento esperado, não na implementação

### ✅ Arrange-Act-Assert
Todos os testes seguem estrutura clara:
```python
def test_should_do_something():
    # Arrange - Configuração
    input_data = {...}

    # Act - Execução
    result = function(input_data)

    # Assert - Verificação
    assert result.field == expected_value
```

### ✅ Cobertura de Edge Cases
- Valores nulos/ausentes
- Listas vazias
- Strings vazias
- Casos de fronteira (boundary conditions)
- Erros esperados

---

## Convenções de Nomenclatura

### Classes de Teste
```python
class TestNomeDaFuncaoOuMetodo:
    """Testes para NomeDaFuncaoOuMetodo"""
```

### Métodos de Teste
```python
def test_should_<acao_esperada>_when_<condicao>():
    """Deve <acao_esperada> quando <condicao>"""
```

Exemplos:
- `test_should_return_200_when_document_uploaded_successfully`
- `test_should_use_default_message_when_content_type_is_audio`
- `test_should_raise_value_error_when_agent_not_found`

---

## Fixtures Comuns

Fixtures reutilizáveis estão definidas em `conftest.py`:

- `agent_id` - ID de agente de exemplo
- `user_id` - ID de usuário de exemplo
- `document_dict` - Dicionário de documento completo
- `document_dict_with_mongo_error` - Documento com erro do MongoDB
- `upload_result_success` - Resultado de upload bem-sucedido
- `upload_result_with_mongo_error` - Resultado de upload com erro
- `delete_result_success` - Resultado de deleção bem-sucedido
- `file_content` - Conteúdo de arquivo de exemplo
- `file_name` - Nome de arquivo de exemplo

---

## Próximos Passos

### Testes Faltantes (Não Implementados Neste PR)
- [ ] Repository tests (com banco de dados in-memory)
- [ ] Domain/Factory tests (validação de regras de negócio)
- [ ] Testes E2E (com banco real e integrações externas)

### Melhorias Futuras
- [ ] Adicionar testes de performance
- [ ] Adicionar testes de carga
- [ ] Configurar CI/CD para executar testes automaticamente
- [ ] Adicionar badge de cobertura de código
- [ ] Adicionar testes de contrato (Pact/OpenAPI)

---

## Troubleshooting

### Erro: "No module named 'main'"
Os testes de API assumem que o app FastAPI está em `main.py`. Se o arquivo principal for diferente, ajuste o import em `test_agents_api.py`:
```python
from seu_arquivo_principal import app
```

### Erro: "get_current_user not found"
Certifique-se de que o path do patch está correto. Deve apontar para onde a função é **usada**, não onde é **definida**:
```python
patch("api.agents_api.get_current_user", return_value=mock_user)
```

### Testes passam localmente mas falham no CI
- Verifique versões de dependências (pytest, FastAPI, Pydantic)
- Verifique variáveis de ambiente necessárias
- Verifique timezone (use `datetime.utcnow()` para consistência)

---

## Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [IT Valley Architecture Patterns](https://itvalley.com.br)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
