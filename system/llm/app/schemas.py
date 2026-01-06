from pydantic import BaseModel
from typing import List, Optional

class LogContext(BaseModel):
    timestamp: str
    level: str
    message: str
    signal_type: str

class AgentInput(BaseModel):
    source: str
    host: str
    logs: List[LogContext]

class LLMResponse(BaseModel):
    priority: int
    incident_type: str
    summary: str
    confidence: float
    metadata: Optional[dict] = {}