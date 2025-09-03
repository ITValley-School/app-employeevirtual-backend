-- Script SIMPLES para corrigir a tabela users para UUIDs
-- Execute este script no SQL Server Management Studio

USE [EmployeeVirtual]
GO

PRINT '=== CORRIGINDO TABELA USERS PARA UUIDs ===';

-- 1. Verificar estrutura atual
PRINT 'Estrutura atual da tabela users:';
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    CHARACTER_MAXIMUM_LENGTH
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'empl' AND TABLE_NAME = 'users'
ORDER BY ORDINAL_POSITION;

-- 2. Criar tabela temporária com UUIDs
PRINT 'Criando tabela temporária...';
CREATE TABLE #temp_users (
    id NVARCHAR(36) NOT NULL,
    name NVARCHAR(100) NOT NULL,
    email NVARCHAR(255) NOT NULL,
    password_hash NVARCHAR(255) NOT NULL,
    plan NVARCHAR(20) NOT NULL DEFAULT 'free',
    status NVARCHAR(20) NOT NULL DEFAULT 'active',
    role NVARCHAR(20) NOT NULL DEFAULT 'user',
    avatar_url NVARCHAR(500) NULL,
    preferences NVARCHAR(MAX) NULL,
    metadata NVARCHAR(MAX) NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NULL,
    last_login DATETIME2 NULL
);

-- 3. Copiar dados existentes (se houver)
IF EXISTS (SELECT 1 FROM [empl].[users])
BEGIN
    PRINT 'Copiando dados existentes...';
    INSERT INTO #temp_users (id, name, email, password_hash, plan, status, role, avatar_url, preferences, metadata, created_at, updated_at, last_login)
    SELECT 
        NEWID() as id,  -- Gerar novo UUID para cada usuário
        name,
        email,
        password_hash,
        ISNULL(plan, 'free'),
        ISNULL(status, 'active'),
        ISNULL(role, 'user'),
        avatar_url,
        preferences,
        metadata,
        created_at,
        updated_at,
        last_login
    FROM [empl].[users];
    
    PRINT 'Dados copiados com sucesso.';
END
ELSE
BEGIN
    PRINT 'Nenhum dado existente para copiar.';
END

-- 4. Remover tabela antiga
PRINT 'Removendo tabela antiga...';
DROP TABLE [empl].[users];

-- 5. Criar nova tabela com UUIDs
PRINT 'Criando nova tabela com UUIDs...';
CREATE TABLE [empl].[users] (
    id NVARCHAR(36) NOT NULL PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    email NVARCHAR(255) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    plan NVARCHAR(20) NOT NULL DEFAULT 'free',
    status NVARCHAR(20) NOT NULL DEFAULT 'active',
    role NVARCHAR(20) NOT NULL DEFAULT 'user',
    avatar_url NVARCHAR(500) NULL,
    preferences NVARCHAR(MAX) NULL,
    metadata NVARCHAR(MAX) NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NULL,
    last_login DATETIME2 NULL
);

-- 6. Restaurar dados
IF EXISTS (SELECT 1 FROM #temp_users)
BEGIN
    PRINT 'Restaurando dados...';
    INSERT INTO [empl].[users] (id, name, email, password_hash, plan, status, role, avatar_url, preferences, metadata, created_at, updated_at, last_login)
    SELECT id, name, email, password_hash, plan, status, role, avatar_url, preferences, metadata, created_at, updated_at, last_login
    FROM #temp_users;
    
    PRINT 'Dados restaurados com sucesso.';
END

-- 7. Limpar tabela temporária
DROP TABLE #temp_users;

-- 8. Criar índices
PRINT 'Criando índices...';
CREATE INDEX IX_users_email ON [empl].[users](email);
CREATE INDEX IX_users_plan ON [empl].[users](plan);
CREATE INDEX IX_users_status ON [empl].[users](status);
CREATE INDEX IX_users_role ON [empl].[users](role);

-- 9. Verificar resultado
PRINT '=== VERIFICAÇÃO FINAL ===';
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    CHARACTER_MAXIMUM_LENGTH
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'empl' AND TABLE_NAME = 'users'
ORDER BY ORDINAL_POSITION;

PRINT '=== CORREÇÃO CONCLUÍDA! ===';
PRINT 'A tabela users agora aceita UUIDs corretamente.';
PRINT 'Teste o sistema novamente!';
