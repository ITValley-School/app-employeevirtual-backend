-- Script para criar tabelas de gerenciamento de chaves LLM
-- Execute este script no SQL Server Management Studio

USE [dbmasterclasse]
GO

PRINT '=== CRIANDO TABELAS DE GERENCIAMENTO DE CHAVES LLM ===';

-- 1. Tabela de chaves LLM do sistema
PRINT 'Criando tabela system_llm_keys...';
CREATE TABLE [empl].[system_llm_keys] (
    id NVARCHAR(36) NOT NULL PRIMARY KEY DEFAULT NEWID(),
    provider NVARCHAR(50) NOT NULL, -- openai, anthropic, google, etc.
    api_key NVARCHAR(500) NOT NULL, -- chave criptografada
    is_active BIT NOT NULL DEFAULT 1,
    usage_limit DECIMAL(10,2) NULL, -- limite de uso mensal
    current_usage DECIMAL(10,2) DEFAULT 0,
    last_used DATETIME2 NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NULL
);

-- 2. Tabela de chaves LLM dos usuários
PRINT 'Criando tabela user_llm_keys...';
CREATE TABLE [empl].[user_llm_keys] (
    id NVARCHAR(36) NOT NULL PRIMARY KEY DEFAULT NEWID(),
    user_id NVARCHAR(36) NOT NULL,
    provider NVARCHAR(50) NOT NULL,
    api_key NVARCHAR(500) NOT NULL, -- chave criptografada
    is_active BIT NOT NULL DEFAULT 1,
    usage_limit DECIMAL(10,2) NULL,
    current_usage DECIMAL(10,2) DEFAULT 0,
    last_used DATETIME2 NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NULL,
    FOREIGN KEY (user_id) REFERENCES [empl].[users](id) ON DELETE CASCADE
);

-- 3. Modificar tabela agents para suportar chaves
PRINT 'Modificando tabela agents...';
ALTER TABLE [empl].[agents] ADD
    use_system_key BIT NOT NULL DEFAULT 0, -- usar chave do sistema?
    user_key_id NVARCHAR(36) NULL, -- referência à chave do usuário
    system_key_provider NVARCHAR(50) NULL; -- qual chave do sistema usar

-- 4. Criar índices para performance
PRINT 'Criando índices...';

-- Índices para system_llm_keys
CREATE INDEX IX_system_llm_keys_provider ON [empl].[system_llm_keys](provider);
CREATE INDEX IX_system_llm_keys_active ON [empl].[system_llm_keys](is_active);

-- Índices para user_llm_keys
CREATE INDEX IX_user_llm_keys_user_id ON [empl].[user_llm_keys](user_id);
CREATE INDEX IX_user_llm_keys_provider ON [empl].[user_llm_keys](provider);
CREATE INDEX IX_user_llm_keys_active ON [empl].[user_llm_keys](is_active);

-- Índices para agents (novas colunas)
CREATE INDEX IX_agents_use_system_key ON [empl].[agents](use_system_key);
CREATE INDEX IX_agents_user_key_id ON [empl].[agents](user_key_id);
CREATE INDEX IX_agents_system_key_provider ON [empl].[agents](system_key_provider);

-- 5. Inserir dados padrão para chaves do sistema (exemplo)
PRINT 'Inserindo dados padrão...';
INSERT INTO [empl].[system_llm_keys] (provider, api_key, usage_limit, is_active)
VALUES 
    ('openai', 'ENCRYPTED_KEY_PLACEHOLDER', 1000.00, 1),
    ('anthropic', 'ENCRYPTED_KEY_PLACEHOLDER', 1000.00, 1),
    ('google', 'ENCRYPTED_KEY_PLACEHOLDER', 1000.00, 1),
    ('azure', 'ENCRYPTED_KEY_PLACEHOLDER', 1000.00, 1);

-- 6. Verificar tabelas criadas
PRINT '=== VERIFICAÇÃO FINAL ===';
SELECT 
    TABLE_NAME,
    TABLE_SCHEMA
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'empl' 
AND TABLE_NAME IN ('system_llm_keys', 'user_llm_keys')
ORDER BY TABLE_NAME;

-- Verificar estrutura da tabela agents modificada
PRINT 'Estrutura da tabela agents modificada:';
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'empl' 
AND TABLE_NAME = 'agents'
AND COLUMN_NAME IN ('use_system_key', 'user_key_id', 'system_key_provider')
ORDER BY ORDINAL_POSITION;

PRINT '=== TABELAS LLM CRIADAS COM SUCESSO! ===';
PRINT 'Agora você pode implementar as APIs de gerenciamento de chaves.';
