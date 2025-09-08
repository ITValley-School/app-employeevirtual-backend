"""
Serviço de agentes para o sistema EmployeeVirtual
Camada de lógica de negócio - NÃO faz consultas SQL diretas
"""
import json
import time
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from pydantic_ai import Agent as PydanticAgent

from models.agent_models import (
    AgentCreate, AgentUpdate, AgentResponse, AgentType, AgentStatus, LLMProvider
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
    
    def create_agent(self, user_id: str, agent_data: AgentCreate) -> AgentResponse:
        """
        Cria um novo agente personalizado
        
        Args:
            user_id: ID do usuário
            agent_data: Dados do agente
            
        Returns:
            AgentResponse: Dados do agente criado
        """
        # Validações de negócio
        if not agent_data.name or len(agent_data.name.strip()) < 2:
            raise ValueError("Nome do agente deve ter pelo menos 2 caracteres")
        
        if not agent_data.system_prompt or len(agent_data.system_prompt.strip()) < 10:
            raise ValueError("Prompt do sistema deve ter pelo menos 10 caracteres")
        
        # Preparar dados para o repository
        agent_dict = {
            "user_id": user_id,
            "name": agent_data.name.strip(),
            "description": agent_data.description,
            "agent_type": agent_data.agent_type,
            "system_prompt": agent_data.system_prompt.strip(),
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
        self._log_user_activity(
            user_id, 
            "agent_created", 
            f"Agente '{agent_data.name}' criado"
        )
        
        return AgentResponse.from_orm(db_agent)

    def validate_agent_config(self, agent_data: AgentCreate) -> Dict[str, Any]:
        """
        Valida configuração de agente sem criar no banco
        
        Args:
            agent_data: Dados do agente
        
        Returns:
            Dict com validação: { valid, errors, warnings, normalized }
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Validações básicas
        if not agent_data.name or len(agent_data.name.strip()) < 2:
            errors.append("Nome do agente deve ter pelo menos 2 caracteres")

        if not agent_data.system_prompt or len(agent_data.system_prompt.strip()) < 10:
            errors.append("Prompt do sistema deve ter pelo menos 10 caracteres")

        if not agent_data.llm_provider:
            errors.append("Provedor LLM é obrigatório")

        if not agent_data.model or len(str(agent_data.model).strip()) == 0:
            errors.append("Modelo LLM é obrigatório")

        # Faixa de temperatura
        if agent_data.temperature is not None:
            try:
                temp = float(agent_data.temperature)
                if temp < 0.0 or temp > 2.0:
                    errors.append("Temperature deve estar entre 0.0 e 2.0")
            except (TypeError, ValueError):
                errors.append("Temperature inválida")

        # max_tokens opcional, mas pode sugerir limite
        if agent_data.max_tokens is not None:
            try:
                mt = int(agent_data.max_tokens)
                if mt <= 0:
                    errors.append("max_tokens deve ser positivo")
                elif mt > 8000:
                    warnings.append("max_tokens alto; pode aumentar custo/latência")
            except (TypeError, ValueError):
                errors.append("max_tokens inválido")

        normalized = {
            "name": agent_data.name.strip() if agent_data.name else agent_data.name,
            "description": agent_data.description,
            "agent_type": agent_data.agent_type,
            "system_prompt": agent_data.system_prompt.strip() if agent_data.system_prompt else agent_data.system_prompt,
            "personality": agent_data.personality,
            "avatar_url": agent_data.avatar_url,
            "llm_provider": str(agent_data.llm_provider),
            "model": str(agent_data.model),
            "temperature": agent_data.temperature,
            "max_tokens": agent_data.max_tokens,
        }

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "normalized": normalized,
        }
    
    def get_user_agents(self, user_id: str, include_system: bool = True) -> List[AgentResponse]:
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
        # Converter agentes para response models, tratando enums
        response_agents = []
        for agent in agents:
            agent = self._convert_agent_enums(agent)
            response_agents.append(AgentResponse.from_orm(agent))
        
        return response_agents
    
    def get_agent_by_id(self, agent_id: str, user_id: Optional[str] = None) -> Optional[AgentResponse]:
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
        
        # Converter strings para enums se necessário
        if isinstance(agent.agent_type, str):
            try:
                agent.agent_type = AgentType(agent.agent_type)
            except ValueError:
                agent.agent_type = AgentType.CUSTOM
        
        if isinstance(agent.status, str):
            try:
                agent.status = AgentStatus(agent.status)
            except ValueError:
                agent.status = AgentStatus.ACTIVE
                
        if isinstance(agent.llm_provider, str):
            try:
                agent.llm_provider = LLMProvider(agent.llm_provider)
            except ValueError:
                agent.llm_provider = LLMProvider.OPENAI
        
        return AgentResponse.from_orm(agent)
    
    def update_agent(self, agent_id: str, user_id: str, agent_data: AgentUpdate) -> Optional[AgentResponse]:
        """
        Atualiza agente
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            agent_data: Dados a serem atualizados
            
        Returns:
            AgentResponse atualizado ou None se não encontrado
        """
        # Validações de negócio
        update_data = agent_data.dict(exclude_unset=True)
        
        if "name" in update_data and len(update_data["name"].strip()) < 2:
            raise ValueError("Nome do agente deve ter pelo menos 2 caracteres")
        
        if "system_prompt" in update_data and len(update_data["system_prompt"].strip()) < 10:
            raise ValueError("Prompt do sistema deve ter pelo menos 10 caracteres")
        
        # Limpar strings
        if "name" in update_data:
            update_data["name"] = update_data["name"].strip()
        if "system_prompt" in update_data:
            update_data["system_prompt"] = update_data["system_prompt"].strip()
        
        # Atualizar via repository
        agent = self.repository.update_agent(agent_id, user_id, update_data)
        
        if not agent:
            return None
        
        # Registrar atividade
        self._log_user_activity(
            user_id, 
            "agent_updated", 
            f"Agente '{agent.name}' atualizado"
        )
        
        # Converter strings para enums se necessário
        if isinstance(agent.agent_type, str):
            try:
                agent.agent_type = AgentType(agent.agent_type)
            except ValueError:
                agent.agent_type = AgentType.CUSTOM
        
        if isinstance(agent.status, str):
            try:
                agent.status = AgentStatus(agent.status)
            except ValueError:
                agent.status = AgentStatus.ACTIVE
                
        if isinstance(agent.llm_provider, str):
            try:
                agent.llm_provider = LLMProvider(agent.llm_provider)
            except ValueError:
                agent.llm_provider = LLMProvider.OPENAI
        
        return AgentResponse.from_orm(agent)
    
    def delete_agent(self, agent_id: str, user_id: str) -> bool:
        """
        Deleta agente
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            
        Returns:
            True se deletado com sucesso
        """
        # Buscar agente para obter nome antes de deletar
        agent = self.repository.get_agent_by_id(agent_id, user_id)
        if not agent:
            return False
        
        agent_name = agent.name
        
        # Deletar via repository
        success = self.repository.delete_agent(agent_id, user_id)
        
        if success:
            # Registrar atividade
            self._log_user_activity(
                user_id, 
                "agent_deleted", 
                f"Agente '{agent_name}' deletado"
            )
        
        return success
    
    async def execute_agent(self, agent_id: str, user_id: str, user_message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
        # Validações de negócio
        if not user_message or len(user_message.strip()) < 1:
            raise ValueError("Mensagem não pode estar vazia")
        
        # Buscar agente via repository
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
            # Validar se o modelo está definido
            if not agent.model or agent.model.strip() == "":
                # Usar modelo padrão baseado no provedor
                default_models = {
                    "openai": "gpt-4o-mini",
                    "anthropic": "claude-3-5-sonnet-latest", 
                    "google": "gemini-2.0-flash-exp",
                    "groq": "llama-3.1-8b-instant",
                    "mistral": "mistral-large-latest",
                    "cohere": "command-r-plus",
                    "deepseek": "deepseek-chat"
                }
                model_name = default_models.get(agent.llm_provider, "gpt-4o-mini")
                print(f"⚠️ Modelo não definido para agente {agent_id}, usando padrão: {model_name}")
                
                # Corrigir no banco de dados para futuras execuções
                try:
                    agent.model = model_name
                    self.db.commit()
                    print(f"✅ Modelo corrigido no banco de dados: {model_name}")
                except Exception as e:
                    print(f"⚠️ Erro ao corrigir modelo no banco: {e}")
            else:
                model_name = agent.model.strip()
            
            # Construir model_string limpo (sem parâmetros)
            # Converter enum para string (o enum LLMProvider já tem valores como strings)
            provider_str = agent.llm_provider.value if hasattr(agent.llm_provider, 'value') else str(agent.llm_provider)
            
            model_string = f"{provider_str}:{model_name}"
            
            print(f"🔧 Model string construído: {model_string}")
            print(f"🔧 Parâmetros: temperature={agent.temperature}, max_tokens={agent.max_tokens}")
            
            # Configurar variáveis de ambiente para o Pydantic AI
            await self._configure_llm_environment(agent, user_id)
            
            # Criar agente Pydantic AI (versão 0.3.6)
            # Usar apenas o model_string limpo - parâmetros são ignorados pelo Pydantic AI
            pydantic_agent = PydanticAgent(model_string, system_prompt=system_prompt)
            
            result = await pydantic_agent.run(user_message.strip())
            
            execution_time = time.time() - start_time
            
            # Salvar execução via repository
            execution_data = {
                "agent_id": agent_id,
                "user_id": user_id,
                "user_message": user_message.strip(),
                "response": result.output,
                "model_used": model_string,
                "execution_time": execution_time,
                "success": True,
                "context": json.dumps(context) if context else None
            }
            
            self.repository.create_execution(execution_data)
            
            # Atualizar estatísticas do agente
            self.repository.update_agent_stats(agent_id)
            
            # Registrar atividade
            self._log_user_activity(
                user_id, 
                "agent_executed", 
                f"Agente '{agent.name}' executado"
            )
            
            return {
                "agent_id": agent_id,
                "agent_name": agent.name,
                "user_message": user_message.strip(),
                "response": result.output,
                "model_used": model_string,
                "execution_time": execution_time,
                "success": True
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_message = str(e)
            
            # Salvar execução com erro via repository
            execution_data = {
                "agent_id": agent_id,
                "user_id": user_id,
                "user_message": user_message.strip(),
                "response": "",
                "model_used": f"{agent.llm_provider}:{agent.model}",
                "execution_time": execution_time,
                "success": False,
                "error_message": error_message,
                "context": json.dumps(context) if context else None
            }
            
            self.repository.create_execution(execution_data)
            
            return {
                "agent_id": agent_id,
                "agent_name": agent.name,
                "user_message": user_message.strip(),
                "response": "",
                "model_used": f"{agent.llm_provider}:{agent.model}",
                "execution_time": execution_time,
                "success": False,
                "error_message": error_message
            }
    
    def get_agent_executions(self, agent_id: str, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Busca execuções do agente
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            limit: Limite de execuções
            
        Returns:
            Lista de execuções
        """
        # Validar limite
        if limit < 1 or limit > 100:
            limit = 50
        
        # Buscar via repository
        executions = self.repository.get_agent_executions(agent_id, user_id, limit)
        
        # Converter para dict
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
    
    def add_knowledge_to_agent(self, agent_id: str, user_id: str, file_data: Dict[str, Any]) -> Dict[str, Any]:
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
        
        # Validações de negócio
        required_fields = ["file_name", "file_type", "file_size", "file_url"]
        for field in required_fields:
            if field not in file_data or not file_data[field]:
                raise ValueError(f"Campo obrigatório: {field}")
        
        # Preparar dados para repository
        knowledge_data = {
            "agent_id": agent_id,
            "file_name": file_data["file_name"],
            "file_type": file_data["file_type"],
            "file_size": file_data["file_size"],
            "file_url": file_data["file_url"],
            "orion_file_id": file_data.get("orion_file_id")
        }
        
        # Criar via repository
        knowledge = self.repository.create_knowledge(knowledge_data)
        
        # Registrar atividade
        self._log_user_activity(
            user_id, 
            "agent_knowledge_added", 
            f"Conhecimento adicionado ao agente '{agent.name}'"
        )
        
        return {
            "id": knowledge.id,
            "agent_id": agent_id,
            "file_name": knowledge.file_name,
            "file_type": knowledge.file_type,
            "processed": knowledge.processed,
            "created_at": knowledge.created_at
        }
    
    def get_agent_knowledge(self, agent_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Busca base de conhecimento do agente
        
        Args:
            agent_id: ID do agente
            user_id: ID do usuário
            
        Returns:
            Lista de arquivos de conhecimento
        """
        # Verificar se agente existe e pertence ao usuário
        agent = self.repository.get_agent_by_id(agent_id, user_id)
        if not agent:
            raise ValueError("Agente não encontrado")
        
        # Buscar conhecimento via repository
        knowledge_files = self.repository.get_agent_knowledge(agent_id)
        
        return [
            {
                "id": k.id,
                "file_name": k.file_name,
                "file_type": k.file_type,
                "file_size": k.file_size,
                "processed": k.processed,
                "created_at": k.created_at,
                "processed_at": k.processed_at
            }
            for k in knowledge_files
        ]
    
    def get_system_agents(self) -> List[Dict[str, Any]]:
        """
        Busca agentes do sistema
        
        Returns:
            Lista de agentes do sistema
        """
        # Buscar via repository
        system_agents = self.repository.get_system_agents()
        
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
    
    async def _get_agent_knowledge_context(self, agent_id: str, query: str) -> Optional[str]:
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
    
    def _convert_agent_enums(self, agent):
        """Converte strings para enums se necessário"""
        if isinstance(agent.agent_type, str):
            try:
                agent.agent_type = AgentType(agent.agent_type)
            except ValueError:
                agent.agent_type = AgentType.CUSTOM
        
        if isinstance(agent.status, str):
            try:
                agent.status = AgentStatus(agent.status)
            except ValueError:
                agent.status = AgentStatus.ACTIVE
                
        if isinstance(agent.llm_provider, str):
            try:
                agent.llm_provider = LLMProvider(agent.llm_provider)
            except ValueError:
                agent.llm_provider = LLMProvider.OPENAI
        
        return agent
    
    def _log_user_activity(self, user_id: str, activity_type: str, description: str):
        """
        Registra atividade do usuário
        
        Args:
            user_id: ID do usuário
            activity_type: Tipo da atividade
            description: Descrição da atividade
        """
        activity_data = {
            "user_id": user_id,
            "activity_type": activity_type,
            "description": description
        }
        
        self.repository.log_user_activity(activity_data)
    
    async def _configure_llm_environment(self, agent, user_id: str):
        """
        Configura variáveis de ambiente para o Pydantic AI
        
        Args:
            agent: Agente com configurações LLM
            user_id: ID do usuário
        """
        try:
            # Importar serviço de chaves LLM
            from services.llm_key_service import LLMKeyService
            llm_key_service = LLMKeyService(self.db)
            
            # Tentar obter chave do agente
            key_info = await llm_key_service.get_key_for_agent(agent.id, user_id)
            
            if key_info:
                # Configurar variável de ambiente com a chave
                provider = key_info['provider'].upper()
                api_key = key_info['api_key']
                
                if provider == 'OPENAI':
                    os.environ['OPENAI_API_KEY'] = api_key
                    print(f"✅ OPENAI_API_KEY configurada para agente {agent.id}")
                elif provider == 'ANTHROPIC':
                    os.environ['ANTHROPIC_API_KEY'] = api_key
                    print(f"✅ ANTHROPIC_API_KEY configurada para agente {agent.id}")
                elif provider == 'GOOGLE':
                    os.environ['GOOGLE_API_KEY'] = api_key
                    print(f"✅ GOOGLE_API_KEY configurada para agente {agent.id}")
                elif provider == 'GROQ':
                    os.environ['GROQ_API_KEY'] = api_key
                    print(f"✅ GROQ_API_KEY configurada para agente {agent.id}")
                elif provider == 'MISTRAL':
                    os.environ['MISTRAL_API_KEY'] = api_key
                    print(f"✅ MISTRAL_API_KEY configurada para agente {agent.id}")
                elif provider == 'COHERE':
                    os.environ['COHERE_API_KEY'] = api_key
                    print(f"✅ COHERE_API_KEY configurada para agente {agent.id}")
                elif provider == 'DEEPSEEK':
                    os.environ['DEEPSEEK_API_KEY'] = api_key
                    print(f"✅ DEEPSEEK_API_KEY configurada para agente {agent.id}")
                else:
                    print(f"⚠️ Provedor {provider} não suportado para configuração automática")
            else:
                # Verificar se já existe variável de ambiente
                provider = str(agent.llm_provider).upper()
                env_var = f"{provider}_API_KEY"
                
                if os.getenv(env_var):
                    print(f"✅ {env_var} já configurada nas variáveis de ambiente")
                else:
                    print(f"⚠️ Nenhuma chave encontrada para agente {agent.id} e {env_var} não está configurada")
                    
        except Exception as e:
            print(f"⚠️ Erro ao configurar ambiente LLM: {e}")
            # Continuar execução mesmo com erro de configuração
