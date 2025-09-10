"""
Script para popular dados iniciais do System Agents
Execute este script após aplicar as migrações SQL
"""
import sys
import os
from uuid import uuid4
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data.database import DATABASE_URL
from models.system_agent_models import (
    AgentCategory, SystemAgent, SystemAgentVersion, SystemAgentVisibility,
    UserPlan, AgentStatus
)

def create_sample_data():
    """Cria dados de exemplo para o catálogo"""
    
    # Conecta ao banco
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🚀 Criando dados iniciais do System Agents...")
        
        # 1. Criar categorias
        categories = [
            {"name": "Recursos Humanos", "slug": "rh", "icon": "users", "description": "Agentes para gestão de pessoas e talentos"},
            {"name": "E-commerce", "slug": "ecommerce", "icon": "shopping-cart", "description": "Agentes para análise e otimização de vendas online"},
            {"name": "Marketing Digital", "slug": "marketing", "icon": "megaphone", "description": "Agentes para estratégias e campanhas de marketing"},
            {"name": "Análise de Dados", "slug": "analytics", "icon": "chart-bar", "description": "Agentes para análise e visualização de dados"},
            {"name": "Atendimento ao Cliente", "slug": "support", "icon": "headset", "description": "Agentes para suporte e relacionamento com clientes"}
        ]
        
        category_map = {}
        for cat_data in categories:
            category = AgentCategory(
                id=uuid4(),
                name=cat_data["name"],
                slug=cat_data["slug"],
                icon=cat_data["icon"],
                description=cat_data["description"]
            )
            db.add(category)
            category_map[cat_data["slug"]] = category.id
            print(f"✅ Categoria criada: {cat_data['name']}")
        
        db.commit()
        
        # 2. Criar agentes
        agents_data = [
            {
                "name": "Recrutador de Talentos IA",
                "description": "Analisa perfis e encontra candidatos ideais",
                "category": "rh",
                "icon": "user-search"
            },
            {
                "name": "Análise de Concorrência E-commerce", 
                "description": "Monitora preços e estratégias da concorrência",
                "category": "ecommerce",
                "icon": "search-dollar"
            },
            {
                "name": "Gerador de Conteúdo para Redes Sociais",
                "description": "Cria posts engajantes para suas redes sociais",
                "category": "marketing", 
                "icon": "share-alt"
            },
            {
                "name": "Dashboard de Métricas de Vendas",
                "description": "Gera relatórios completos de performance de vendas",
                "category": "analytics",
                "icon": "chart-line"
            },
            {
                "name": "Chatbot Inteligente de Suporte",
                "description": "Responde dúvidas dos clientes automaticamente",
                "category": "support",
                "icon": "robot"
            }
        ]
        
        agents_map = {}
        for agent_data in agents_data:
            agent = SystemAgent(
                id=uuid4(),
                name=agent_data["name"],
                short_description=agent_data["description"],
                category_id=category_map[agent_data["category"]],
                icon=agent_data["icon"],
                status=AgentStatus.ACTIVE,
                owner="system"
            )
            db.add(agent)
            agents_map[agent_data["name"]] = agent.id
            print(f"✅ Agente criado: {agent_data['name']}")
        
        db.commit()
        
        # 3. Criar versões para cada agente
        for agent_name, agent_id in agents_map.items():
            version = SystemAgentVersion(
                id=uuid4(),
                system_agent_id=agent_id,
                version="1.0.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Parâmetro de entrada"}
                    },
                    "required": ["query"]
                },
                output_schema={
                    "type": "object", 
                    "properties": {
                        "result": {"type": "string", "description": "Resultado da execução"}
                    }
                },
                orion_workflows=["workflow_sample_v1"],
                is_default=True,
                status=AgentStatus.ACTIVE
            )
            db.add(version)
            print(f"✅ Versão 1.0.0 criada para: {agent_name}")
        
        db.commit()
        
        # 4. Criar regras de visibilidade (todos os agentes visíveis para todos os planos)
        for agent_id in agents_map.values():
            for plan in UserPlan:
                visibility = SystemAgentVisibility(
                    id=uuid4(),
                    system_agent_id=agent_id,
                    tenant_id=None,  # Visível para todos os tenants
                    plan=plan,
                    region=None,  # Visível para todas as regiões
                    is_visible=True
                )
                db.add(visibility)
        
        db.commit()
        print(f"✅ Regras de visibilidade criadas para todos os planos")
        
        print("\n🎉 Dados iniciais criados com sucesso!")
        print(f"📊 {len(categories)} categorias")
        print(f"🤖 {len(agents_data)} agentes")
        print(f"📦 {len(agents_data)} versões")
        print(f"👁️ {len(agents_data) * len(UserPlan)} regras de visibilidade")
        
    except Exception as e:
        print(f"❌ Erro ao criar dados: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Função principal"""
    print("System Agents - Populador de Dados Iniciais")
    print("=" * 50)
    
    try:
        create_sample_data()
        print("\n✅ Script executado com sucesso!")
        print("\n💡 Próximos passos:")
        print("1. Execute as migrações SQL em scripts/")
        print("2. Inicie o servidor FastAPI")
        print("3. Acesse /docs para testar as APIs")
        
    except Exception as e:
        print(f"\n❌ Erro na execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
