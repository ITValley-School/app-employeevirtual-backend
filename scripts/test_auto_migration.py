#!/usr/bin/env python3
"""
Script para testar o sistema de auto-migração
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.migrations import (
    auto_migrate, 
    force_migrate, 
    get_status, 
    test_db,
    migrator
)

def print_separator(title: str):
    """Imprime um separador visual"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_success(message: str):
    """Imprime mensagem de sucesso"""
    print(f"✅ {message}")

def print_error(message: str):
    """Imprime mensagem de erro"""
    print(f"❌ {message}")

def print_info(message: str):
    """Imprime mensagem informativa"""
    print(f"ℹ️ {message}")

def print_warning(message: str):
    """Imprime mensagem de aviso"""
    print(f"⚠️ {message}")

def test_connection():
    """Testa conexão com banco"""
    print_separator("TESTE DE CONEXÃO")
    
    try:
        success = test_db()
        if success:
            print_success("Conexão com banco estabelecida")
            return True
        else:
            print_error("Falha na conexão com banco")
            return False
    except Exception as e:
        print_error(f"Erro no teste de conexão: {e}")
        return False

def test_status():
    """Testa obtenção de status"""
    print_separator("STATUS DO BANCO")
    
    try:
        status = get_status()
        print_info(f"Status: {status['status']}")
        print_info(f"Tabelas existentes: {status['existing_tables']}")
        print_info(f"Tabelas faltando: {status['missing_tables']}")
        print_info(f"Tabelas órfãs: {status['orphaned_tables']}")
        print_info(f"Total de modelos: {status['total_metadata_tables']}")
        print_info(f"Conexão: {'OK' if status['connection'] else 'FALHA'}")
        
        return status
    except Exception as e:
        print_error(f"Erro ao obter status: {e}")
        return None

def test_safe_migration():
    """Testa migração segura"""
    print_separator("MIGRAÇÃO SEGURA")
    
    try:
        print_info("Executando migração segura...")
        success = auto_migrate()
        
        if success:
            print_success("Migração segura concluída")
        else:
            print_error("Falha na migração segura")
        
        return success
    except Exception as e:
        print_error(f"Erro na migração segura: {e}")
        return False

def test_force_migration():
    """Testa migração forçada (CUIDADO!)"""
    print_separator("MIGRAÇÃO FORÇADA")
    
    print_warning("⚠️ ATENÇÃO: Esta operação recriará TODAS as tabelas!")
    print_warning("⚠️ ISSO PODE CAUSAR PERDA DE DADOS!")
    
    response = input("🤔 Tem certeza? Digite 'SIM' para continuar: ")
    
    if response.upper() != "SIM":
        print_info("Operação cancelada pelo usuário")
        return False
    
    try:
        print_info("Executando migração forçada...")
        success = force_migrate()
        
        if success:
            print_success("Migração forçada concluída")
        else:
            print_error("Falha na migração forçada")
        
        return success
    except Exception as e:
        print_error(f"Erro na migração forçada: {e}")
        return False

def test_table_analysis():
    """Testa análise de tabelas"""
    print_separator("ANÁLISE DE TABELAS")
    
    try:
        # Tabelas existentes
        existing = migrator.get_existing_tables()
        print_info(f"Tabelas no banco: {len(existing)}")
        
        # Tabelas nos modelos
        metadata = migrator.get_metadata_tables()
        print_info(f"Tabelas nos modelos: {len(metadata)}")
        
        # Diferenças
        differences = migrator.check_table_differences()
        print_info(f"Tabelas órfãs: {len(differences['orphaned'])}")
        print_info(f"Tabelas faltando: {len(differences['missing'])}")
        print_info(f"Tabelas comuns: {len(differences['common'])}")
        
        return True
    except Exception as e:
        print_error(f"Erro na análise: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 EmployeeVirtual - Testador de Auto-Migração")
    print("=" * 60)
    
    # Teste de conexão
    if not test_connection():
        print_error("❌ Não é possível continuar sem conexão com banco")
        return
    
    # Status inicial
    initial_status = test_status()
    if not initial_status:
        print_error("❌ Não foi possível obter status inicial")
        return
    
    # Análise de tabelas
    test_table_analysis()
    
    # Menu de opções
    while True:
        print_separator("MENU DE OPÇÕES")
        print("1. Ver status atual")
        print("2. Executar migração segura")
        print("3. Executar migração forçada (CUIDADO!)")
        print("4. Analisar tabelas")
        print("5. Sair")
        
        choice = input("\n🤔 Escolha uma opção (1-5): ")
        
        if choice == "1":
            test_status()
        elif choice == "2":
            test_safe_migration()
        elif choice == "3":
            test_force_migration()
        elif choice == "4":
            test_table_analysis()
        elif choice == "5":
            print_info("Saindo...")
            break
        else:
            print_error("Opção inválida!")
        
        # Pausa
        input("\n⏸️ Pressione ENTER para continuar...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n💥 Erro inesperado: {e}")
