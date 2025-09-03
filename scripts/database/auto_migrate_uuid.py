#!/usr/bin/env python3
"""
Script de Auto-Migrate para recriar todas as tabelas com UUIDs
Execute este script após remover todas as tabelas do banco
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from data.database import get_database_url
from models.user_models import Base as UserBase
from models.agent_models import Base as AgentBase
from models.flow_models import Base as FlowBase
from models.chat_models import Base as ChatBase
from models.file_models import Base as FileBase
from models.dashboard_models import Base as DashboardBase

def create_all_tables():
    """Cria todas as tabelas com UUIDs na ordem correta"""
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
        
        # Criar todas as tabelas na ORDEM CORRETA (respeitando dependências)
        print("\n🏗️ Criando tabelas na ordem correta...")
        
        # 1. Tabelas BASE (sem dependências) - PRIMEIRO
        print("📋 Criando tabelas BASE (usuários)...")
        UserBase.metadata.create_all(engine, checkfirst=True)
        
        # 2. Tabelas que dependem de users - SEGUNDO
        print("🤖 Criando tabelas que dependem de users (agentes)...")
        AgentBase.metadata.create_all(engine, checkfirst=True)
        
        print("🔄 Criando tabelas que dependem de users (flows)...")
        FlowBase.metadata.create_all(engine, checkfirst=True)
        
        print("💬 Criando tabelas que dependem de users (chat)...")
        ChatBase.metadata.create_all(engine, checkfirst=True)
        
        # 3. Tabelas que dependem de agents/flows - TERCEIRO
        print("📁 Criando tabelas que dependem de agents/flows (files)...")
        FileBase.metadata.create_all(engine, checkfirst=True)
        
        # 4. Tabelas de dashboard (sem dependências críticas) - QUARTO
        print("📊 Criando tabelas de dashboard...")
        DashboardBase.metadata.create_all(engine, checkfirst=True)
        
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
        
        print("\n🎉 AUTO-MIGRATE CONCLUÍDO COM SUCESSO!")
        print("Agora todas as tabelas estão configuradas para usar UUIDs.")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o auto-migrate: {e}")
        import traceback
        traceback.print_exc()
        return False

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
            
            # Verificar outras tabelas importantes
            tables_to_check = ['agents', 'flows', 'chat_conversations', 'files']
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
    print("🚀 AUTO-MIGRATE PARA UUIDs - EmployeeVirtual Backend")
    print("=" * 60)
    
    # Verificar se o usuário quer continuar
    response = input("\n⚠️ ATENÇÃO: Este script irá recriar TODAS as tabelas!")
    response += input("   Todos os dados existentes serão perdidos!")
    response += input("   Deseja continuar? (digite 'SIM' para confirmar): ")
    
    if response.upper() != 'SIM':
        print("❌ Operação cancelada pelo usuário.")
        return
    
    print("\n🔄 Iniciando auto-migrate...")
    
    # Executar auto-migrate
    if create_all_tables():
        # Verificar configuração de UUIDs
        verify_uuid_columns()
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. ✅ Tabelas criadas com UUIDs")
        print("2. 🔄 Reinicie o sistema Python")
        print("3. 🧪 Teste o registro de usuários")
        print("4. 📊 Verifique se os UUIDs estão sendo gerados")
        
    else:
        print("\n❌ AUTO-MIGRATE FALHOU!")
        print("Verifique os erros acima e tente novamente.")

if __name__ == "__main__":
    main()
