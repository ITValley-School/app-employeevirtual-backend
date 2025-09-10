-- scripts/004_create_system_agent_visibility.sql
-- Tabela para controle de quem vê/usa cada agente do sistema

IF NOT EXISTS (SELECT * FROM sys.objects WHERE name = 'system_agent_visibility' AND type = 'U')
BEGIN
    CREATE TABLE dbo.system_agent_visibility (
        id UNIQUEIDENTIFIER NOT NULL DEFAULT NEWSEQUENTIALID() PRIMARY KEY,
        system_agent_id UNIQUEIDENTIFIER NOT NULL,
        tenant_id UNIQUEIDENTIFIER NULL,
        plan NVARCHAR(20) NULL, -- free|pro|enterprise
        region NVARCHAR(40) NULL,
        is_enabled BIT NOT NULL DEFAULT 1,
        start_at DATETIME2 NULL,
        end_at DATETIME2 NULL,
        CONSTRAINT FK_system_agent_visibility_agent
            FOREIGN KEY (system_agent_id) REFERENCES dbo.system_agents(id)
    );
    
    -- Índice para queries de visibilidade
    CREATE INDEX IX_visibility_agent_tenant ON dbo.system_agent_visibility(system_agent_id, tenant_id, is_enabled);
    
    PRINT 'Tabela system_agent_visibility criada com sucesso';
END
ELSE
BEGIN
    PRINT 'Tabela system_agent_visibility já existe';
END;
GO
