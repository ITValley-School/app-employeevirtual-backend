"""
Entidades de dados para agentes
Responsabilidade: Mapeamento objeto-relacional e persistência
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, text
from sqlalchemy.sql import func
from data.base import Base


class AgentEntity(Base):
    """Entidade de agentes"""
    __tablename__ = "agents"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    agent_type = Column(String(50), nullable=False)
    system_prompt = Column(Text, nullable=False)
    personality = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False)
    llm_provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    temperature = Column(Float, default=0.7, nullable=False)
    max_tokens = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_used = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f"<AgentEntity(id={self.id}, name='{self.name}', type='{self.agent_type}')>"


class AgentKnowledgeEntity(Base):
    """Entidade de base de conhecimento dos agentes"""
    __tablename__ = "agent_knowledge"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(String(36), primary_key=True, server_default=text("NEWID()"), index=True)
    agent_id = Column(String(36), ForeignKey('empl.agents.id'), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_url = Column(String(500), nullable=False)
    orion_file_id = Column(String(100), nullable=True)  # ID do arquivo no Orion
    processed = Column(Boolean, default=False, nullable=False)
    vector_ids = Column(Text, nullable=True)  # JSON array de IDs dos vetores no Pinecone
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<AgentKnowledgeEntity(id={self.id}, agent_id={self.agent_id}, file='{self.file_name}')>"


class AgentExecutionEntity(Base):
    """Entidade de execuções de agentes"""
    __tablename__ = "agent_executions"
    __table_args__ = {'schema': 'empl'}
    
    id = Column(String(36), primary_key=True, server_default=text("NEWID()"), index=True)
    agent_id = Column(String(36), ForeignKey('empl.agents.id'), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    user_message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    model_used = Column(String(100), nullable=False)
    execution_time = Column(Float, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    success = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text, nullable=True)
    context = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AgentExecutionEntity(id={self.id}, agent_id={self.agent_id}, success={self.success})>"


# REMOVIDO: SystemAgentEntity
# Esta classe foi movida para models/system_agent_models.py como SystemAgent
# Para evitar conflito de tabela duplicada no SQLAlchemy
#
# class SystemAgentEntity(Base):
#     """Entidade de agentes do sistema (pré-configurados)"""
#     __tablename__ = "system_agents"
#     __table_args__ = {'schema': 'empl'}
#     
#     id = Column(String(36), primary_key=True, server_default=text("NEWID()"), index=True)
#     name = Column(String(100), nullable=False, unique=True)
#     description = Column(Text, nullable=False)
#     agent_type = Column(String(50), nullable=False)
#     system_prompt = Column(Text, nullable=False)
#     avatar_url = Column(String(500), nullable=True)
#     orion_endpoint = Column(String(200), nullable=True)  # Endpoint específico no Orion
#     is_active = Column(Boolean, default=True, nullable=False)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now())
#     
#     def __repr__(self):
#         return f"<SystemAgentEntity(id={self.id}, name='{self.name}', type='{self.agent_type}')>"
