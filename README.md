# IncidentIQ
A portfolio project that leverages system designing and langGraph that works with clients system logs and provide valuable insights and analysis

Architechtural design
┌────────────┐
│  Feeder    │
└────┬───────┘
     ↓
┌────────────┐
│ FastAPI    │  (Ingest)
└────┬───────┘
     ↓
┌────────────┐
│ Message    │  (Kafka / RabbitMQ / Redis)
│ Broker     │
└────┬───────┘
     ↓
┌────────────┐
│ Workers    │  (Celery)
└────┬───────┘
     ↓
┌────────────┐
│ LangChain  │  (Brain Service)
└────┬───────┘
     ↓
┌────────────┐
│ Postgres   │
└────────────┘
