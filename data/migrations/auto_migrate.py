"""
Sistema de auto-migração automática do banco de dados
"""
import logging
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from data.database import engine
from data.base import Base, get_all_metadata

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoMigrator:
    """
    Classe para gerenciar migrações automáticas do banco
    """
    
    def __init__(self):
        self.engine = engine
        self.inspector = inspect(engine)
        self.metadata = get_all_metadata()
    
    def test_connection(self):
        """
        Testa conexão com o banco
        """
        try:
            with self.engine.connect() as conn:
                # Para Azure SQL Server
                result = conn.execute(text("SELECT @@VERSION as version"))
                version = result.fetchone()
                logger.info(f"✅ Conectado ao Azure SQL Server: {version[0]}")
                return True
        except Exception as e:
            logger.error(f"❌ Erro de conexão: {e}")
            return False
    
    def get_existing_tables(self):
        """
        Lista tabelas existentes no banco
        """
        try:
            tables = self.inspector.get_table_names(schema="empl")
            logger.info(f"📦 Tabelas existentes no schema 'empl': {len(tables)}")
            for table in tables:
                logger.info(f"   - {table}")
            return tables
        except Exception as e:
            logger.error(f"❌ Erro ao listar tabelas: {e}")
            return []
    
    def get_metadata_tables(self):
        """
        Lista tabelas definidas nos modelos
        """
        try:
            tables = list(self.metadata.tables.keys())
            logger.info(f"📋 Tabelas definidas nos modelos: {len(tables)}")
            for table in tables:
                logger.info(f"   - {table}")
            return tables
        except Exception as e:
            logger.error(f"❌ Erro ao listar metadados: {e}")
            return []
    
    def check_table_differences(self):
        """
        Verifica diferenças entre banco e modelos
        """
        existing_tables = set(self.get_existing_tables())
        metadata_tables = set(self.get_metadata_tables())
        
        # Tabelas que existem no banco mas não nos modelos
        orphaned_tables = existing_tables - metadata_tables
        
        # Tabelas que existem nos modelos mas não no banco
        missing_tables = metadata_tables - existing_tables
        
        # Tabelas que existem em ambos
        common_tables = existing_tables & metadata_tables
        
        logger.info(f"🔍 Análise de diferenças:")
        logger.info(f"   - Tabelas órfãs (banco): {len(orphaned_tables)}")
        logger.info(f"   - Tabelas faltando (modelos): {len(missing_tables)}")
        logger.info(f"   - Tabelas comuns: {len(common_tables)}")
        
        return {
            "orphaned": orphaned_tables,
            "missing": missing_tables,
            "common": common_tables
        }
    
    def create_missing_tables(self):
        """
        Cria tabelas que estão faltando
        """
        try:
            logger.info("🚀 Criando tabelas faltantes...")
            
            # Criar apenas tabelas que não existem
            self.metadata.create_all(bind=self.engine, checkfirst=True)
            
            logger.info("✅ Tabelas criadas/atualizadas com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas: {e}")
            return False
    
    def force_recreate_all_tables(self):
        """
        FORÇA recriação de todas as tabelas (CUIDADO!)
        """
        try:
            logger.warning("⚠️ ATENÇÃO: Recriando TODAS as tabelas...")
            logger.warning("⚠️ ISSO PODE CAUSAR PERDA DE DADOS!")
            
            # Remover todas as tabelas
            self.metadata.drop_all(bind=self.engine)
            logger.info("🗑️ Tabelas removidas")
            
            # Recriar todas as tabelas
            self.metadata.create_all(bind=self.engine)
            logger.info("✅ Tabelas recriadas com sucesso!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao recriar tabelas: {e}")
            return False
    
    def safe_migrate(self):
        """
        Migração segura - apenas cria tabelas faltantes
        """
        try:
            logger.info("🔄 Iniciando migração segura...")
            
            # Verificar conexão
            if not self.test_connection():
                return False
            
            # Analisar diferenças
            differences = self.check_table_differences()
            
            # Se há tabelas faltando, criar
            if differences["missing"]:
                logger.info(f"📝 Criando {len(differences['missing'])} tabelas faltantes...")
                return self.create_missing_tables()
            else:
                logger.info("✅ Nenhuma migração necessária")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro na migração segura: {e}")
            return False
    
    def full_migrate(self):
        """
        Migração completa - recria todas as tabelas
        """
        try:
            logger.info("🔄 Iniciando migração completa...")
            
            # Verificar conexão
            if not self.test_connection():
                return False
            
            # Recriar todas as tabelas
            return self.force_recreate_all_tables()
            
        except Exception as e:
            logger.error(f"❌ Erro na migração completa: {e}")
            return False
    
    def get_migration_status(self):
        """
        Retorna status atual da migração
        """
        try:
            differences = self.check_table_differences()
            
            return {
                "status": "ready" if not differences["missing"] else "needs_migration",
                "existing_tables": len(differences["common"]),
                "missing_tables": len(differences["missing"]),
                "orphaned_tables": len(differences["orphaned"]),
                "total_metadata_tables": len(self.metadata.tables),
                "connection": self.test_connection()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter status: {e}")
            return {"status": "error", "error": str(e)}

# Instância global do migrador
migrator = AutoMigrator()

# Funções de conveniência
def auto_migrate():
    """
    Executa migração automática segura
    """
    return migrator.safe_migrate()

def force_migrate():
    """
    Executa migração completa (CUIDADO!)
    """
    return migrator.full_migrate()

def get_status():
    """
    Retorna status da migração
    """
    return migrator.get_migration_status()

def test_db():
    """
    Testa conexão com banco
    """
    return migrator.test_connection()
