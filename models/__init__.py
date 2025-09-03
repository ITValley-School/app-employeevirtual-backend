"""
Importa todos os modelos para registro na base SQLAlchemy
"""
from .user_models import *
from .agent_models import *
from .chat_models import *
from .dashboard_models import *
from .file_models import *
from .flow_models import *
from .llm_models import *

# Lista todos os modelos importados
__all__ = [
    # User models
    "User", "UserSession", "UserActivity", "UserMetrics",
    
    # Agent models  
    "Agent", "AgentExecutionDB", "AgentKnowledge", "AgentMetricsDB", "SystemAgent",
    
    # Chat models
    "Conversation", "Message", "ConversationContext", "MessageReaction",
    
    # Dashboard models
    "SystemMetrics", "FlowMetricsDB",
    
    # File models
    "File", "FileProcessing", "DataLakeFile",
    
    # Flow models
    "Flow", "FlowStep", "FlowExecution", "FlowExecutionStep", "FlowTemplate",
    
    # LLM models
    "SystemLLMKey", "UserLLMKey",
    
    # Orion models
    "OrionService"
]

