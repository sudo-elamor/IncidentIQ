from sqlalchemy import Column, BigInteger, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base

class RawLog(Base):
    __tablename__ = "raw_logs"
    # Remove partitioning
    # __table_args__ = {"postgresql_partition_by": "RANGE (timestamp)"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    source = Column(Text, nullable=False)
    service = Column(Text, nullable=False)
    host = Column(Text)
    level = Column(Text)
    message = Column(Text, nullable=False)
    meta = Column(JSONB)
