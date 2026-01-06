from typing import List, Dict, Optional
from pydantic import BaseModel


class LLMResponse(BaseModel):
    priority: int
    incident_type: str
    summary: str
    confidence: float
    recommended_actions: List[str] = []
    metadata: Dict[str, str] = {}
