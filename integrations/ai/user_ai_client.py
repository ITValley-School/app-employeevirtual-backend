"""
Cliente de IA para usuários
Seguindo padrão IT Valley Architecture
"""
from typing import Dict, Any, Optional
from datetime import datetime

from schemas.users.responses import UserResponse


class UserAIPayload:
    """Payload para análise de IA de usuário"""
    def __init__(self, user_id: str, user_data: Dict[str, Any]):
        self.user_id = user_id
        self.user_data = user_data


class UserAIResponse:
    """Response de análise de IA de usuário"""
    def __init__(self, score_engagement: float, category: str, recommendations: list[str]):
        self.score_engagement = score_engagement
        self.category = category
        self.recommendations = recommendations


class UserAIClient:
    """
    Cliente para integração com IA para usuários
    Isola detalhes de IA do resto do sistema
    """
    
    def __init__(self, ai_service_url: str, api_key: str):
        self.ai_service_url = ai_service_url
        self.api_key = api_key
    
    def analyze_user_profile(self, payload: UserAIPayload) -> UserAIResponse:
        """
        Analisa perfil do usuário com IA
        
        Args:
            payload: Dados do usuário para análise
            
        Returns:
            UserAIResponse: Análise da IA
        """
        # Simula chamada para serviço de IA
        # Em implementação real, faria HTTP request
        
        # Análise simulada baseada nos dados
        user_data = payload.user_data
        
        # Calcula score de engajamento
        score = self._calculate_engagement_score(user_data)
        
        # Determina categoria
        category = self._determine_user_category(score, user_data)
        
        # Gera recomendações
        recommendations = self._generate_recommendations(category, user_data)
        
        return UserAIResponse(
            score_engagement=score,
            category=category,
            recommendations=recommendations
        )
    
    def _calculate_engagement_score(self, user_data: Dict[str, Any]) -> float:
        """Calcula score de engajamento"""
        # Lógica simulada
        total_agents = user_data.get('total_agents', 0)
        total_flows = user_data.get('total_flows', 0)
        total_executions = user_data.get('total_executions', 0)
        
        # Score baseado em atividade
        score = min(1.0, (total_agents * 0.3 + total_flows * 0.4 + total_executions * 0.3) / 100)
        
        return round(score, 2)
    
    def _determine_user_category(self, score: float, user_data: Dict[str, Any]) -> str:
        """Determina categoria do usuário"""
        plan = user_data.get('plan', 'free')
        
        if score >= 0.8:
            return "power_user"
        elif score >= 0.5:
            return "active_user"
        elif plan != "free":
            return "premium_user"
        else:
            return "basic_user"
    
    def _generate_recommendations(self, category: str, user_data: Dict[str, Any]) -> list[str]:
        """Gera recomendações personalizadas"""
        recommendations = []
        
        if category == "power_user":
            recommendations.extend([
                "Considere upgrade para Enterprise",
                "Explore automações avançadas",
                "Configure integrações externas"
            ])
        elif category == "active_user":
            recommendations.extend([
                "Experimente novos tipos de agentes",
                "Crie workflows mais complexos",
                "Analise métricas de performance"
            ])
        elif category == "premium_user":
            recommendations.extend([
                "Aproveite recursos premium",
                "Configure notificações avançadas",
                "Explore templates profissionais"
            ])
        else:
            recommendations.extend([
                "Experimente criar seu primeiro agente",
                "Explore templates gratuitos",
                "Considere upgrade para mais recursos"
            ])
        
        return recommendations
    
    def get_user_insights(self, user_id: str, period_days: int = 30) -> Dict[str, Any]:
        """
        Gera insights do usuário
        
        Args:
            user_id: ID do usuário
            period_days: Período em dias
            
        Returns:
            dict: Insights gerados
        """
        # Simula geração de insights
        return {
            "user_id": user_id,
            "period_days": period_days,
            "insights": {
                "productivity_trend": "increasing",
                "most_used_features": ["agents", "flows", "chat"],
                "optimization_suggestions": [
                    "Configure automações para tarefas repetitivas",
                    "Use templates para acelerar criação",
                    "Monitore métricas de performance"
                ]
            },
            "generated_at": datetime.utcnow().isoformat()
        }
