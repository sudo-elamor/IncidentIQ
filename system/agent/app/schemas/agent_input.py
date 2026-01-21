from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime

from schemas.enums import Severity, LogCategory, SignalType

class AgentLog(BaseModel):
    timestamp: datetime
    severity: Severity
    category: LogCategory
    signal_type: SignalType
    service: str | None
    message: str
    metadata: Dict[str, str]

class LogStats(BaseModel):
    total_logs: int
    failure_count: int
    degradation_count: int
    noise_count: int
    services_involved: List[str]
    window_start: datetime
    window_end: datetime

class RoutingHint(BaseModel):
    priority: int  # 1–5
    requires_attention: bool

class AgentTrace(BaseModel):
    batch_id: str
    received_at: datetime
    stats: LogStats | None = None      
    routing: RoutingHint | None = None


class AgentInput(BaseModel):
    raw_log_id: int
    source: str
    host: str
    logs: List[AgentLog]
    trace: AgentTrace

