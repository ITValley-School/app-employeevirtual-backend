#!/usr/bin/env python3
"""
Script SIMPLES para recriar tabelas essenciais com UUIDs
Execute este script após remover todas as tabelas do banco
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text, inspect
from data.database import get_database_url

def create_simple_tables():
    """Cria tabelas simples com UUIDs"""
    try:
        # Obter URL do banco
        database_url = get_database_url()
        print(f"🔗 Conectando ao banco: {database_url}")
        
        # Criar engine
        engine = create_engine(database_url, echo=True)
        
        # Verificar conexão
        with engine.connect() as conn:
            result = conn.execute(text("SELECT @@VERSION"))
            version = result.fetchone()[0]
            print(f"✅ Conectado ao SQL Server: {version[:50]}...")
        
        # Verificar se o schema empl existe
        with engine.connect() as conn:
            result = conn.execute(text("""
                IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'empl')
                BEGIN
                    EXEC('CREATE SCHEMA empl')
                END
            """))
            conn.commit()
            print("✅ Schema 'empl' verificado/criado")
        
        # Criar tabelas simples com UUIDs
        print("\n🏗️ Criando tabelas simples com UUIDs...")
        
        # 1. Tabela users (base)
        print("📋 Criando tabela users...")
        create_users_table(engine)
        
        # 2. Tabela user_sessions
        print("🔐 Criando tabela user_sessions...")
        create_user_sessions_table(engine)
        
        # 3. Tabela user_activities
        print("📊 Criando tabela user_activities...")
        create_user_activities_table(engine)
        
        # Verificar tabelas criadas
        print("\n🔍 Verificando tabelas criadas...")
        inspector = inspect(engine)
        tables = inspector.get_table_names(schema='empl')
        
        if tables:
            print(f"✅ {len(tables)} tabelas criadas no schema 'empl':")
            for table in sorted(tables):
                print(f"   📋 {table}")
                
                # Mostrar estrutura da tabela
                columns = inspector.get_columns(table, schema='empl')
                for col in columns:
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    print(f"      - {col['name']}: {col['type']} {nullable}")
        else:
            print("⚠️ Nenhuma tabela foi criada!")
        
        print("\n🎉 MIGRAÇÃO SIMPLES CONCLUÍDA COM SUCESSO!")
        print("Agora as tabelas essenciais estão configuradas para usar UUIDs.")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_users_table(engine):
    """Cria tabela users com UUIDs"""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE [empl].[users] (
                id NVARCHAR(36) NOT NULL PRIMARY KEY DEFAULT NEWID(),
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
            )
        """))
        
        # Criar índices
        conn.execute(text("CREATE INDEX IX_users_email ON [empl].[users](email)"))
        conn.execute(text("CREATE INDEX IX_users_plan ON [empl].[users](plan)"))
        conn.execute(text("CREATE INDEX IX_users_status ON [empl].[users](status)"))
        
        conn.commit()
        print("   ✅ Tabela users criada com UUIDs")

def create_user_sessions_table(engine):
    """Cria tabela user_sessions com UUIDs"""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE [empl].[user_sessions] (
                id NVARCHAR(36) NOT NULL PRIMARY KEY DEFAULT NEWID(),
                user_id NVARCHAR(36) NOT NULL,
                token NVARCHAR(500) NOT NULL UNIQUE,
                expires_at DATETIME2 NOT NULL,
                created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
                is_active BIT NOT NULL DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES [empl].[users](id) ON DELETE CASCADE
            )
        """))
        
        # Criar índices
        conn.execute(text("CREATE INDEX IX_user_sessions_user_id ON [empl].[user_sessions](user_id)"))
        conn.execute(text("CREATE INDEX IX_user_sessions_token ON [empl].[user_sessions](token)"))
        conn.execute(text("CREATE INDEX IX_user_sessions_expires_at ON [empl].[user_sessions](expires_at)"))
        
        conn.commit()
        print("   ✅ Tabela user_sessions criada com UUIDs")

def create_user_activities_table(engine):
    """Cria tabela user_activities com UUIDs"""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE [empl].[user_activities] (
                id NVARCHAR(36) NOT NULL PRIMARY KEY DEFAULT NEWID(),
                user_id NVARCHAR(36) NOT NULL,
                activity_type NVARCHAR(50) NOT NULL,
                description NVARCHAR(MAX) NULL,
                activity_metadata NVARCHAR(MAX) NULL,
                created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
                FOREIGN KEY (user_id) REFERENCES [empl].[users](id) ON DELETE CASCADE
            )
        """))
        
        # Criar índices
        conn.execute(text("CREATE INDEX IX_user_activities_user_id ON [empl].[user_activities](user_id)"))
        conn.execute(text("CREATE INDEX IX_user_activities_activity_type ON [empl].[user_activities](activity_type)"))
        conn.execute(text("CREATE INDEX IX_user_activities_created_at ON [empl].[user_activities](created_at)"))
        
        conn.commit()
        print("   ✅ Tabela user_activities criada com UUIDs")

def verify_uuid_columns():
    """Verifica se as colunas ID estão configuradas para UUIDs"""
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        print("\n🔍 Verificando configuração de UUIDs...")
        
        with engine.connect() as conn:
            # Verificar tabela users
            result = conn.execute(text("""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    CHARACTER_MAXIMUM_LENGTH,
                    IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'empl' 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME = 'id'
            """))
            
            user_id_col = result.fetchone()
            if user_id_col:
                print(f"✅ Tabela users.id: {user_id_col[1]} (max: {user_id_col[2]})")
                if user_id_col[1] == 'nvarchar' and user_id_col[2] == 36:
                    print("   🎯 Configurada corretamente para UUIDs!")
                else:
                    print("   ⚠️ NÃO configurada para UUIDs!")
            else:
                print("❌ Coluna users.id não encontrada!")
            
            # Verificar outras tabelas
            tables_to_check = ['user_sessions', 'user_activities']
            for table in tables_to_check:
                result = conn.execute(text(f"""
                    SELECT 
                        COLUMN_NAME,
                        DATA_TYPE,
                        CHARACTER_MAXIMUM_LENGTH
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = 'empl' 
                    AND TABLE_NAME = '{table}' 
                    AND COLUMN_NAME = 'id'
                """))
                
                col = result.fetchone()
                if col:
                    print(f"✅ Tabela {table}.id: {col[1]} (max: {col[2]})")
                else:
                    print(f"⚠️ Tabela {table}.id não encontrada")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar UUIDs: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 MIGRAÇÃO SIMPLES PARA UUIDs - EmployeeVirtual Backend")
    print("=" * 60)
    
    # Verificar se o usuário quer continuar
    response = input("\n⚠️ ATENÇÃO: Este script irá criar tabelas essenciais com UUIDs!")
    response += input("   Deseja continuar? (digite 'SIM' para confirmar): ")
    
    if response.upper() != 'SIM':
        print("❌ Operação cancelada pelo usuário.")
        return
    
    print("\n🔄 Iniciando migração simples...")
    
    # Executar migração
    if create_simple_tables():
        # Verificar configuração de UUIDs
        verify_uuid_columns()
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. ✅ Tabelas essenciais criadas com UUIDs")
        print("2. 🔄 Reinicie o sistema Python")
        print("3. 🧪 Teste o registro de usuários")
        print("4. 📊 Verifique se os UUIDs estão sendo gerados")
        
    else:
        print("\n❌ MIGRAÇÃO FALHOU!")
        print("Verifique os erros acima e tente novamente.")

if __name__ == "__main__":
    main()
