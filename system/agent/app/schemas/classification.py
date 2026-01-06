from pydantic import BaseModel, Field
from typing import List

class ClassificationResult(BaseModel):
    severity: str = Field(..., example="ERROR")
    category: str = Field(..., example="application")
    signal_type: str = Field(..., example="failure")
    confidence: float = Field(..., ge=0.0, le=1.0)
    keywords: List[str]
