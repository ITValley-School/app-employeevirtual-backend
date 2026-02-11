# Setup dos Testes

Este guia explica como configurar e executar os testes do projeto.

## 1. Instalação de Dependências

### Instalar dependências de teste
```bash
pip install -r requirements-test.txt
```

Ou instalar manualmente:
```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock httpx faker coverage
```

### Verificar instalação
```bash
pytest --version
```

Deve exibir algo como:
```
pytest 7.4.3
```

---

## 2. Estrutura de Diretórios

Certifique-se de que a estrutura está assim:

```
employeevirtual_backend/
├── api/
│   └── agents_api.py
├── services/
│   └── agent_service.py
├── mappers/
│   └── agent_mapper.py
├── schemas/
│   └── agents/
│       ├── requests.py
│       └── responses.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_agent_mapper.py
│   ├── test_agent_service.py
│   └── test_agents_api.py
├── main.py
└── pytest.ini
```

---

## 3. Executar os Testes

### Todos os testes
```bash
pytest
```

### Testes específicos por camada
```bash
# Mapper (transformações puras)
pytest tests/test_agent_mapper.py -v

# Service (lógica de orquestração)
pytest tests/test_agent_service.py -v

# API (endpoints HTTP)
pytest tests/test_agents_api.py -v
```

### Executar um teste específico
```bash
pytest tests/test_agent_mapper.py::TestAgentMapperToDocument::test_should_convert_dict_to_agent_document_response -v
```

### Executar testes por marcador
```bash
# Testes unitários
pytest -m unit

# Testes de mapper
pytest -m mapper

# Testes de API
pytest -m api
```

---

## 4. Cobertura de Código

### Gerar relatório de cobertura
```bash
pytest --cov=mappers --cov=services --cov=api --cov-report=term-missing
```

### Gerar relatório HTML
```bash
pytest --cov=mappers --cov=services --cov=api --cov-report=html
```

O relatório será gerado em `htmlcov/index.html`. Abra no navegador para visualizar.

---

## 5. Configurações do Pytest

O arquivo `pytest.ini` já está configurado com:
- ✅ Descoberta automática de testes
- ✅ Marcadores customizados (unit, integration, mapper, service, api)
- ✅ Configuração de cobertura
- ✅ Formato de saída verboso

---

## 6. Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'mappers'"
**Solução**: Certifique-se de executar os testes do diretório raiz do projeto:
```bash
cd C:\Projetos\Projetos Pessoais\employeevirtual_backend\employeevirtual_backend
pytest
```

### Erro: "No module named 'main'"
**Solução**: Verifique se o arquivo `main.py` existe no diretório raiz. Se o arquivo principal tiver outro nome, ajuste o import em `test_agents_api.py`:
```python
from seu_arquivo import app
```

### Erro: "fixture 'mock_current_user' not found"
**Solução**: Verifique se o arquivo `conftest.py` está presente no diretório `tests/`.

### Erro: Import de UserEntity falha
**Solução**: Ajuste o caminho de import conforme a estrutura do seu projeto. Exemplo:
```python
from data.entities.user_entities import UserEntity
# ou
from entities.user import UserEntity
```

### Testes de API falham com erro de autenticação
**Solução**: Os testes mockam a autenticação. Certifique-se de que o patch está correto:
```python
with patch("api.agents_api.get_current_user", return_value=mock_current_user):
    # testes aqui
```

O path deve ser onde a função é **usada** (no módulo da API), não onde é **definida**.

---

## 7. Executar no CI/CD

### GitHub Actions
Adicione ao `.github/workflows/tests.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: pytest --cov --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### GitLab CI
Adicione ao `.gitlab-ci.yml`:
```yaml
test:
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pip install -r requirements-test.txt
    - pytest --cov --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

---

## 8. Boas Práticas

### Antes de commitar
```bash
# Execute todos os testes
pytest

# Verifique cobertura
pytest --cov --cov-report=term-missing

# Execute apenas testes rápidos
pytest -m "not slow"
```

### Durante desenvolvimento
```bash
# Execute em modo watch (requer pytest-watch)
pip install pytest-watch
ptw

# Execute com breakpoint de debug
pytest --pdb

# Execute mostrando print statements
pytest -s
```

### Paralelização (para acelerar)
```bash
# Instale pytest-xdist
pip install pytest-xdist

# Execute testes em paralelo
pytest -n auto
```

---

## 9. Comandos Úteis

```bash
# Listar todos os testes sem executar
pytest --collect-only

# Executar apenas testes que falharam na última execução
pytest --lf

# Executar testes em ordem aleatória (detecta dependências)
pip install pytest-randomly
pytest

# Gerar relatório JSON
pytest --json-report --json-report-file=report.json

# Executar com timeout (requer pytest-timeout)
pip install pytest-timeout
pytest --timeout=10
```

---

## 10. Próximos Passos

Após validar que os testes estão funcionando:

1. ✅ Adicione mais testes conforme novos métodos forem criados
2. ✅ Configure CI/CD para executar testes automaticamente
3. ✅ Adicione badge de cobertura ao README principal
4. ✅ Implemente testes de Repository (com banco in-memory)
5. ✅ Implemente testes E2E (com banco real)

---

## Suporte

Em caso de dúvidas ou problemas:
1. Verifique este documento
2. Leia o `README.md` na pasta tests
3. Consulte a documentação oficial: https://docs.pytest.org/
