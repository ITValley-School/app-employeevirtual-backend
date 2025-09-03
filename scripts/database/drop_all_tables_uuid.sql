-- Script para remover TODAS as tabelas do schema empl
-- Execute este script no SQL Server Management Studio ANTES de fazer auto-migrate

USE [dbmasterclasse]
GO

PRINT '=== REMOVENDO TODAS AS TABELAS DO SCHEMA EMPL ===';

-- 1. Verificar tabelas existentes
PRINT 'Tabelas encontradas no schema empl:';
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'empl' 
ORDER BY TABLE_NAME;

-- 2. Verificar e remover FOREIGN KEY constraints com verificação de existência
PRINT 'Verificando e removendo FOREIGN KEY constraints...';

-- Mostrar todas as constraints existentes
PRINT 'Constraints encontradas no schema empl:';
SELECT 
    tc.TABLE_NAME,
    tc.CONSTRAINT_NAME,
    tc.CONSTRAINT_TYPE
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
WHERE tc.TABLE_SCHEMA = 'empl'
ORDER BY tc.TABLE_NAME, tc.CONSTRAINT_TYPE;

-- Remover foreign keys uma por uma com verificação
DECLARE @tableName NVARCHAR(128);
DECLARE @constraintName NVARCHAR(128);
DECLARE @sql NVARCHAR(MAX);

-- Cursor para iterar sobre todas as foreign keys
DECLARE constraint_cursor CURSOR FOR
SELECT 
    tc.TABLE_NAME,
    tc.CONSTRAINT_NAME
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
INNER JOIN INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc ON tc.CONSTRAINT_NAME = rc.CONSTRAINT_NAME
WHERE tc.TABLE_SCHEMA = 'empl' AND tc.CONSTRAINT_TYPE = 'FOREIGN KEY';

OPEN constraint_cursor;
FETCH NEXT FROM constraint_cursor INTO @tableName, @constraintName;

WHILE @@FETCH_STATUS = 0
BEGIN
    -- Verificar se a constraint ainda existe antes de tentar removê-la
    IF EXISTS (
        SELECT 1 FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
        WHERE TABLE_SCHEMA = 'empl' 
        AND TABLE_NAME = @tableName 
        AND CONSTRAINT_NAME = @constraintName
    )
    BEGIN
        SET @sql = 'ALTER TABLE [empl].[' + @tableName + '] DROP CONSTRAINT [' + @constraintName + ']';
        PRINT 'Removendo constraint: ' + @constraintName + ' da tabela ' + @tableName;
        
        BEGIN TRY
            EXEC sp_executesql @sql;
            PRINT '✅ Constraint ' + @constraintName + ' removida com sucesso';
        END TRY
        BEGIN CATCH
            PRINT '⚠️ Erro ao remover constraint ' + @constraintName + ': ' + ERROR_MESSAGE();
        END CATCH
    END
    ELSE
    BEGIN
        PRINT '⚠️ Constraint ' + @constraintName + ' não encontrada na tabela ' + @tableName;
    END
    
    FETCH NEXT FROM constraint_cursor INTO @tableName, @constraintName;
END

CLOSE constraint_cursor;
DEALLOCATE constraint_cursor;

-- 3. Verificar se ainda há constraints restantes
PRINT 'Verificando constraints restantes após remoção...';
SELECT 
    tc.TABLE_NAME,
    tc.CONSTRAINT_NAME,
    tc.CONSTRAINT_TYPE
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
WHERE tc.TABLE_SCHEMA = 'empl'
ORDER BY tc.TABLE_NAME, tc.CONSTRAINT_TYPE;

-- 4. Agora remover tabelas na ordem correta
PRINT 'Removendo tabelas...';

-- Primeiro remover tabelas que podem ter foreign keys
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'empl' AND TABLE_NAME = 'user_activities')
BEGIN
    PRINT 'Removendo user_activities...';
    BEGIN TRY
        DROP TABLE [empl].[user_activities];
        PRINT '✅ user_activities removida';
    END TRY
    BEGIN CATCH
        PRINT '⚠️ Erro ao remover user_activities: ' + ERROR_MESSAGE();
    END CATCH
END

IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'empl' AND TABLE_NAME = 'user_sessions')
BEGIN
    PRINT 'Removendo user_sessions...';
    BEGIN TRY
        DROP TABLE [empl].[user_sessions];
        PRINT '✅ user_sessions removida';
    END TRY
    BEGIN CATCH
        PRINT '⚠️ Erro ao remover user_sessions: ' + ERROR_MESSAGE();
    END CATCH
END

IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'empl' AND TABLE_NAME = 'chat_messages')
BEGIN
    PRINT 'Removendo chat_messages...';
    BEGIN TRY
        DROP TABLE [empl].[chat_messages];
        PRINT '✅ chat_messages removida';
    END TRY
    BEGIN CATCH
        PRINT '⚠️ Erro ao remover chat_messages: ' + ERROR_MESSAGE();
    END CATCH
END

IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'empl' AND TABLE_NAME = 'chat_conversations')
BEGIN
    PRINT 'Removendo chat_conversations...';
    BEGIN TRY
        DROP TABLE [empl].[chat_conversations];
        PRINT '✅ chat_conversations removida';
    END TRY
    BEGIN CATCH
        PRINT '⚠️ Erro ao remover chat_conversations: ' + ERROR_MESSAGE();
    END CATCH
END

IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'empl' AND TABLE_NAME = 'flow_executions')
BEGIN
    PRINT 'Removendo flow_executions...';
    BEGIN TRY
        DROP TABLE [empl].[flow_executions];
        PRINT '✅ flow_executions removida';
    END TRY
    BEGIN CATCH
        PRINT '⚠️ Erro ao remover flow_executions: ' + ERROR_MESSAGE();
    END CATCH
END

IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'empl' AND TABLE_NAME = 'flows')
BEGIN
    PRINT 'Removendo flows...';
    BEGIN TRY
        DROP TABLE [empl].[flows];
        PRINT '✅ flows removida';
    END TRY
    BEGIN CATCH
        PRINT '⚠️ Erro ao remover flows: ' + ERROR_MESSAGE();
    END CATCH
END

IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'empl' AND TABLE_NAME = 'agent_executions')
BEGIN
    PRINT 'Removendo agent_executions...';
    BEGIN TRY
        DROP TABLE [empl].[agent_executions];
        PRINT '✅ agent_executions removida';
    END TRY
    BEGIN CATCH
        PRINT '⚠️ Erro ao remover agent_executions: ' + ERROR_MESSAGE();
    END CATCH
END

IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'empl' AND TABLE_NAME = 'agents')
BEGIN
    PRINT 'Removendo agents...';
    BEGIN TRY
        DROP TABLE [empl].[agents];
        PRINT '✅ agents removida';
    END TRY
    BEGIN CATCH
        PRINT '⚠️ Erro ao remover agents: ' + ERROR_MESSAGE();
    END CATCH
END

IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'empl' AND TABLE_NAME = 'files')
BEGIN
    PRINT 'Removendo files...';
    BEGIN TRY
        DROP TABLE [empl].[files];
        PRINT '✅ files removida';
    END TRY
    BEGIN CATCH
        PRINT '⚠️ Erro ao remover files: ' + ERROR_MESSAGE();
    END CATCH
END

-- Por último remover a tabela users
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'empl' AND TABLE_NAME = 'users')
BEGIN
    PRINT 'Removendo users...';
    BEGIN TRY
        DROP TABLE [empl].[users];
        PRINT '✅ users removida';
    END TRY
    BEGIN CATCH
        PRINT '⚠️ Erro ao remover users: ' + ERROR_MESSAGE();
    END CATCH
END

-- 5. Verificar se todas as tabelas foram removidas
PRINT '=== VERIFICAÇÃO FINAL ===';
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'empl' 
ORDER BY TABLE_NAME;

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'empl')
BEGIN
    PRINT '✅ TODAS AS TABELAS FORAM REMOVIDAS COM SUCESSO!';
    PRINT 'Agora você pode executar o auto-migrate para recriar as tabelas com UUIDs.';
END
ELSE
BEGIN
    PRINT '⚠️ ALGUMAS TABELAS AINDA EXISTEM:';
    SELECT TABLE_NAME 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_SCHEMA = 'empl' 
    ORDER BY TABLE_NAME;
END

PRINT '=== LIMPEZA CONCLUÍDA! ===';
PRINT 'Execute o auto-migrate agora para recriar as tabelas com UUIDs.';
