from sqlalchemy import Column, BigInteger, Text, TIMESTAMP, JSON
from sqlalchemy.dialects.postgresql import JSONB
from db.base import Base


class RawLog(Base):
    __tablename__ = "raw_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    source = Column(Text, nullable=False)
    service = Column(Text, nullable=False)
    host = Column(Text)
    level = Column(Text)
    message = Column(Text, nullable=False)
    meta = Column(JSON)
