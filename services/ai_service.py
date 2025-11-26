"""
Serviço de IA - Integração com Pydantic AI
Fornece capacidades de IA para agentes e chat
Seguindo padrão IT Valley Architecture
"""
import logging
import os
from typing import Optional, Dict, Any
from pydantic_ai import Agent
from pydantic import BaseModel

from config.settings import settings
from integrations.ai.rag_agent import RagAgentRunner

logger = logging.getLogger(__name__)


class AIResponse(BaseModel):
    """Resposta padrão da IA"""
    response: str


# Singleton para AIService (evita múltiplas inicializações do Pinecone)
_ai_service_instance: Optional['AIService'] = None


class AIService:
    """
    Serviço de IA - Orquestra integração com modelos de IA
    Usa Pydantic AI como abstração de modelos
    Singleton pattern para evitar múltiplas inicializações do Pinecone
    """
    
    def __init__(self):
        """Inicializa o serviço de IA com configurações globais"""
        self.openai_api_key = settings.openai_api_key
        # Configura a variável de ambiente para Pydantic AI
        if self.openai_api_key:
            os.environ["OPENAI_API_KEY"] = self.openai_api_key
        
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY não configurada. IA não funcionará.")

        # Usa pinecone_index_name se definido, senão usa vector_db_index_name (padrão "employee")
        rag_index_name = settings.pinecone_index_name or settings.vector_db_index_name
        self.supports_rag = bool(settings.pinecone_api_key and rag_index_name)
        self.rag_runner: Optional[RagAgentRunner] = None
        if self.supports_rag:
            try:
                logger.info("🔧 Inicializando RagAgentRunner (índice: %s)", rag_index_name)
                self.rag_runner = RagAgentRunner(rag_index_name)
                logger.info("✅ RagAgentRunner inicializado com sucesso")
            except Exception as exc:
                logger.error("Falha ao inicializar RagAgentRunner: %s", exc, exc_info=True)
                self.supports_rag = False
    
    @classmethod
    def get_instance(cls) -> 'AIService':
        """
        Retorna instância singleton do AIService.
        Evita múltiplas inicializações do Pinecone.
        """
        global _ai_service_instance
        if _ai_service_instance is None:
            _ai_service_instance = cls()
        return _ai_service_instance
    
    async def generate_response(
        self,
        message: str,
        system_prompt: str = "Você é um assistente útil e amigável.",
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        temperature: float = 0.7,
        model: str = "gpt-4-turbo-preview",
        max_tokens: int = 2000
    ) -> str:
        """
        Gera resposta usando modelo de IA via Pydantic AI (ASYNC)
        
        Args:
            message: Mensagem do usuário
            system_prompt: Prompt do sistema/agente
            agent_id: ID do agente (para logging)
            user_id: ID do usuário (para logging)
            temperature: Criatividade da resposta (0-1)
            model: Modelo a usar
            max_tokens: Máximo de tokens na resposta
            
        Returns:
            str: Resposta gerada pela IA
            
        Raises:
            ValueError: Se API key não configurada
        """
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY não configurada")
        
        try:
            logger.info(f"🤖 Gerando resposta com IA para usuário={user_id}, agente={agent_id}")
            logger.debug(f"   message={message[:100]}... model={model}")
            
            # Cria agent do Pydantic AI com tipo de saída definido
            agent = Agent(
                model=f"openai:{model}",
                system_prompt=system_prompt,
                output_type=AIResponse
            )
            
            # Executa agent de forma async
            result = await agent.run(message)
            
            # Extrai resposta
            response_text = result.data.response if hasattr(result.data, 'response') else str(result.data)
            
            logger.info(f"✅ Resposta gerada com sucesso. Tokens aproximados: {len(response_text.split())}")
            
            return response_text
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resposta com IA: {str(e)}", exc_info=True)
            raise

    def generate_rag_response_sync(
        self,
        message: str,
        agent_id: str,
        agent_name: str,
        instructions: Optional[str]
    ) -> str:
        """
        Executa resposta usando agente RAG quando suportado.
        """
        if not self.rag_runner:
            return self.generate_response_sync(
                message=message,
                system_prompt=instructions or f"Você é o agente {agent_name}.",
                agent_id=agent_id,
                user_id=None
            )

        try:
            logger.info("🔎 Executando fluxo RAG para agente %s", agent_id)
            return self.rag_runner.run(
                agent_id=agent_id,
                agent_name=agent_name,
                instructions=instructions,
                user_message=message,
            )
        except Exception as exc:
            logger.error("Erro no fluxo RAG, fallback para resposta padrão: %s", exc, exc_info=True)
            return self.generate_response_sync(
                message=message,
                system_prompt=instructions or f"Você é o agente {agent_name}.",
                agent_id=agent_id,
                user_id=None
            )
    
    def generate_response_sync(
        self,
        message: str,
        system_prompt: str = "Você é um assistente útil e amigável.",
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        temperature: float = 0.7,
        model: str = "gpt-4-turbo-preview",
        max_tokens: int = 2000
    ) -> str:
        """
        Gera resposta usando modelo de IA via Pydantic AI (SYNC)
        Versão síncrona para uso em contextos não-async
        
        Args:
            message: Mensagem do usuário
            system_prompt: Prompt do sistema/agente
            agent_id: ID do agente (para logging)
            user_id: ID do usuário (para logging)
            temperature: Criatividade da resposta (0-1)
            model: Modelo a usar
            max_tokens: Máximo de tokens na resposta
            
        Returns:
            str: Resposta gerada pela IA
            
        Raises:
            ValueError: Se API key não configurada
        """
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY não configurada")
        
        try:
            logger.info(f"🤖 Gerando resposta com IA para usuário={user_id}, agente={agent_id}")
            logger.debug(f"   message={message[:100]}... model={model}")
            
            # Cria agent do Pydantic AI com tipo de saída definido
            agent = Agent(
                model=f"openai:{model}",
                system_prompt=system_prompt,
                output_type=AIResponse
            )
            
            # Executa agent de forma síncrona
            result = agent.run_sync(message)
            
            # Extrai resposta
            response_text = result.data.response if hasattr(result.data, 'response') else str(result.data)
            
            logger.info(f"✅ Resposta gerada com sucesso. Tokens aproximados: {len(response_text.split())}")
            
            return response_text
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resposta com IA: {str(e)}", exc_info=True)
            raise
    
    async def process_agent_message(
        self,
        message: str,
        agent_config: Dict[str, Any],
        conversation_history: Optional[list] = None
    ) -> str:
        """
        Processa mensagem usando configuração específica do agente
        
        Args:
            message: Mensagem do usuário
            agent_config: Configuração do agente (name, system_prompt, model, temperature, etc)
            conversation_history: Histórico de conversa anterior
            
        Returns:
            str: Resposta gerada
        """
        system_prompt = agent_config.get('system_prompt', f"Você é um assistente chamado {agent_config.get('name', 'Agente')}.")
        model = agent_config.get('model', 'gpt-4-turbo-preview')
        temperature = float(agent_config.get('temperature', 0.7))
        max_tokens = int(agent_config.get('max_tokens', 2000))
        
        # Monta contexto com histórico se disponível
        full_message = message
        if conversation_history:
            # Limita histórico aos últimos 5 mensagens para economizar tokens
            recent_history = conversation_history[-10:]
            history_text = "\n".join([
                f"{h['role']}: {h['content']}"
                for h in recent_history
            ])
            full_message = f"Histórico da conversa:\n{history_text}\n\nNova mensagem do usuário: {message}"
        
        return await self.generate_response(
            message=full_message,
            system_prompt=system_prompt,
            temperature=temperature,
            model=model,
            max_tokens=max_tokens
        )
