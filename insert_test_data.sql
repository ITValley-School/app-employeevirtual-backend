-- ========================================
-- EMPLOYEEVIRTUAL - DADOS DE TESTE
-- Execute estes comandos no seu Azure SQL Server
-- ========================================

-- 1. INSERIR USUÁRIO DE TESTE
INSERT INTO empl.users (
    email, 
    password_hash, 
    full_name, 
    is_active, 
    created_at
) VALUES (
    'teste@employeevirtual.com',
    '$2b$12$LQv3c4yqdCaOdOzQa.BN8OqGgKrKQz8gvJgGOp.RwQ8oL5.2l3M1G', -- senha: "123456"
    'Usuário de Teste',
    1,
    GETDATE()
);

-- 2. INSERIR AGENTE DE TESTE (ID = 1)
INSERT INTO empl.agents (
    id,
    user_id, 
    name, 
    description, 
    agent_type, 
    system_prompt, 
    personality, 
    avatar_url, 
    status, 
    llm_provider, 
    model, 
    temperature, 
    max_tokens, 
    created_at,
    usage_count
) VALUES (
    1, -- ID fixo
    1, -- user_id (do usuário criado acima)
    'Assistente de Programação',
    'Agente especializado em desenvolvimento de código, debugging e melhores práticas de programação.',
    'custom',
    'Você é um assistente especializado em programação e desenvolvimento de software. Você deve:

1. Fornecer código limpo, bem comentado e seguindo melhores práticas
2. Explicar a lógica por trás das soluções propostas
3. Sugerir melhorias e otimizações quando relevante
4. Detectar possíveis bugs ou problemas no código
5. Ser preciso e direto nas respostas
6. Usar exemplos práticos sempre que possível

Linguagens que você domina: Python, JavaScript, TypeScript, Java, C#, SQL, HTML, CSS, React, Node.js, FastAPI, Django.

Responda sempre em português brasileiro.',
    'Sou meticuloso, direto e focado em qualidade. Gosto de código limpo e bem estruturado. Tenho paixão por resolver problemas complexos de forma elegante.',
    'https://via.placeholder.com/150/0066CC/FFFFFF?text=DEV',
    'active',
    'openai',
    'gpt-4o-mini',
    0.3,
    4000,
    GETDATE(),
    0
);

-- 3. INSERIR MAIS ALGUNS AGENTES DE TESTE
INSERT INTO empl.agents (
    user_id, 
    name, 
    description, 
    agent_type, 
    system_prompt, 
    personality, 
    status, 
    llm_provider, 
    model, 
    temperature, 
    max_tokens, 
    created_at,
    usage_count
) VALUES 
(1, 'Analista de Dados', 
 'Especialista em análise de dados, estatística e visualizações.',
 'custom',
 'Você é um analista de dados expert. Ajude com análises estatísticas, visualizações e insights de dados. Responda em português.',
 'Analítico, curioso e apaixonado por padrões nos dados.',
 'active',
 'anthropic', 
 'claude-3-5-haiku-latest',
 0.5,
 3000,
 GETDATE(),
 0),

(1, 'Assistente Geral', 
 'Agente de uso geral para tarefas diversas e conversação.',
 'custom',
 'Você é um assistente útil e amigável. Ajude com tarefas gerais, responda perguntas e mantenha conversas engajantes. Sempre responda em português brasileiro.',
 'Amigável, prestativo e sempre disposto a ajudar.',
 'active',
 'openai',
 'gpt-4o',
 0.7,
 2000,
 GETDATE(),
 0);

-- 4. VERIFICAR SE OS DADOS FORAM INSERIDOS
SELECT 
    a.id,
    a.name,
    a.description,
    a.llm_provider,
    a.model,
    a.status,
    u.email as user_email
FROM empl.agents a
JOIN empl.users u ON a.user_id = u.id
ORDER BY a.id;

-- ========================================
-- COMANDOS ÚTEIS PARA TESTES
-- ========================================

-- Ver todos os agentes
SELECT * FROM empl.agents;

-- Ver todas as execuções de agentes
SELECT * FROM empl.agent_executions ORDER BY created_at DESC;

-- Ver atividades do usuário
SELECT * FROM empl.user_activities ORDER BY created_at DESC;

-- Limpar dados de teste (se necessário)
-- DELETE FROM empl.agent_executions;
-- DELETE FROM empl.agents WHERE user_id = 1;
-- DELETE FROM empl.users WHERE email = 'teste@employeevirtual.com';
