"""
Módulo de entidades de dados
Responsável apenas pelo mapeamento objeto-relacional
"""
from .dashboard_entities import (
    UserMetricsEntity,
    AgentMetricsEntity, 
    FlowMetricsEntity,
    SystemMetricsEntity
)

from .agent_entities import (
    AgentEntity,
    AgentKnowledgeEntity,
    AgentExecutionEntity,
    SystemAgentEntity
)

from .user_entities import (
    UserEntity,
    UserSessionEntity,
    UserActivityEntity
)

from .chat_entities import (
    ConversationEntity,
    MessageEntity,
    ConversationContextEntity,
    MessageReactionEntity
)

from .flow_entities import (
    FlowEntity,
    FlowStepEntity,
    FlowExecutionEntity,
    FlowExecutionStepEntity,
    FlowTemplateEntity
)

from .file_entities import (
    FileEntity,
    FileProcessingEntity,
    OrionServiceEntity,
    DataLakeFileEntity
)

__all__ = [
    # Dashboard entities
    "UserMetricsEntity",
    "AgentMetricsEntity",
    "FlowMetricsEntity", 
    "SystemMetricsEntity",
    # Agent entities
    "AgentEntity",
    "AgentKnowledgeEntity",
    "AgentExecutionEntity",
    "SystemAgentEntity",
    # User entities
    "UserEntity",
    "UserSessionEntity",
    "UserActivityEntity",
    # Chat entities
    "ConversationEntity",
    "MessageEntity",
    "ConversationContextEntity",
    "MessageReactionEntity",
    # Flow entities
    "FlowEntity",
    "FlowStepEntity",
    "FlowExecutionEntity",
    "FlowExecutionStepEntity",
    "FlowTemplateEntity",
    # File entities
    "FileEntity",
    "FileProcessingEntity",
    "OrionServiceEntity",
    "DataLakeFileEntity"
]
