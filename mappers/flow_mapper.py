"""
Mapper para flows
Converte entre Entity (domínio) e Response (API)
Seguindo padrão IT Valley Architecture
"""
from typing import Optional, List
from datetime import datetime

from schemas.flows.responses import (
    FlowResponse, 
    FlowDetailResponse, 
    FlowListResponse,
    FlowExecuteResponse,
    FlowStatsResponse
)
from domain.flows.flow_entity import FlowEntity


class FlowMapper:
    """Mapper para conversão de flows"""
    
    @staticmethod
    def to_public(flow: FlowEntity) -> FlowResponse:
        """Converte FlowEntity para FlowResponse (visão pública)"""
        return FlowResponse(
            id=flow.id,
            name=flow.name,
            description=flow.description,
            type=flow.type,
            status=flow.status,
            created_at=flow.created_at,
            updated_at=flow.updated_at,
            user_id=flow.user_id
        )
    
    @staticmethod
    def to_detail(flow: FlowEntity, stats: Optional[dict] = None) -> FlowDetailResponse:
        """Converte FlowEntity para FlowDetailResponse (visão detalhada)"""
        return FlowDetailResponse(
            id=flow.id,
            name=flow.name,
            description=flow.description,
            type=flow.type,
            status=flow.status,
            created_at=flow.created_at,
            updated_at=flow.updated_at,
            user_id=flow.user_id,
            steps=flow.steps,
            triggers=flow.triggers,
            settings=flow.settings,
            total_executions=stats.get('total_executions', 0) if stats else 0,
            last_execution=stats.get('last_execution') if stats else None,
            success_rate=stats.get('success_rate') if stats else None
        )
    
    @staticmethod
    def to_list(flows: List[FlowEntity], total: int, page: int, size: int) -> FlowListResponse:
        """Converte lista de FlowEntity para FlowListResponse"""
        return FlowListResponse(
            flows=[FlowMapper.to_public(flow) for flow in flows],
            total=total,
            page=page,
            size=size
        )
    
    @staticmethod
    def to_execution_response(result: dict, flow_id: str) -> FlowExecuteResponse:
        """Cria response para execução de flow a partir de dict do Service"""
        return FlowExecuteResponse(
            flow_id=flow_id,
            execution_id=result.get('execution_id', ''),
            status=result.get('status', 'completed'),
            steps_completed=result.get('steps_completed', 0),
            total_steps=result.get('total_steps', 0),
            execution_time=result.get('execution_time', 0.0),
            result=result.get('output_data'),
            timestamp=datetime.utcnow()
        )
    
    @staticmethod
    def to_stats(flow: FlowEntity, stats: dict) -> FlowStatsResponse:
        """Converte FlowEntity para FlowStatsResponse (estatísticas)"""
        return FlowStatsResponse(
            flow_id=flow.id,
            total_executions=stats.get('total_executions', 0),
            successful_executions=stats.get('successful_executions', 0),
            failed_executions=stats.get('failed_executions', 0),
            avg_execution_time=stats.get('avg_execution_time', 0.0),
            success_rate=stats.get('success_rate', 0.0),
            last_activity=stats.get('last_activity'),
            performance_trend=stats.get('performance_trend', 'stable')
        )
