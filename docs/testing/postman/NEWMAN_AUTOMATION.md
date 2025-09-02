# Newman Test Automation Scripts

Este diretório contém scripts para executar os testes do Postman via linha de comando usando Newman.

## 📋 Pré-requisitos

### Instalar Newman
```bash
# Via npm (global)
npm install -g newman

# Via npm (local)
npm install newman

# Verificar instalação
newman --version
```

## 🚀 Scripts Disponíveis

### Teste Completo - Desenvolvimento
```bash
newman run EmployeeVirtual_Agents_API.postman_collection.json \
  -e EmployeeVirtual-Development.postman_environment.json \
  --reporters cli,html,json \
  --reporter-html-export newman-report.html \
  --reporter-json-export newman-report.json \
  --timeout-request 30000 \
  --delay-request 1000
```

### Teste Específico - Apenas Autenticação
```bash
newman run EmployeeVirtual_Agents_API.postman_collection.json \
  -e EmployeeVirtual-Development.postman_environment.json \
  --folder "🔐 Autenticação" \
  --reporters cli
```

### Teste de Smoke - Endpoints Críticos
```bash
newman run EmployeeVirtual_Agents_API.postman_collection.json \
  -e EmployeeVirtual-Development.postman_environment.json \
  --folder "🔐 Autenticação" \
  --folder "👤 Usuários" \
  --reporters cli,json \
  --reporter-json-export smoke-test.json
```

## 📊 Relatórios

### HTML Report
- Gera relatório visual completo
- Inclui gráficos e métricas
- Exportado como `newman-report.html`

### JSON Report
- Dados estruturados para análise
- Integrável com ferramentas de CI/CD
- Exportado como `newman-report.json`

### CLI Report
- Output direto no terminal
- Ideal para debugging rápido
- Mostra falhas em tempo real

## 🔧 Configurações Avançadas

### Timeout e Delays
```bash
--timeout-request 30000    # 30s timeout por request
--delay-request 1000       # 1s delay entre requests
--timeout-script 5000      # 5s timeout para scripts
```

### Variáveis de Ambiente
```bash
--env-var "baseUrl=http://localhost:8000"
--env-var "testEmail=custom@test.com"
```

### Dados Externos
```bash
--iteration-data test-data.json   # Dados para múltiplas iterações
--iteration-count 5               # Executar 5 vezes
```

## 📁 Exemplo de Estrutura CI/CD

### GitHub Actions
```yaml
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '16'
      - name: Install Newman
        run: npm install -g newman
      - name: Run API Tests
        run: |
          newman run docs/testing/postman/EmployeeVirtual_Agents_API.postman_collection.json \
            -e docs/testing/postman/EmployeeVirtual-Development.postman_environment.json \
            --reporters cli,json \
            --reporter-json-export newman-report.json
      - name: Upload Test Results
        uses: actions/upload-artifact@v2
        with:
          name: newman-report
          path: newman-report.json
```

### Azure DevOps
```yaml
- task: Npm@1
  displayName: 'Install Newman'
  inputs:
    command: 'custom'
    customCommand: 'install -g newman'

- task: CmdLine@2
  displayName: 'Run API Tests'
  inputs:
    script: |
      newman run docs/testing/postman/EmployeeVirtual_Agents_API.postman_collection.json \
        -e docs/testing/postman/EmployeeVirtual-Development.postman_environment.json \
        --reporters cli,json \
        --reporter-json-export $(Agent.TempDirectory)/newman-report.json

- task: PublishTestResults@2
  inputs:
    testResultsFormat: 'JUnit'
    testResultsFiles: '$(Agent.TempDirectory)/newman-report.json'
```

## 🔍 Análise de Resultados

### Métricas Importantes
- **Executed**: Total de requests executados
- **Failed**: Requests que falharam
- **Skipped**: Requests pulados
- **Test Scripts**: Scripts de teste executados
- **Assertions**: Validações realizadas

### Interpretação de Falhas
```bash
# Falha de conexão
"ECONNREFUSED" → Servidor não está rodando

# Falha de autenticação  
"401 Unauthorized" → Token inválido ou expirado

# Falha de validação
"422 Unprocessable Entity" → Dados de entrada inválidos

# Falha de script
"AssertionError" → Teste automatizado falhou
```

## 🛠️ Scripts Personalizados

### Windows PowerShell
```powershell
# run-tests.ps1
param(
    [string]$Environment = "Development",
    [string]$Collection = "EmployeeVirtual_Agents_API.postman_collection.json"
)

$envFile = "EmployeeVirtual-$Environment.postman_environment.json"
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$reportName = "newman-report-$timestamp"

newman run $Collection `
  -e $envFile `
  --reporters cli,html,json `
  --reporter-html-export "$reportName.html" `
  --reporter-json-export "$reportName.json" `
  --timeout-request 30000 `
  --delay-request 1000

Write-Host "Relatórios gerados:"
Write-Host "  HTML: $reportName.html"
Write-Host "  JSON: $reportName.json"
```

### Linux/Mac Bash
```bash
#!/bin/bash
# run-tests.sh

ENVIRONMENT=${1:-Development}
COLLECTION="EmployeeVirtual_Agents_API.postman_collection.json"
ENV_FILE="EmployeeVirtual-$ENVIRONMENT.postman_environment.json"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
REPORT_NAME="newman-report-$TIMESTAMP"

newman run "$COLLECTION" \
  -e "$ENV_FILE" \
  --reporters cli,html,json \
  --reporter-html-export "$REPORT_NAME.html" \
  --reporter-json-export "$REPORT_NAME.json" \
  --timeout-request 30000 \
  --delay-request 1000

echo "Relatórios gerados:"
echo "  HTML: $REPORT_NAME.html"
echo "  JSON: $REPORT_NAME.json"
```

## 📈 Monitoramento Contínuo

### Postman Monitoring
1. Importe a coleção no Postman web
2. Configure um monitor automático
3. Defina frequência (5min, 1h, 1d)
4. Configure alertas por email/Slack

### Custom Monitoring
```bash
# Cron job para executar testes a cada hora
0 * * * * /usr/local/bin/newman run /path/to/collection.json -e /path/to/environment.json --reporters json --reporter-json-export /var/log/api-tests.json
```

---

**Documentação Atualizada**: 2024-01-01
**Newman Version**: 5.x+
**Postman Collection Version**: 2.1.0
