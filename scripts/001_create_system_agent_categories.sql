-- scripts/001_create_system_agent_categories.sql
-- Tabela para categorias de agentes do sistema

IF NOT EXISTS (SELECT * FROM sys.objects WHERE name = 'system_agent_categories' AND type = 'U')
BEGIN
    CREATE TABLE dbo.system_agent_categories (
        id UNIQUEIDENTIFIER NOT NULL DEFAULT NEWSEQUENTIALID() PRIMARY KEY,
        name NVARCHAR(80) NOT NULL,
        icon NVARCHAR(50) NULL,
        description NVARCHAR(300) NULL,
        order_index INT DEFAULT 0,
        is_active BIT DEFAULT 1,
        created_at DATETIME2 DEFAULT SYSDATETIME(),
        updated_at DATETIME2 DEFAULT SYSDATETIME()
    );
    
    -- Constraint: UNIQUE(name)
    CREATE UNIQUE INDEX UQ_system_agent_categories_name ON dbo.system_agent_categories(name);
    
    PRINT 'Tabela system_agent_categories criada com sucesso';
END
ELSE
BEGIN
    PRINT 'Tabela system_agent_categories já existe';
END;
GO
