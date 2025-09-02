-- Script para corrigir a tabela users para usar UUIDs
-- Execute este script no SQL Server Management Studio

USE [EmployeeVirtual]
GO

-- 1. Verificar se a tabela existe e sua estrutura atual
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'empl' AND TABLE_NAME = 'users')
BEGIN
    PRINT 'Tabela users encontrada. Verificando estrutura...';
    
    -- Mostrar estrutura atual
    SELECT 
        COLUMN_NAME,
        DATA_TYPE,
        IS_NULLABLE,
        COLUMN_DEFAULT,
        CHARACTER_MAXIMUM_LENGTH
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = 'empl' AND TABLE_NAME = 'users'
    ORDER BY ORDINAL_POSITION;
    
    -- Verificar se a coluna id é IDENTITY
    SELECT 
        c.name AS column_name,
        c.is_identity,
        c.seed_value,
        c.increment_value
    FROM sys.columns c
    INNER JOIN sys.tables t ON c.object_id = t.object_id
    INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
    WHERE s.name = 'empl' AND t.name = 'users' AND c.name = 'id';
END
ELSE
BEGIN
    PRINT 'Tabela users não encontrada no schema empl.';
    RETURN;
END

-- 2. Se a coluna id for IDENTITY, vamos corrigir isso
IF EXISTS (
    SELECT 1 FROM sys.columns c
    INNER JOIN sys.tables t ON c.object_id = t.object_id
    INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
    WHERE s.name = 'empl' AND t.name = 'users' AND c.name = 'id' AND c.is_identity = 1
)
BEGIN
    PRINT 'Coluna id é IDENTITY. Corrigindo para permitir UUIDs...';
    
    -- Criar tabela temporária com a estrutura correta
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
    
    -- Copiar dados existentes (se houver)
    IF EXISTS (SELECT 1 FROM [empl].[users])
    BEGIN
        PRINT 'Copiando dados existentes...';
        INSERT INTO #temp_users (id, name, email, password_hash, plan, status, avatar_url, preferences, created_at, updated_at, last_login)
        SELECT 
            NEWID() as id,  -- Gerar novo UUID para cada usuário existente
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
        
        PRINT 'Dados copiados com sucesso.';
    END
    ELSE
    BEGIN
        PRINT 'Nenhum dado existente para copiar.';
    END
    
    -- Remover tabela antiga
    DROP TABLE [empl].[users];
    
    -- Criar nova tabela com UUIDs
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
    
    -- Restaurar dados
    IF EXISTS (SELECT 1 FROM #temp_users)
    BEGIN
        INSERT INTO [empl].[users] (id, name, email, password_hash, plan, status, avatar_url, preferences, created_at, updated_at, last_login)
        SELECT id, name, email, password_hash, plan, status, avatar_url, preferences, created_at, updated_at, last_login
        FROM #temp_users;
        
        PRINT 'Dados restaurados com sucesso.';
    END
    
    -- Limpar tabela temporária
    DROP TABLE #temp_users;
    
    PRINT 'Tabela users corrigida para usar UUIDs!';
END
ELSE
BEGIN
    PRINT 'Coluna id não é IDENTITY. Verificando se já está configurada para UUIDs...';
    
    -- Verificar se a coluna id é NVARCHAR(36)
    IF EXISTS (
        SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = 'empl' AND TABLE_NAME = 'users' 
        AND COLUMN_NAME = 'id' AND DATA_TYPE = 'nvarchar' AND CHARACTER_MAXIMUM_LENGTH = 36
    )
    BEGIN
        PRINT 'Coluna id já está configurada para UUIDs (NVARCHAR(36)).';
    END
    ELSE
    BEGIN
        PRINT 'Coluna id não está configurada para UUIDs. Estrutura atual:';
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = 'empl' AND TABLE_NAME = 'users' AND COLUMN_NAME = 'id';
    END
END

-- 3. Criar índices se não existirem
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_users_email')
BEGIN
    CREATE INDEX IX_users_email ON [empl].[users](email);
    PRINT 'Índice IX_users_email criado.';
END

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_users_plan')
BEGIN
    CREATE INDEX IX_users_plan ON [empl].[users](plan);
    PRINT 'Índice IX_users_plan criado.';
END

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_users_status')
BEGIN
    CREATE INDEX IX_users_status ON [empl].[users](status);
    PRINT 'Índice IX_users_status criado.';
END

-- 4. Verificar resultado final
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
PRINT 'Agora a tabela users deve aceitar UUIDs corretamente.';
