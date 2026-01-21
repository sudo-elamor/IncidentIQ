from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Float,
    DateTime,
    JSON,
    func,
)
from db.base import Base

class AgentResult(Base):
    __tablename__ = "agent_results"

    id = Column(BigInteger, primary_key=True)
    raw_log_id = Column(Integer, index=True)
    
    batch_id = Column(String, index=True, nullable=False)
    source = Column(String, index=True, nullable=False)

    priority = Column(Integer, nullable=False)
    incident_type = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)

    insights = Column(JSON)     
    meta = Column(JSON)     

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
