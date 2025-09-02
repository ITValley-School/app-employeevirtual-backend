# 📁 Pasta de Testes - EmployeeVirtual API

Esta pasta contém todos os recursos necessários para testar a API do EmployeeVirtual de forma completa e sistemática.

## 📋 Conteúdo da Pasta

### 📖 Documentação Principal
- **`ROTEIRO_TESTES_COMPLETO.md`** - Guia completo de testes (513 linhas)
- **`QUICK_TEST_GUIDE.md`** - Guia rápido para validação (15 minutos)
- **`ROTEIRO_TESTES_PARA_PDF.html`** - Versão HTML otimizada para PDF

### 🔧 Scripts de Automação
- **`generate-pdf.ps1`** - Gera PDF do roteiro de testes
- **Exemplos de uso:**
  ```powershell
  .\generate-pdf.ps1                     # Gera PDF padrão
  .\generate-pdf.ps1 -OutputName "Custom" # Nome personalizado
  ```

### 📁 Subpastas

#### `postman/` - Coleção e Ambientes Postman
- **`EmployeeVirtual_Agents_API.postman_collection.json`** - Coleção completa
- **`EmployeeVirtual-Development.postman_environment.json`** - Ambiente de desenvolvimento
- **`EmployeeVirtual-Production.postman_environment.json`** - Ambiente de produção
- **`POSTMAN_SETUP_GUIDE.md`** - Guia de configuração detalhado
- **`NEWMAN_AUTOMATION.md`** - Documentação de automação
- **`README.md`** - Visão geral da pasta Postman
- **`run-tests.ps1`** - Script avançado de testes
- **`quick-test.bat`** - Script básico para Windows

## 🚀 Como Começar

### Opção 1: Teste Rápido (2 minutos)
```bash
# 1. Verificar servidor
curl http://localhost:8000/health

# 2. Teste automatizado básico
cd postman
.\quick-test.bat
```

### Opção 2: Setup Completo Postman (5 minutos)
```bash
# 1. Importar no Postman
# - Abra Postman → File → Import
# - Selecione todos os .json da pasta postman/

# 2. Configurar ambiente Development

# 3. Executar Collection Runner
```

### Opção 3: Automação Avançada (Newman)
```bash
# 1. Instalar Newman
npm install -g newman

# 2. Executar testes via script
cd postman
.\run-tests.ps1 -TestSuite smoke -OpenReport
```

## 📊 Tipos de Teste Disponíveis

### 🧪 Por Complexidade
| Tipo | Duração | Descrição |
|------|---------|-----------|
| **Quick** | 2 min | Health check + auth básico |
| **Smoke** | 5 min | Funcionalidades críticas |
| **Full** | 15 min | Todos os endpoints |
| **Custom** | Variável | Módulos específicos |

### 🎯 Por Módulo
| Módulo | Endpoints | Casos de Teste |
|--------|-----------|----------------|
| **Auth** | 2 | Login, register, refresh |
| **Users** | 3 | Profile, update, delete |
| **Agents** | 5 | CRUD completo + execute |
| **Chats** | 4 | CRUD + mensagens |
| **Flows** | 5 | CRUD + execução |
| **Files** | 4 | Upload, download, process |
| **Dashboard** | 2 | Stats, activity |

### 🔒 Por Segurança
- **Authentication Tests** - Tokens, permissões
- **Authorization Tests** - Isolamento de usuários
- **Validation Tests** - Input sanitization
- **Security Headers** - CORS, CSP, etc.

## 🛠️ Ferramentas Necessárias

### Básico (Obrigatório)
- ✅ **Postman** (10.x+) - Interface de testes
- ✅ **Servidor local** - API rodando na porta 8000
- ✅ **Banco de dados** - Schema instalado

### Avançado (Opcional)
- 🔧 **Newman** - Automação via CLI
- 🔧 **wkhtmltopdf** - Geração de PDF
- 🔧 **Git** - Versionamento e CI/CD

## 📈 Metodologia de Teste

### 1. Preparação
```bash
# Verificar ambiente
python main.py &          # Iniciar servidor
curl http://localhost:8000/health  # Health check
```

### 2. Execução
```bash
# Sequencial (recomendado)
1. Auth → 2. Users → 3. Agents → 4. Chats → 5. Flows → 6. Files → 7. Dashboard

# Paralelo (avançado)
newman run collection.json --folder "Auth" &
newman run collection.json --folder "Users" &
```

### 3. Validação
```bash
# Critérios de sucesso
- Status codes 2xx para casos de sucesso
- Status codes 4xx/5xx para casos de erro esperado
- Response times < 2000ms
- Dados corretos nas responses
- Tokens válidos sendo gerados
```

## 📊 Relatórios e Análise

### Relatórios Automáticos
- **HTML Report** - Visualização completa com gráficos
- **JSON Report** - Dados estruturados para análise
- **CLI Output** - Feedback em tempo real

### Métricas Importantes
- **Success Rate** - % de testes que passaram
- **Response Time** - Tempo médio de resposta
- **Error Distribution** - Tipos de erro mais comuns
- **Coverage** - % de endpoints testados

## 🔧 Troubleshooting

### Problemas Comuns
| Erro | Causa | Solução |
|------|-------|---------|
| Connection refused | Servidor parado | `python main.py` |
| 401 Unauthorized | Token inválido | Refazer login |
| 422 Validation Error | Dados inválidos | Verificar JSON |
| Newman not found | Newman não instalado | `npm install -g newman` |

### Debug Avançado
```javascript
// Scripts de debug para Postman
console.log("Request:", pm.request.url);
console.log("Response:", pm.response.json());
console.log("Environment:", pm.environment.toObject());
```

## 📚 Documentação Relacionada

### Links Internos
- `../api/API_DOCUMENTATION.md` - Especificação completa da API
- `../INSTALLATION.md` - Guia de instalação do projeto
- `../database/DATABASE_FINAL_USAGE_GUIDE.md` - Guia do banco de dados

### Links Externos
- [Postman Documentation](https://learning.postman.com/)
- [Newman Documentation](https://learning.postman.com/docs/running-collections/using-newman-cli/)
- [JWT.io](https://jwt.io/) - Debug de tokens JWT

## 🎯 Objetivos de Qualidade

### Funcional
- ✅ 100% dos endpoints funcionando
- ✅ Todos os casos de uso cobertos
- ✅ Validação completa de dados

### Não-Funcional
- ✅ Performance < 2s por request
- ✅ Segurança validada
- ✅ Estabilidade confirmada

### Processo
- ✅ Testes automatizados
- ✅ Documentação atualizada
- ✅ CI/CD integrado

---

## 🚀 Primeiros Passos

1. **Leia o guia rápido**: `QUICK_TEST_GUIDE.md`
2. **Configure o Postman**: `postman/POSTMAN_SETUP_GUIDE.md`  
3. **Execute o teste básico**: `postman/quick-test.bat`
4. **Analise os resultados**: Todos verdes = ✅ Sucesso!
5. **Para PDF**: Execute `.\generate-pdf.ps1`

## 💡 Dicas para Desenvolvedores

- **Sempre teste localmente primeiro** antes de push
- **Use o Collection Runner** para validação completa
- **Configure CI/CD** com Newman para automação
- **Monitore performance** - responses devem ser < 2s
- **Documente bugs** encontrados para correção
- **Mantenha ambientes** (dev/prod) sempre atualizados

---

**Criado em**: Janeiro 2024  
**Versão**: 1.0.0  
**Equipe**: EmployeeVirtual Development Team  
**Contato**: dev@employeevirtual.com
