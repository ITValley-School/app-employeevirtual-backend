# 🤖 Como Executar Agentes de IA Pydantic - EmployeeVirtual## 📋 Visão GeralEste guia completo mostra como usar os agentes de IA do EmployeeVirtual que foram implementados com **Pydantic AI**. Os agentes suportam 50+ modelos LLM de diferentes provedores e oferecem funcionalidades avançadas como tools, dependency injection e structured output.---## 🚀 Configuração Inicial### 1. **Variáveis de Ambiente**Configure as chaves de API dos provedores LLM:```bash# OpenAIOPENAI_API_KEY=sk-your_openai_key_here# AnthropicANTHROPIC_API_KEY=sk-ant-your_anthropic_key# GoogleGOOGLE_API_KEY=your_google_ai_key# GroqGROQ_API_KEY=gsk_your_groq_key# Azure OpenAIAZURE_OPENAI_API_KEY=your_azure_keyAZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/# Outros provedoresMISTRAL_API_KEY=your_mistral_keyCOHERE_API_KEY=your_cohere_keyDEEPSEEK_API_KEY=your_deepseek_key```### 2. **Dependências**```bashpip install pydantic-ai httpx sqlalchemy```---## 🎯 Criando um Agente### **1. Endpoint: `POST /api/agents/`**```pythonimport requests# Dados do agenteagent_data = {    "name": "Assistente GPT-4",    "description": "Agente especializado em análise e conversação",    "agent_type": "custom",    "llm_provider": "openai",    "model": "gpt-4o",    "temperature": 0.7,    "max_tokens": 4000,    "system_prompt": "Você é um assistente especializado em análise de dados e conversação inteligente. Seja preciso, útil e educado.",    "personality": "Amigável, profissional e detalhista"}# Headers com autenticaçãoheaders = {    "Authorization": "Bearer seu_token_aqui",    "Content-Type": "application/json"}# Criar agenteresponse = requests.post(    "http://localhost:8000/api/agents/",    json=agent_data,    headers=headers)agent = response.json()print(f"Agente criado: ID {agent['id']} - {agent['name']}")```### **2. Via Python Direto**```pythonfrom services.agent_service import AgentServicefrom models.agent_models import AgentCreatefrom data.database import get_db# Configurar sessão do bancodb = next(get_db())agent_service = AgentService(db)# Criar agenteagent_data = AgentCreate(    name="Assistente Claude",    description="Agente com Claude 3.5 Sonnet",    llm_provider="anthropic",    model="claude-3-5-sonnet-latest",    temperature=0.3,    max_tokens=8000,    system_prompt="Você é um assistente especializado em programação e análise técnica.")agent = agent_service.create_agent(user_id=123, agent_data=agent_data)print(f"Agente criado: {agent.name}")```---## 🔥 Executando Agentes### **1. Execução Básica - API**```pythonimport requests# Dados da execuçãoexecution_data = {    "user_message": "Explique o que é machine learning em termos simples",    "context": {        "source": "api_request",        "timestamp": "2025-01-15T10:30:00Z"    }}headers = {    "Authorization": "Bearer seu_token_aqui",    "Content-Type": "application/json"}# Executar agenteresponse = requests.post(    f"http://localhost:8000/api/agents/{agent_id}/execute",    json=execution_data,    headers=headers)result = response.json()print(f"Resposta: {result['response']}")print(f"Tempo de execução: {result['execution_time']:.2f}s")print(f"Modelo usado: {result['model_used']}")```### **2. Execução via Python**```python# Execução direta no códigoresult = await agent_service.execute_agent(    agent_id=1,    user_id=123,    user_message="Analise este relatório e me dê insights",    context={        "file_url": "https://example.com/relatorio.pdf",        "analysis_type": "business_intelligence",        "priority": "high"    })# Resultadoprint(f"Resposta: {result['response']}")print(f"Sucesso: {result['success']}")print(f"Tempo: {result['execution_time']:.2f}s")print(f"Modelo: {result['model_used']}")```---## 🛠️ Modelos LLM Suportados### **Modelos Principais por Categoria**| **Categoria** | **Modelo Recomendado** | **Provedor** | **Uso** ||---------------|------------------------|--------------|---------|| **Chat Geral** | `gpt-4o-mini` | OpenAI | Conversação rápida e econômica || **Análise Complexa** | `claude-3-5-sonnet-latest` | Anthropic | Raciocínio avançado || **Programação** | `codestral-latest` | Mistral | Código e desenvolvimento || **Raciocínio** | `o1-mini` | OpenAI | Problemas complexos || **Respostas Rápidas** | `llama-3.1-8b-instant` | Groq | Velocidade máxima || **Criativo** | `claude-3-5-haiku-latest` | Anthropic | Conteúdo criativo |### **Lista Completa de Provedores**- **OpenAI**: GPT-4o, GPT-4o-mini, O1, O3, ChatGPT-4o-latest- **Anthropic**: Claude 3.5 Sonnet, Claude 4, Haiku, Opus- **Google**: Gemini 2.0/2.5 Flash/Pro- **Groq**: Llama 3.3, Qwen, Whisper, Vision models- **Mistral**: Large, Small, Codestral- **Cohere**: Command R/R+, Aya Expanse- **DeepSeek**: Chat, Reasoner---## 🎛️ Configurações de Agentes### **Parâmetros Importantes**```pythonagent_config = {    # Parâmetros do modelo    "temperature": 0.7,      # 0.0-2.0: Criatividade (0=determinístico, 2=muito criativo)    "max_tokens": 4000,      # Limite de tokens de resposta        # Configurações do agente    "llm_provider": "openai", # Provedor: openai, anthropic, google, groq, etc.    "model": "gpt-4o",       # Modelo específico        # Personalização    "personality": "Amigável e profissional",    "system_prompt": "Você é um especialista em...",}```### **Configurações Recomendadas por Uso**```python# Para análise de dadosanalysis_config = {    "llm_provider": "anthropic",    "model": "claude-3-5-sonnet-latest",    "temperature": 0.3,  # Baixa para precisão    "max_tokens": 8000}# Para conversação casualchat_config = {    "llm_provider": "openai",     "model": "gpt-4o-mini",    "temperature": 0.7,  # Média para naturalidade    "max_tokens": 2000}# Para programaçãocode_config = {    "llm_provider": "mistral",    "model": "codestral-latest",     "temperature": 0.1,  # Muito baixa para precisão    "max_tokens": 8000}# Para criatividadecreative_config = {    "llm_provider": "anthropic",    "model": "claude-3-5-haiku-latest",    "temperature": 0.9,  # Alta para criatividade    "max_tokens": 4000}```---## 📊 Gerenciamento de Agentes### **1. Listar Agentes**```python# Via APIresponse = requests.get(    "http://localhost:8000/api/agents/",    headers=headers,    params={"include_system": True})agents = response.json()for agent in agents:    print(f"ID: {agent['id']} | Nome: {agent['name']} | Modelo: {agent['llm_provider']}:{agent['model']}")```### **2. Atualizar Agente**```pythonupdate_data = {    "name": "Assistente GPT-4 Melhorado",    "temperature": 0.5,    "system_prompt": "Prompt atualizado com novas instruções..."}response = requests.put(    f"http://localhost:8000/api/agents/{agent_id}",    json=update_data,    headers=headers)```### **3. Histórico de Execuções**```python# Buscar últimas execuçõesresponse = requests.get(    f"http://localhost:8000/api/agents/{agent_id}/executions",    headers=headers,    params={"limit": 10})executions = response.json()for exec in executions:    print(f"[{exec['created_at']}] {exec['user_message'][:50]}...")    print(f"  Resposta: {exec['response'][:100]}...")    print(f"  Sucesso: {exec['success']} | Tempo: {exec['execution_time']:.2f}s\n")```---## 🧠 Base de Conhecimento (RAG)### **1. Adicionar Conhecimento**```pythonknowledge_data = {    "file_name": "manual_empresa.pdf",    "file_type": "pdf",     "file_size": 2048576,  # bytes    "file_url": "https://storage.com/manual_empresa.pdf",    "orion_file_id": "orion_123456"  # opcional - para integração ORION}response = requests.post(    f"http://localhost:8000/api/agents/{agent_id}/knowledge",    json=knowledge_data,    headers=headers)knowledge = response.json()print(f"Conhecimento adicionado: {knowledge['file_name']}")```### **2. Usar Conhecimento na Execução**```python# O agente automaticamente usa o conhecimento adicionadoresult = await agent_service.execute_agent(    agent_id=1,    user_id=123,    user_message="Com base no manual da empresa, explique o processo de férias")# O sistema busca automaticamente no conhecimento e inclui no contextoprint(f"Resposta baseada no conhecimento: {result['response']}")```---## 🔧 Integração com ORION### **Processamento Automático de Arquivos**```python# O agente pode processar arquivos automaticamente via ORIONresult = await agent_service.execute_agent(    agent_id=1,    user_id=123,    user_message="Transcreva este áudio e me dê um resumo",    context={        "file_url": "https://example.com/audio.mp3",        "process_type": "whisper",  # whisper, ocr, pdf, youtube_transcriber    })print(f"Resultado com processamento ORION: {result['response']}")```### **Tipos de Processamento ORION Suportados**- **`whisper`**: Transcrição de áudio/vídeo- **`ocr`**: Extração de texto de imagens  
- **`pdf`**: Processamento de documentos PDF
- **`youtube_transcriber`**: Transcrição de vídeos do YouTube

---

## 💡 Exemplos Práticos

### **1. Assistente de Análise de Dados**

```python
# Criar agente especializado
agent_data = {
    "name": "Analista de Dados",
    "llm_provider": "anthropic",
    "model": "claude-3-5-sonnet-latest",
    "temperature": 0.3,
    "system_prompt": """
    Você é um especialista em análise de dados e business intelligence.
    - Analise dados de forma clara e objetiva
    - Forneça insights acionáveis
    - Use visualizações quando necessário
    - Explique metodologias usadas
    """
}

# Executar análise
result = await agent_service.execute_agent(
    agent_id=agent['id'],
    user_id=123,
    user_message="Analise as vendas do Q4 e identifique tendências",
    context={"data_source": "sales_q4.csv"}
)
```

### **2. Assistente de Código**

```python
# Agente para programação
agent_data = {
    "name": "Dev Assistant",
    "llm_provider": "mistral", 
    "model": "codestral-latest",
    "temperature": 0.1,
    "system_prompt": """
    Você é um assistente especializado em programação.
    - Escreva código limpo e bem documentado
    - Explique conceitos técnicos claramente
    - Sugira melhorias e otimizações
    - Siga boas práticas de desenvolvimento
    """
}

# Pedir ajuda com código
result = await agent_service.execute_agent(
    agent_id=agent['id'],
    user_id=123,
    user_message="Crie uma função Python para validar CPF"
)
```

### **3. Assistente Multimodal**

```python
# Agente que processa imagens e áudio
result = await agent_service.execute_agent(
    agent_id=1,
    user_id=123,
    user_message="Analise esta imagem e extraia o texto, depois me dê um resumo",
    context={
        "file_url": "https://example.com/documento.jpg",
        "process_type": "ocr"
    }
)

print(f"Análise multimodal: {result['response']}")
```

---

## 🚨 Tratamento de Erros

### **Códigos de Erro Comuns**

```python
try:
    result = await agent_service.execute_agent(agent_id, user_id, message)
    
    if result['success']:
        print(f"✅ Sucesso: {result['response']}")
    else:
        print(f"❌ Erro: {result['error_message']}")
        
except ValueError as e:
    if "não encontrado" in str(e):
        print("❌ Agente não existe ou não pertence ao usuário")
    elif "não está ativo" in str(e):
        print("❌ Agente está inativo")
    elif "Mensagem não pode estar vazia" in str(e):
        print("❌ Mensagem é obrigatória")
    else:
        print(f"❌ Erro de validação: {e}")
        
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
```

---

## 📈 Monitoramento

### **1. Estatísticas do Agente**

```python
# Via API
response = requests.get(f"http://localhost:8000/api/agents/{agent_id}", headers=headers)
agent = response.json()

print(f"Uso total: {agent['usage_count']} execuções")
print(f"Último uso: {agent['last_used']}")
print(f"Status: {agent['status']}")
```

### **2. Performance**

```python
# Métricas de execução
executions = requests.get(f"http://localhost:8000/api/agents/{agent_id}/executions", headers=headers).json()

total_time = sum(e['execution_time'] for e in executions)
avg_time = total_time / len(executions) if executions else 0
success_rate = sum(1 for e in executions if e['success']) / len(executions) if executions else 0

print(f"Tempo médio: {avg_time:.2f}s")
print(f"Taxa de sucesso: {success_rate:.1%}")
```

---

## 🎉 Resumo de Comandos Rápidos

### **Workflow Completo**

```python
from services.agent_service import AgentService
from models.agent_models import AgentCreate

# 1. Inicializar serviço
agent_service = AgentService(db)

# 2. Criar agente
agent_data = AgentCreate(
    name="Meu Assistente",
    llm_provider="openai",
    model="gpt-4o-mini", 
    system_prompt="Você é um assistente útil."
)
agent = agent_service.create_agent(user_id=123, agent_data=agent_data)

# 3. Executar
result = await agent_service.execute_agent(
    agent_id=agent.id,
    user_id=123,
    user_message="Olá, como você pode me ajudar?"
)

# 4. Verificar resultado
print(f"Resposta: {result['response']}")
print(f"Tempo: {result['execution_time']:.2f}s")
```

### **Via API - Comando Único**

```bash
# Criar e executar agente via curl
curl -X POST "http://localhost:8000/api/agents/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Agent",
    "llm_provider": "openai",
    "model": "gpt-4o-mini",
    "system_prompt": "Você é um assistente útil.",
    "temperature": 0.7
  }'

# Executar agente
curl -X POST "http://localhost:8000/api/agents/1/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_message": "Explique quantum computing"}'
```

---

## 🔮 Recursos Avançados Futuros

- **Streaming de Respostas**: Respostas em tempo real
- **Multi-Agent Conversations**: Agentes colaborando
- **Custom Tools**: Ferramentas personalizadas
- **Instrumentação com Logfire**: Monitoring avançado
- **RAG Avançado**: Busca semântica aprimorada

---

**🚀 Parabéns! Agora você domina os agentes Pydantic AI do EmployeeVirtual!**

Para dúvidas ou suporte, consulte a documentação da API completa ou entre em contato com a equipe de desenvolvimento.
