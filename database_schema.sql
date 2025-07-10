-- Scripts de criação das tabelas para o sistema EmployeeVirtual
-- Banco de dados: SQL Azure
-- Esquema: empl

-- Criar esquema se não existir
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'empl')
BEGIN
    EXEC('CREATE SCHEMA empl')
END
GO

-- Tabela de usuários
CREATE TABLE empl.users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    email NVARCHAR(255) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    plan NVARCHAR(20) NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'basic', 'pro', 'enterprise')),
    status NVARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended', 'pending')),
    avatar_url NVARCHAR(500) NULL,
    preferences NTEXT NULL, -- JSON string
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NULL,
    last_login DATETIME2 NULL
);

CREATE INDEX IX_users_email ON empl.users(email);
CREATE INDEX IX_users_status ON empl.users(status);
CREATE INDEX IX_users_created_at ON empl.users(created_at);

-- Tabela de sessões de usuário
CREATE TABLE empl.user_sessions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    token NVARCHAR(500) NOT NULL UNIQUE,
    expires_at DATETIME2 NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    is_active BIT NOT NULL DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES empl.users(id) ON DELETE CASCADE
);

CREATE INDEX IX_user_sessions_user_id ON empl.user_sessions(user_id);
CREATE INDEX IX_user_sessions_token ON empl.user_sessions(token);
CREATE INDEX IX_user_sessions_expires_at ON empl.user_sessions(expires_at);

-- Tabela de atividades do usuário
CREATE TABLE empl.user_activities (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    activity_type NVARCHAR(50) NOT NULL,
    description NTEXT NULL,
    metadata NTEXT NULL, -- JSON string
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    FOREIGN KEY (user_id) REFERENCES empl.users(id) ON DELETE CASCADE
);

CREATE INDEX IX_user_activities_user_id ON empl.user_activities(user_id);
CREATE INDEX IX_user_activities_type ON empl.user_activities(activity_type);
CREATE INDEX IX_user_activities_created_at ON empl.user_activities(created_at);

-- Tabela de agentes
CREATE TABLE empl.agents (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    name NVARCHAR(100) NOT NULL,
    description NTEXT NULL,
    agent_type NVARCHAR(30) NOT NULL DEFAULT 'custom' CHECK (agent_type IN ('custom', 'system', 'transcriber', 'youtube_transcriber', 'pdf_reader', 'image_ocr')),
    system_prompt NTEXT NOT NULL,
    personality NTEXT NULL,
    avatar_url NVARCHAR(500) NULL,
    status NVARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'draft', 'error')),
    llm_provider NVARCHAR(20) NOT NULL DEFAULT 'openai' CHECK (llm_provider IN ('openai', 'anthropic', 'google', 'groq', 'ollama', 'mistral', 'cohere', 'deepseek', 'azure', 'openrouter')),
    model NVARCHAR(100) NOT NULL,
    temperature FLOAT NOT NULL DEFAULT 0.7,
    max_tokens INT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NULL,
    last_used DATETIME2 NULL,
    usage_count INT NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES empl.users(id) ON DELETE CASCADE
);

CREATE INDEX IX_agents_user_id ON empl.agents(user_id);
CREATE INDEX IX_agents_type ON empl.agents(agent_type);
CREATE INDEX IX_agents_status ON empl.agents(status);
CREATE INDEX IX_agents_created_at ON empl.agents(created_at);

-- Tabela de base de conhecimento dos agentes
CREATE TABLE empl.agent_knowledge (
    id INT IDENTITY(1,1) PRIMARY KEY,
    agent_id INT NOT NULL,
    file_name NVARCHAR(255) NOT NULL,
    file_type NVARCHAR(50) NOT NULL,
    file_size INT NOT NULL,
    file_url NVARCHAR(500) NOT NULL,
    orion_file_id NVARCHAR(100) NULL,
    processed BIT NOT NULL DEFAULT 0,
    vector_ids NTEXT NULL, -- JSON array
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    processed_at DATETIME2 NULL,
    FOREIGN KEY (agent_id) REFERENCES empl.agents(id) ON DELETE CASCADE
);

CREATE INDEX IX_agent_knowledge_agent_id ON empl.agent_knowledge(agent_id);
CREATE INDEX IX_agent_knowledge_processed ON empl.agent_knowledge(processed);

-- Tabela de execuções de agentes
CREATE TABLE empl.agent_executions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    agent_id INT NOT NULL,
    user_id INT NOT NULL,
    user_message NTEXT NOT NULL,
    response NTEXT NOT NULL,
    model_used NVARCHAR(100) NOT NULL,
    execution_time FLOAT NULL,
    tokens_used INT NULL,
    success BIT NOT NULL DEFAULT 1,
    error_message NTEXT NULL,
    context NTEXT NULL, -- JSON string
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    FOREIGN KEY (agent_id) REFERENCES empl.agents(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES empl.users(id) ON DELETE CASCADE
);

CREATE INDEX IX_agent_executions_agent_id ON empl.agent_executions(agent_id);
CREATE INDEX IX_agent_executions_user_id ON empl.agent_executions(user_id);
CREATE INDEX IX_agent_executions_created_at ON empl.agent_executions(created_at);

-- Tabela de agentes do sistema
CREATE TABLE empl.system_agents (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL UNIQUE,
    description NTEXT NOT NULL,
    agent_type NVARCHAR(30) NOT NULL CHECK (agent_type IN ('transcriber', 'youtube_transcriber', 'pdf_reader', 'image_ocr')),
    system_prompt NTEXT NOT NULL,
    avatar_url NVARCHAR(500) NULL,
    orion_endpoint NVARCHAR(200) NULL,
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NULL
);

-- Tabela de flows
CREATE TABLE empl.flows (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    name NVARCHAR(100) NOT NULL,
    description NTEXT NULL,
    status NVARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('active', 'inactive', 'draft', 'paused', 'error')),
    tags NTEXT NULL, -- JSON array
    estimated_time INT NULL, -- em segundos
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NULL,
    last_executed DATETIME2 NULL,
    execution_count INT NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES empl.users(id) ON DELETE CASCADE
);

CREATE INDEX IX_flows_user_id ON empl.flows(user_id);
CREATE INDEX IX_flows_status ON empl.flows(status);
CREATE INDEX IX_flows_created_at ON empl.flows(created_at);

-- Tabela de etapas dos flows
CREATE TABLE empl.flow_steps (
    id INT IDENTITY(1,1) PRIMARY KEY,
    flow_id INT NOT NULL,
    name NVARCHAR(100) NOT NULL,
    step_type NVARCHAR(30) NOT NULL CHECK (step_type IN ('agent_execution', 'pause_for_review', 'condition', 'file_upload', 'orion_service')),
    [order] INT NOT NULL,
    description NTEXT NULL,
    config NTEXT NULL, -- JSON string
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NULL,
    FOREIGN KEY (flow_id) REFERENCES empl.flows(id) ON DELETE CASCADE
);

CREATE INDEX IX_flow_steps_flow_id ON empl.flow_steps(flow_id);
CREATE INDEX IX_flow_steps_order ON empl.flow_steps([order]);

-- Tabela de execuções de flows
CREATE TABLE empl.flow_executions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    flow_id INT NOT NULL,
    user_id INT NOT NULL,
    status NVARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'paused', 'cancelled')),
    input_data NTEXT NULL, -- JSON string
    output_data NTEXT NULL, -- JSON string
    current_step INT NULL,
    total_steps INT NOT NULL,
    completed_steps INT NOT NULL DEFAULT 0,
    error_message NTEXT NULL,
    execution_time FLOAT NULL,
    started_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    completed_at DATETIME2 NULL,
    FOREIGN KEY (flow_id) REFERENCES empl.flows(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES empl.users(id) ON DELETE CASCADE
);

CREATE INDEX IX_flow_executions_flow_id ON empl.flow_executions(flow_id);
CREATE INDEX IX_flow_executions_user_id ON empl.flow_executions(user_id);
CREATE INDEX IX_flow_executions_status ON empl.flow_executions(status);
CREATE INDEX IX_flow_executions_started_at ON empl.flow_executions(started_at);

-- Tabela de resultados das etapas de execução
CREATE TABLE empl.flow_execution_steps (
    id INT IDENTITY(1,1) PRIMARY KEY,
    execution_id INT NOT NULL,
    step_id INT NOT NULL,
    status NVARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'paused', 'cancelled')),
    input_data NTEXT NULL, -- JSON string
    output_data NTEXT NULL, -- JSON string
    error_message NTEXT NULL,
    execution_time FLOAT NULL,
    started_at DATETIME2 NULL,
    completed_at DATETIME2 NULL,
    FOREIGN KEY (execution_id) REFERENCES empl.flow_executions(id) ON DELETE CASCADE,
    FOREIGN KEY (step_id) REFERENCES empl.flow_steps(id) ON DELETE CASCADE
);

CREATE INDEX IX_flow_execution_steps_execution_id ON empl.flow_execution_steps(execution_id);
CREATE INDEX IX_flow_execution_steps_step_id ON empl.flow_execution_steps(step_id);

-- Tabela de templates de flows
CREATE TABLE empl.flow_templates (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    description NTEXT NOT NULL,
    category NVARCHAR(50) NOT NULL,
    template_data NTEXT NOT NULL, -- JSON string
    is_public BIT NOT NULL DEFAULT 0,
    usage_count INT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NULL
);

CREATE INDEX IX_flow_templates_category ON empl.flow_templates(category);
CREATE INDEX IX_flow_templates_is_public ON empl.flow_templates(is_public);

-- Tabela de conversações
CREATE TABLE empl.conversations (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    agent_id INT NOT NULL,
    title NVARCHAR(200) NULL,
    status NVARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NULL,
    last_message_at DATETIME2 NULL,
    FOREIGN KEY (user_id) REFERENCES empl.users(id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES empl.agents(id) ON DELETE CASCADE
);

CREATE INDEX IX_conversations_user_id ON empl.conversations(user_id);
CREATE INDEX IX_conversations_agent_id ON empl.conversations(agent_id);
CREATE INDEX IX_conversations_status ON empl.conversations(status);
CREATE INDEX IX_conversations_last_message_at ON empl.conversations(last_message_at);

-- Tabela de mensagens
CREATE TABLE empl.messages (
    id INT IDENTITY(1,1) PRIMARY KEY,
    conversation_id INT NOT NULL,
    user_id INT NOT NULL,
    agent_id INT NULL,
    content NTEXT NOT NULL,
    message_type NVARCHAR(20) NOT NULL CHECK (message_type IN ('user', 'agent', 'system')),
    metadata NTEXT NULL, -- JSON string
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    edited_at DATETIME2 NULL,
    is_edited BIT NOT NULL DEFAULT 0,
    FOREIGN KEY (conversation_id) REFERENCES empl.conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES empl.users(id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES empl.agents(id) ON DELETE SET NULL
);

CREATE INDEX IX_messages_conversation_id ON empl.messages(conversation_id);
CREATE INDEX IX_messages_user_id ON empl.messages(user_id);
CREATE INDEX IX_messages_agent_id ON empl.messages(agent_id);
CREATE INDEX IX_messages_created_at ON empl.messages(created_at);

-- Tabela de contexto das conversações
CREATE TABLE empl.conversation_contexts (
    id INT IDENTITY(1,1) PRIMARY KEY,
    conversation_id INT NOT NULL,
    context_key NVARCHAR(100) NOT NULL,
    context_value NTEXT NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NULL,
    FOREIGN KEY (conversation_id) REFERENCES empl.conversations(id) ON DELETE CASCADE
);

CREATE INDEX IX_conversation_contexts_conversation_id ON empl.conversation_contexts(conversation_id);
CREATE INDEX IX_conversation_contexts_key ON empl.conversation_contexts(context_key);

-- Tabela de reações às mensagens
CREATE TABLE empl.message_reactions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    message_id INT NOT NULL,
    user_id INT NOT NULL,
    reaction_type NVARCHAR(20) NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    FOREIGN KEY (message_id) REFERENCES empl.messages(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES empl.users(id) ON DELETE CASCADE
);

CREATE INDEX IX_message_reactions_message_id ON empl.message_reactions(message_id);
CREATE INDEX IX_message_reactions_user_id ON empl.message_reactions(user_id);

-- Tabela de arquivos
CREATE TABLE empl.files (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    agent_id INT NULL,
    original_name NVARCHAR(255) NOT NULL,
    file_path NVARCHAR(500) NOT NULL,
    file_url NVARCHAR(500) NOT NULL,
    file_type NVARCHAR(20) NOT NULL CHECK (file_type IN ('pdf', 'docx', 'doc', 'txt', 'csv', 'xlsx', 'xls', 'pptx', 'ppt', 'image', 'audio', 'video', 'other')),
    file_size INT NOT NULL,
    orion_file_id NVARCHAR(100) NULL,
    status NVARCHAR(20) NOT NULL DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'processing', 'processed', 'error', 'deleted')),
    description NTEXT NULL,
    tags NTEXT NULL, -- JSON array
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NULL,
    processed_at DATETIME2 NULL,
    FOREIGN KEY (user_id) REFERENCES empl.users(id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES empl.agents(id) ON DELETE SET NULL
);

CREATE INDEX IX_files_user_id ON empl.files(user_id);
CREATE INDEX IX_files_agent_id ON empl.files(agent_id);
CREATE INDEX IX_files_type ON empl.files(file_type);
CREATE INDEX IX_files_status ON empl.files(status);
CREATE INDEX IX_files_created_at ON empl.files(created_at);

-- Tabela de processamentos de arquivos
CREATE TABLE empl.file_processing (
    id INT IDENTITY(1,1) PRIMARY KEY,
    file_id INT NOT NULL,
    processing_type NVARCHAR(20) NOT NULL CHECK (processing_type IN ('ocr', 'transcription', 'vectorization', 'analysis')),
    status NVARCHAR(50) NOT NULL DEFAULT 'pending',
    result NTEXT NULL, -- JSON string
    error_message NTEXT NULL,
    processing_time FLOAT NULL,
    orion_task_id NVARCHAR(100) NULL,
    config NTEXT NULL, -- JSON string
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    completed_at DATETIME2 NULL,
    FOREIGN KEY (file_id) REFERENCES empl.files(id) ON DELETE CASCADE
);

CREATE INDEX IX_file_processing_file_id ON empl.file_processing(file_id);
CREATE INDEX IX_file_processing_type ON empl.file_processing(processing_type);
CREATE INDEX IX_file_processing_status ON empl.file_processing(status);

-- Tabela de serviços do Orion
CREATE TABLE empl.orion_services (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    service_type NVARCHAR(50) NOT NULL,
    file_id INT NULL,
    agent_id INT NULL,
    status NVARCHAR(50) NOT NULL DEFAULT 'pending',
    request_data NTEXT NULL, -- JSON string
    response_data NTEXT NULL, -- JSON string
    error_message NTEXT NULL,
    processing_time FLOAT NULL,
    orion_task_id NVARCHAR(100) NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    completed_at DATETIME2 NULL,
    FOREIGN KEY (user_id) REFERENCES empl.users(id) ON DELETE CASCADE,
    FOREIGN KEY (file_id) REFERENCES empl.files(id) ON DELETE SET NULL,
    FOREIGN KEY (agent_id) REFERENCES empl.agents(id) ON DELETE SET NULL
);

CREATE INDEX IX_orion_services_user_id ON empl.orion_services(user_id);
CREATE INDEX IX_orion_services_type ON empl.orion_services(service_type);
CREATE INDEX IX_orion_services_status ON empl.orion_services(status);

-- Tabela de arquivos no Data Lake
CREATE TABLE empl.datalake_files (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    file_id INT NOT NULL,
    datalake_path NVARCHAR(500) NOT NULL,
    datalake_url NVARCHAR(500) NOT NULL,
    metadata NTEXT NULL, -- JSON string
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    FOREIGN KEY (user_id) REFERENCES empl.users(id) ON DELETE CASCADE,
    FOREIGN KEY (file_id) REFERENCES empl.files(id) ON DELETE CASCADE
);

CREATE INDEX IX_datalake_files_user_id ON empl.datalake_files(user_id);
CREATE INDEX IX_datalake_files_file_id ON empl.datalake_files(file_id);

-- Tabela de métricas por usuário
CREATE TABLE empl.user_metrics (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    metric_date DATE NOT NULL,
    total_agents INT NOT NULL DEFAULT 0,
    total_flows INT NOT NULL DEFAULT 0,
    agent_executions INT NOT NULL DEFAULT 0,
    flow_executions INT NOT NULL DEFAULT 0,
    file_uploads INT NOT NULL DEFAULT 0,
    chat_messages INT NOT NULL DEFAULT 0,
    time_saved FLOAT NOT NULL DEFAULT 0.0, -- em horas
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NULL,
    FOREIGN KEY (user_id) REFERENCES empl.users(id) ON DELETE CASCADE
);

CREATE INDEX IX_user_metrics_user_id ON empl.user_metrics(user_id);
CREATE INDEX IX_user_metrics_date ON empl.user_metrics(metric_date);

-- Tabela de métricas de agentes
CREATE TABLE empl.agent_metrics (
    id INT IDENTITY(1,1) PRIMARY KEY,
    agent_id INT NOT NULL,
    user_id INT NOT NULL,
    metric_date DATE NOT NULL,
    executions INT NOT NULL DEFAULT 0,
    total_execution_time FLOAT NOT NULL DEFAULT 0.0,
    successful_executions INT NOT NULL DEFAULT 0,
    failed_executions INT NOT NULL DEFAULT 0,
    tokens_used INT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NULL,
    FOREIGN KEY (agent_id) REFERENCES empl.agents(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES empl.users(id) ON DELETE CASCADE
);

CREATE INDEX IX_agent_metrics_agent_id ON empl.agent_metrics(agent_id);
CREATE INDEX IX_agent_metrics_user_id ON empl.agent_metrics(user_id);
CREATE INDEX IX_agent_metrics_date ON empl.agent_metrics(metric_date);

-- Tabela de métricas de flows
CREATE TABLE empl.flow_metrics (
    id INT IDENTITY(1,1) PRIMARY KEY,
    flow_id INT NOT NULL,
    user_id INT NOT NULL,
    metric_date DATE NOT NULL,
    executions INT NOT NULL DEFAULT 0,
    total_execution_time FLOAT NOT NULL DEFAULT 0.0,
    successful_executions INT NOT NULL DEFAULT 0,
    failed_executions INT NOT NULL DEFAULT 0,
    time_saved FLOAT NOT NULL DEFAULT 0.0, -- em horas
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NULL,
    FOREIGN KEY (flow_id) REFERENCES empl.flows(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES empl.users(id) ON DELETE CASCADE
);

CREATE INDEX IX_flow_metrics_flow_id ON empl.flow_metrics(flow_id);
CREATE INDEX IX_flow_metrics_user_id ON empl.flow_metrics(user_id);
CREATE INDEX IX_flow_metrics_date ON empl.flow_metrics(metric_date);

-- Tabela de métricas do sistema
CREATE TABLE empl.system_metrics (
    id INT IDENTITY(1,1) PRIMARY KEY,
    metric_date DATE NOT NULL,
    total_users INT NOT NULL DEFAULT 0,
    active_users INT NOT NULL DEFAULT 0,
    total_agents INT NOT NULL DEFAULT 0,
    total_flows INT NOT NULL DEFAULT 0,
    total_executions INT NOT NULL DEFAULT 0,
    total_files INT NOT NULL DEFAULT 0,
    total_storage_used FLOAT NOT NULL DEFAULT 0.0, -- em GB
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE()
);

CREATE INDEX IX_system_metrics_date ON empl.system_metrics(metric_date);

-- Inserir agentes do sistema pré-configurados
INSERT INTO empl.system_agents (name, description, agent_type, system_prompt, orion_endpoint) VALUES
('Transcriber', 'Transcreve áudios em texto com alta precisão', 'transcriber', 'Você é um especialista em transcrição de áudio. Transcreva o áudio fornecido com precisão, mantendo pontuação adequada e formatação clara.', '/api/transcription'),
('YouTube Transcriber', 'Transcreve vídeos do YouTube automaticamente', 'youtube_transcriber', 'Você é um especialista em transcrição de vídeos do YouTube. Extraia e transcreva o conteúdo de áudio dos vídeos fornecidos.', '/api/youtube-transcription'),
('PDF Reader', 'Extrai e analisa textos de documentos PDF', 'pdf_reader', 'Você é um especialista em análise de documentos PDF. Extraia, organize e analise o conteúdo dos documentos fornecidos de forma estruturada.', '/api/pdf-analysis'),
('Image OCR', 'Lê e extrai texto de imagens e documentos escaneados', 'image_ocr', 'Você é um especialista em OCR (Reconhecimento Óptico de Caracteres). Extraia todo o texto visível das imagens fornecidas com precisão.', '/api/ocr');

PRINT 'Esquema de banco de dados criado com sucesso!'
PRINT 'Total de tabelas criadas: 25'
PRINT 'Agentes do sistema inseridos: 4'

