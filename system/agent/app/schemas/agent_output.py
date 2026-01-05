from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

from schemas.enums import Severity, LogCategory, SignalType


class IncidentInsight(BaseModel):
    title: str
    summary: str
    severity: Severity
    category: LogCategory
    signal_type: SignalType
    affected_services: List[str]
    probable_root_cause: Optional[str]
    recommended_actions: List[str]

class AgentOutput(BaseModel):
    generated_at: datetime
    trace_id: str
    priority: int
    insights: List[IncidentInsight]
    metadata: Dict[str, Any] = Field(default_factory=dict)
