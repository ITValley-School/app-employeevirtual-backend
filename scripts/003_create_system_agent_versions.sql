-- scripts/003_create_system_agent_versions.sql
-- Tabela para versionamento + ponte com executor Orion

IF NOT EXISTS (SELECT * FROM sys.objects WHERE name = 'system_agent_versions' AND type = 'U')
BEGIN
    CREATE TABLE dbo.system_agent_versions (
        id UNIQUEIDENTIFIER NOT NULL DEFAULT NEWSEQUENTIALID() PRIMARY KEY,
        system_agent_id UNIQUEIDENTIFIER NOT NULL,
        version NVARCHAR(20) NOT NULL, -- ex.: 1.0.0
        is_default BIT NOT NULL DEFAULT 1,
        definition_ref NVARCHAR(100) NOT NULL, -- ID do snapshot imutável — Mongo/JSON
        executor NVARCHAR(40) NOT NULL DEFAULT 'orion',
        executor_ref NVARCHAR(120) NOT NULL, -- ex.: service_name no Orion
        executor_version_selector NVARCHAR(20) NULL, -- ex.: ^2
        capabilities NVARCHAR(MAX) NULL, -- JSON: ["scrape.linkedin","stt.transcribe"]
        changelog NVARCHAR(MAX) NULL,
        created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        published_at DATETIME2 NULL,
        CONSTRAINT FK_system_agent_versions_agent
            FOREIGN KEY (system_agent_id) REFERENCES dbo.system_agents(id)
    );
    
    -- Índice para performance (versão default primeiro)
    CREATE INDEX IX_agent_versions_default ON dbo.system_agent_versions(system_agent_id, is_default DESC);
    
    PRINT 'Tabela system_agent_versions criada com sucesso';
END
ELSE
BEGIN
    PRINT 'Tabela system_agent_versions já existe';
END;
GO
