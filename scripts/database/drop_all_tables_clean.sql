-- ================================================================
-- DROP ALL TABLES - EMPLOYEEVIRTUAL DATABASE
-- ================================================================
-- Target: Azure SQL Database
-- Schema: empl
-- Version: Super Clean v1.0
-- Purpose: Complete cleanup for fresh installation
-- ================================================================

PRINT '🧹 Starting complete database cleanup...'
PRINT '⚠️  WARNING: This will delete ALL tables and data!'
PRINT ''

-- Disable foreign key checks temporarily
EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL'

-- Drop all tables in correct order (respecting dependencies)
PRINT '🗑️  Dropping tables...'

-- Drop metrics tables first
IF OBJECT_ID('empl.system_metrics', 'U') IS NOT NULL DROP TABLE empl.system_metrics;
IF OBJECT_ID('empl.flow_metrics', 'U') IS NOT NULL DROP TABLE empl.flow_metrics;
IF OBJECT_ID('empl.agent_metrics', 'U') IS NOT NULL DROP TABLE empl.agent_metrics;
IF OBJECT_ID('empl.user_metrics', 'U') IS NOT NULL DROP TABLE empl.user_metrics;

-- Drop file-related tables
IF OBJECT_ID('empl.datalake_files', 'U') IS NOT NULL DROP TABLE empl.datalake_files;
IF OBJECT_ID('empl.orion_services', 'U') IS NOT NULL DROP TABLE empl.orion_services;
IF OBJECT_ID('empl.file_processing', 'U') IS NOT NULL DROP TABLE empl.file_processing;
IF OBJECT_ID('empl.files', 'U') IS NOT NULL DROP TABLE empl.files;

-- Drop message-related tables
IF OBJECT_ID('empl.message_reactions', 'U') IS NOT NULL DROP TABLE empl.message_reactions;
IF OBJECT_ID('empl.messages', 'U') IS NOT NULL DROP TABLE empl.messages;
IF OBJECT_ID('empl.conversation_contexts', 'U') IS NOT NULL DROP TABLE empl.conversation_contexts;
IF OBJECT_ID('empl.conversations', 'U') IS NOT NULL DROP TABLE empl.conversations;

-- Drop flow-related tables
IF OBJECT_ID('empl.flow_templates', 'U') IS NOT NULL DROP TABLE empl.flow_templates;
IF OBJECT_ID('empl.flow_execution_steps', 'U') IS NOT NULL DROP TABLE empl.flow_execution_steps;
IF OBJECT_ID('empl.flow_executions', 'U') IS NOT NULL DROP TABLE empl.flow_executions;
IF OBJECT_ID('empl.flow_steps', 'U') IS NOT NULL DROP TABLE empl.flow_steps;
IF OBJECT_ID('empl.flows', 'U') IS NOT NULL DROP TABLE empl.flows;

-- Drop agent-related tables
IF OBJECT_ID('empl.system_agents', 'U') IS NOT NULL DROP TABLE empl.system_agents;
IF OBJECT_ID('empl.agent_executions', 'U') IS NOT NULL DROP TABLE empl.agent_executions;
IF OBJECT_ID('empl.agent_knowledge', 'U') IS NOT NULL DROP TABLE empl.agent_knowledge;
IF OBJECT_ID('empl.agents', 'U') IS NOT NULL DROP TABLE empl.agents;

-- Drop user-related tables
IF OBJECT_ID('empl.user_activities', 'U') IS NOT NULL DROP TABLE empl.user_activities;
IF OBJECT_ID('empl.user_sessions', 'U') IS NOT NULL DROP TABLE empl.user_sessions;
IF OBJECT_ID('empl.users', 'U') IS NOT NULL DROP TABLE empl.users;

-- Re-enable foreign key checks
EXEC sp_MSforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT ALL'

PRINT '✅ All tables dropped successfully!'
PRINT ''
PRINT '🧹 Database cleanup completed!'
PRINT '📝 Ready for fresh installation with database_schema_super_clean.sql'
PRINT ''

GO
