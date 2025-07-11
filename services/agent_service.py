"""
Serviço de agentes para o sistema EmployeeVirtual
Camada de lógica de negócio - NÃO faz consultas SQL diretas
"""
import json
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from pydantic_ai import Agent as PydanticAgent
from data.user_repository import UserRepository

from models.agent_models import (
    AgentCreate, AgentKnowledge, AgentUpdate, AgentResponse, SystemAgent
)
from data.agent_repository import AgentRepository


class AgentService:
    """
    Serviço para lógica de negócio de agentes
    Responsável apenas por orquestração e regras de negócio
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = AgentRepository(db)  # Usa o repository para dados
        self.user_repository = UserRepository(db)        
    
    def create_agent(self, user_id: int, agent_data: AgentCreate) -> AgentResponse:
        """
        Cria um novo agente personalizado
        
        Args:
            user_id: ID do usuário
            agent_data: Dados do agente
            
        Returns:
            AgentResponse: Dados do agente criado
        """
        # Preparar dados para o repository
        agent_dict = {
            "user_id": user_id,
            "name": agent_data.name,
            "description": agent_data.description,
            "agent_type": agent_data.agent_type,
            "system_prompt": agent_data.system_prompt,
            "personality": agent_data.personality,
            "avatar_url": agent_data.avatar_url,
            "llm_provider": agent_data.llm_provider,
            "model": agent_data.model,
            "temperature": agent_data.temperature,
            "max_tokens": agent_data.max_tokens
        }
        
        # Criar via repository
        db_agent = self.repository.create_agent(agent_dict)
        
        # Registrar atividade
        self.user_repository.create_activity(
            user_id=user_id,
            activity_type="agent_created", 
            description=f"Agente '{agent_data.name}' criado"
        )        
        
        return AgentResponse.from_orm(db_agent)
    
    def get_user_agents(self, user_id: int, include_system: bool = True) -> List[AgentResponse]:
        """
        Busca agentes do usuário
        
        Args:
            user_id: ID do usuário
            include_system: Incluir agentes do sistema
            
        Returns:
            Lista de agentes
        """
        # Buscar via repository
        agents = self.repository.get_agents_by_user(user_id, include_system)
        
        # Converter para response models
        return [AgentResponse.from_orm(agent) for agent in agents]
    
    def get_agent_by_id(self, agent_id: int, user_id: Optional[int] = None) -> Optional[AgentResponse]:
        """
        Busca agente por ID
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário (para verificação de propriedade)
            
        Returns:
            AgentResponse ou None se não encontrado
        """
        # Buscar via repository
        agent = self.repository.get_agent_by_id(agent_id, user_id)
        
        if not agent:
            return None
        
        return AgentResponse.from_orm(agent)
    
    def update_agent(self, agent_id: int, user_id: int, agent_data: AgentUpdate) -> Optional[AgentResponse]:
        """
        Atualiza agente
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            agent_data: Dados a serem atualizados
            
        Returns:
            AgentResponse atualizado ou None se não encontrado
        """
        agent = self.repository.get_agent_by_id(agent_id, user_id)
        
        if not agent:
            return None
        
        # Atualizar campos fornecidos
        update_data = agent_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        
        agent.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(agent)
        
        # Registrar atividade
        self.user_repository.create_activity(
            user_id=user_id,
            activity_type="agent_updated", 
            description=f"Agente '{agent_data.name}' atualizado"
        )           
        
        return AgentResponse.from_orm(agent)
    
    def delete_agent(self, agent_id: int, user_id: int) -> bool:
        """
        Deleta agente
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            
        Returns:
            True se deletado com sucesso
        """
        agent = self.repository.get_agent_by_id(agent_id, user_id)
        
        if not agent:
            return False
        
        agent_name = agent.name
        
        # Deletar agente (cascade irá deletar relacionados)
        self.db.delete(agent)
        self.db.commit()
        
        # Registrar atividade
        self.user_repository.create_activity(
            user_id=user_id,
            activity_type="agent_deleted", 
            description=f"Agente '{agent_name}' deletado"
        )        

        return True
    
    async def execute_agent(self, agent_id: int, user_id: int, user_message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executa um agente
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            user_message: Mensagem do usuário
            context: Contexto adicional
            
        Returns:
            Resultado da execução
        """
        agent = self.repository.get_agent_by_id(agent_id, user_id)
        
        if not agent:
            raise ValueError("Agente não encontrado")
        
        if agent.status != "active":
            raise ValueError("Agente não está ativo")
        
        start_time = time.time()
        
        try:
            # Preparar prompt com contexto
            system_prompt = agent.system_prompt
            if agent.personality:
                system_prompt += f"\n\nPersonalidade: {agent.personality}"
            
            # Buscar conhecimento do agente (RAG)
            knowledge_context = await self._get_agent_knowledge_context(agent_id, user_message)
            if knowledge_context:
                system_prompt += f"\n\nConhecimento específico:\n{knowledge_context}"
            
            # Executar agente PydanticAI
            model_string = f"{agent.llm_provider}:{agent.model}"
            pydantic_agent = PydanticAgent(model_string, system_prompt=system_prompt)
            
            result = await pydantic_agent.run(user_message)
            
            execution_time = time.time() - start_time
            
            # Salvar execução
            execution = AgentExecutionDB(
                agent_id=agent_id,
                user_id=user_id,
                user_message=user_message,
                response=result.output,
                model_used=model_string,
                execution_time=execution_time,
                success=True,
                context=json.dumps(context) if context else None
            )
            
            self.db.add(execution)
            
            # Atualizar estatísticas do agente
            agent.last_used = datetime.utcnow()
            agent.usage_count += 1
            
            self.db.commit()
            
            # Registrar atividade
            self.user_repository.create_activity(
                user_id=user_id,
                activity_type="agent_executed", 
                description=f"Agente '{agent.name}' executado"
            )                 

            
            return {
                "agent_id": agent_id,
                "agent_name": agent.name,
                "user_message": user_message,
                "response": result.output,
                "model_used": model_string,
                "execution_time": execution_time,
                "success": True
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_message = str(e)
            
            # Salvar execução com erro
            execution = AgentExecutionDB(
                agent_id=agent_id,
                user_id=user_id,
                user_message=user_message,
                response="",
                model_used=f"{agent.llm_provider}:{agent.model}",
                execution_time=execution_time,
                success=False,
                error_message=error_message,
                context=json.dumps(context) if context else None
            )
            
            self.db.add(execution)
            self.db.commit()
            
            return {
                "agent_id": agent_id,
                "agent_name": agent.name,
                "user_message": user_message,
                "response": "",
                "model_used": f"{agent.llm_provider}:{agent.model}",
                "execution_time": execution_time,
                "success": False,
                "error_message": error_message
            }
    
    def get_agent_executions(self, agent_id: int, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Busca execuções do agente
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            limit: Limite de execuções
            
        Returns:
            Lista de execuções
        """
        executions = self.db.query(AgentExecutionDB).filter(
            and_(
                AgentExecutionDB.agent_id == agent_id,
                AgentExecutionDB.user_id == user_id
            )
        ).order_by(desc(AgentExecutionDB.created_at)).limit(limit).all()
        
        return [
            {
                "id": execution.id,
                "user_message": execution.user_message,
                "response": execution.response,
                "model_used": execution.model_used,
                "execution_time": execution.execution_time,
                "success": execution.success,
                "error_message": execution.error_message,
                "created_at": execution.created_at
            }
            for execution in executions
        ]
    
    def add_knowledge_to_agent(self, agent_id: int, user_id: int, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adiciona conhecimento ao agente
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            file_data: Dados do arquivo
            
        Returns:
            Dados do conhecimento adicionado
        """
        # Verificar se agente existe e pertence ao usuário
        agent = self.repository.get_agent_by_id(agent_id, user_id)
        
        if not agent:
            raise ValueError("Agente não encontrado")
        
        knowledge = AgentKnowledge(
            agent_id=agent_id,
            file_name=file_data["file_name"],
            file_type=file_data["file_type"],
            file_size=file_data["file_size"],
            file_url=file_data["file_url"],
            orion_file_id=file_data.get("orion_file_id")
        )
        
        self.db.add(knowledge)
        self.db.commit()
        self.db.refresh(knowledge)
        
        # Registrar atividade
        self.user_repository.create_activity(
            user_id=user_id,
            activity_type="agent_knowledge_added", 
            description=f"Conhecimento adicionado ao agente '{agent.name}'"
        )           
        
        return {
            "id": knowledge.id,
            "agent_id": agent_id,
            "file_name": knowledge.file_name,
            "file_type": knowledge.file_type,
            "processed": knowledge.processed,
            "created_at": knowledge.created_at
        }
    
    def get_system_agents(self) -> List[Dict[str, Any]]:
        """
        Busca agentes do sistema
        
        Returns:
            Lista de agentes do sistema
        """
        system_agents = self.db.query(SystemAgent).filter(
            SystemAgent.is_active == True
        ).all()
        
        return [
            {
                "id": agent.id,
                "name": agent.name,
                "description": agent.description,
                "agent_type": agent.agent_type,
                "avatar_url": agent.avatar_url,
                "orion_endpoint": agent.orion_endpoint
            }
            for agent in system_agents
        ]
    
    async def _get_agent_knowledge_context(self, agent_id: int, query: str) -> Optional[str]:
        """
        Busca contexto da base de conhecimento do agente
        
        Args:
            agent_id: ID do agente
            query: Query para busca
            
        Returns:
            Contexto relevante ou None
        """
        # TODO: Implementar busca semântica no Pinecone
        # Por enquanto, retorna None (sem RAG)
        return None
    


