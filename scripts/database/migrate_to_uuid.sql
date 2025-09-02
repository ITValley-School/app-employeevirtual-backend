-- Script de migração para converter IDs de INTEGER para UUID
-- Execute este script APENAS se você já tem dados nas tabelas
-- Para instalação nova, use o script database_schema_super_clean.sql

USE [EmployeeVirtual]
GO

-- Habilitar extensão UUID se estiver usando PostgreSQL
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Criar tabelas temporárias com UUIDs
-- =============================================

-- Tabela temporária de usuários
CREATE TABLE #temp_users (
    id NVARCHAR(36) NOT NULL,
    name NVARCHAR(100) NOT NULL,
    email NVARCHAR(255) NOT NULL,
    password_hash NVARCHAR(255) NOT NULL,
    plan NVARCHAR(20) NOT NULL DEFAULT 'free',
    status NVARCHAR(20) NOT NULL DEFAULT 'active',
    avatar_url NVARCHAR(500) NULL,
    preferences NVARCHAR(MAX) NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NULL,
    last_login DATETIME2 NULL
);

-- Tabela temporária de sessões
CREATE TABLE #temp_user_sessions (
    id NVARCHAR(36) NOT NULL,
    user_id NVARCHAR(36) NOT NULL,
    token NVARCHAR(500) NOT NULL,
    expires_at DATETIME2 NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    is_active BIT NOT NULL DEFAULT 1
);

-- Tabela temporária de atividades
CREATE TABLE #temp_user_activities (
    id NVARCHAR(36) NOT NULL,
    user_id NVARCHAR(36) NOT NULL,
    activity_type NVARCHAR(50) NOT NULL,
    description NVARCHAR(MAX) NULL,
    activity_metadata NVARCHAR(MAX) NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE()
);

-- 2. Migrar dados existentes para tabelas temporárias
-- =====================================================

-- Migrar usuários
INSERT INTO #temp_users (id, name, email, password_hash, plan, status, avatar_url, preferences, created_at, updated_at, last_login)
SELECT 
    NEWID() as id,  -- Gerar novo UUID
    name,
    email,
    password_hash,
    plan,
    status,
    avatar_url,
    preferences,
    created_at,
    updated_at,
    last_login
FROM [empl].[users];

-- Migrar sessões (se existirem)
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'empl' AND TABLE_NAME = 'user_sessions')
BEGIN
    INSERT INTO #temp_user_sessions (id, user_id, token, expires_at, created_at, is_active)
    SELECT 
        NEWID() as id,
        (SELECT temp.id FROM #temp_users temp WHERE temp.email = (SELECT u.email FROM [empl].[users] u WHERE u.id = us.user_id)) as user_id,
        token,
        expires_at,
        created_at,
        is_active
    FROM [empl].[user_sessions] us;
END

-- Migrar atividades (se existirem)
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'empl' AND TABLE_NAME = 'user_activities')
BEGIN
    INSERT INTO #temp_user_activities (id, user_id, activity_type, description, activity_metadata, created_at)
    SELECT 
        NEWID() as id,
        (SELECT temp.id FROM #temp_users temp WHERE temp.email = (SELECT u.email FROM [empl].[users] u WHERE u.id = ua.user_id)) as user_id,
        activity_type,
        description,
        activity_metadata,
        created_at
    FROM [empl].[user_activities] ua;
END

-- 3. Remover tabelas antigas
-- ============================

-- Remover tabelas antigas (se existirem)
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'empl' AND TABLE_NAME = 'user_activities')
    DROP TABLE [empl].[user_activities];

IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'empl' AND TABLE_NAME = 'user_sessions')
    DROP TABLE [empl].[user_sessions];

IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'empl' AND TABLE_NAME = 'users')
    DROP TABLE [empl].[users];

-- 4. Criar novas tabelas com UUIDs
-- ==================================

-- Tabela de usuários
CREATE TABLE [empl].[users] (
    id NVARCHAR(36) NOT NULL PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    email NVARCHAR(255) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    plan NVARCHAR(20) NOT NULL DEFAULT 'free',
    status NVARCHAR(20) NOT NULL DEFAULT 'active',
    avatar_url NVARCHAR(500) NULL,
    preferences NVARCHAR(MAX) NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NULL,
    last_login DATETIME2 NULL
);

-- Tabela de sessões
CREATE TABLE [empl].[user_sessions] (
    id NVARCHAR(36) NOT NULL PRIMARY KEY,
    user_id NVARCHAR(36) NOT NULL,
    token NVARCHAR(500) NOT NULL UNIQUE,
    expires_at DATETIME2 NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    is_active BIT NOT NULL DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES [empl].[users](id) ON DELETE CASCADE
);

-- Tabela de atividades
CREATE TABLE [empl].[user_activities] (
    id NVARCHAR(36) NOT NULL PRIMARY KEY,
    user_id NVARCHAR(36) NOT NULL,
    activity_type NVARCHAR(50) NOT NULL,
    description NVARCHAR(MAX) NULL,
    activity_metadata NVARCHAR(MAX) NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES [empl].[users](id) ON DELETE CASCADE
);

-- 5. Criar índices
-- ==================

-- Índices para usuários
CREATE INDEX IX_users_email ON [empl].[users](email);
CREATE INDEX IX_users_plan ON [empl].[users](plan);
CREATE INDEX IX_users_status ON [empl].[users](status);
CREATE INDEX IX_users_created_at ON [empl].[users](created_at);

-- Índices para sessões
CREATE INDEX IX_user_sessions_user_id ON [empl].[user_sessions](user_id);
CREATE INDEX IX_user_sessions_token ON [empl].[user_sessions](token);
CREATE INDEX IX_user_sessions_expires_at ON [empl].[user_sessions](expires_at);

-- Índices para atividades
CREATE INDEX IX_user_activities_user_id ON [empl].[user_activities](user_id);
CREATE INDEX IX_user_activities_activity_type ON [empl].[user_activities](activity_type);
CREATE INDEX IX_user_activities_created_at ON [empl].[user_activities](created_at);

-- 6. Migrar dados das tabelas temporárias
-- =========================================

-- Migrar usuários
INSERT INTO [empl].[users] (id, name, email, password_hash, plan, status, avatar_url, preferences, created_at, updated_at, last_login)
SELECT id, name, email, password_hash, plan, status, avatar_url, preferences, created_at, updated_at, last_login
FROM #temp_users;

-- Migrar sessões
INSERT INTO [empl].[user_sessions] (id, user_id, token, expires_at, created_at, is_active)
SELECT id, user_id, token, expires_at, created_at, is_active
FROM #temp_user_sessions
WHERE user_id IS NOT NULL;

-- Migrar atividades
INSERT INTO [empl].[user_activities] (id, user_id, activity_type, description, activity_metadata, created_at)
SELECT id, user_id, activity_type, description, activity_metadata, created_at
FROM #temp_user_activities
WHERE user_id IS NOT NULL;

-- 7. Inserir dados padrão se não existirem
-- =========================================

-- Usuário administrador padrão
IF NOT EXISTS (SELECT * FROM [empl].[users] WHERE email = 'admin@employeevirtual.com')
BEGIN
    INSERT INTO [empl].[users] (id, name, email, password_hash, plan, status)
    VALUES (
        NEWID(),
        'Administrador',
        'admin@employeevirtual.com',
        '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', -- 'password'
        'enterprise',
        'active'
    );
END

-- Usuário de teste padrão
IF NOT EXISTS (SELECT * FROM [empl].[users] WHERE email = 'teste@employeevirtual.com')
BEGIN
    INSERT INTO [empl].[users] (id, name, email, password_hash, plan, status)
    VALUES (
        NEWID(),
        'Usuário Teste',
        'teste@employeevirtual.com',
        '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', -- 'admin'
        'free',
        'active'
    );
END

-- 8. Limpar tabelas temporárias
-- ==============================

DROP TABLE #temp_users;
DROP TABLE #temp_user_sessions;
DROP TABLE #temp_user_activities;

-- 9. Verificar migração
-- =======================

PRINT '=== VERIFICAÇÃO DA MIGRAÇÃO ===';
PRINT 'Usuários migrados: ' + CAST((SELECT COUNT(*) FROM [empl].[users]) AS NVARCHAR(10));
PRINT 'Sessões migradas: ' + CAST((SELECT COUNT(*) FROM [empl].[user_sessions]) AS NVARCHAR(10));
PRINT 'Atividades migradas: ' + CAST((SELECT COUNT(*) FROM [empl].[user_activities]) AS NVARCHAR(10));

-- Mostrar alguns usuários migrados
SELECT TOP 5 id, name, email, plan, status, created_at FROM [empl].[users] ORDER BY created_at DESC;

PRINT '=== MIGRAÇÃO CONCLUÍDA COM SUCESSO! ===';
PRINT 'Agora você pode usar UUIDs em vez de IDs inteiros.';
PRINT 'Lembre-se de atualizar seu código para trabalhar com UUIDs.';
