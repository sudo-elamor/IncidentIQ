from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime

class LogEntry(BaseModel):
    timestamp: datetime = Field(..., example="2025-12-28T09:15:12Z")
    level: str = Field(..., example="INFO")
    service: Optional[str] = None
    message: Optional[str] = None
    metadata: Dict[str, str] = Field(default_factory=dict)

class LogIngestRequest(BaseModel):
    raw_log_id: int = Field(..., example=12345)
    source: str = Field(..., example="feeder")
    host: str = Field(..., example="feeder-01")
    logs: List[LogEntry]
