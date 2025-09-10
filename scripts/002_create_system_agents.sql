-- scripts/002_create_system_agents.sql
-- Tabela para agentes do sistema (catálogo IT Valley)

IF NOT EXISTS (SELECT * FROM sys.objects WHERE name = 'system_agents' AND type = 'U')
BEGIN
    CREATE TABLE dbo.system_agents (
        id UNIQUEIDENTIFIER NOT NULL DEFAULT NEWSEQUENTIALID() PRIMARY KEY,
        slug NVARCHAR(80) NOT NULL UNIQUE,
        name NVARCHAR(120) NOT NULL,
        short_description NVARCHAR(240) NULL,
        category_id UNIQUEIDENTIFIER NULL,
        icon NVARCHAR(120) NULL,
        status NVARCHAR(20) NOT NULL DEFAULT 'active', -- valores: active|hidden|deprecated
        owner NVARCHAR(40) NOT NULL DEFAULT 'itvalley',
        created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        updated_at DATETIME2 NULL,
        CONSTRAINT FK_system_agents_category
            FOREIGN KEY (category_id) REFERENCES dbo.system_agent_categories(id)
    );
    
    -- Índice para performance
    CREATE INDEX IX_system_agents_status_category ON dbo.system_agents(status, category_id);
    
    PRINT 'Tabela system_agents criada com sucesso';
END
ELSE
BEGIN
    PRINT 'Tabela system_agents já existe';
END;
GO
