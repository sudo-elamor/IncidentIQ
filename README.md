# IncidentIQ

IncidentIQ is an end-to-end **incident intelligence platform** that ingests system logs, processes them asynchronously, and applies AI agents to analyze, explain, and surface actionable insights from incidents.

This project is intentionally designed to demonstrate **real-world backend engineering, distributed systems thinking, and applied AI integration** — not just a toy demo.

---

## 🚀 Key Capabilities

* **Log Ingestion Pipeline** – Structured and unstructured logs ingested via a feeder service
* **Asynchronous Processing** – Message-based workload smoothing using Redis + Celery
* **Microservice Architecture** – Clear separation of ingestion, API, workers, and AI agents
* **AI-Driven Analysis** – Local LLM (Ollama) used for log summarization and incident reasoning
* **Containerized Deployment** – Fully orchestrated using Docker Compose

---

## 🧱 System Architecture (v1)

```
[ Log Source ]
      |
      v
[ Feeder Service ]
      |
      v
[ FastAPI Service ]
      |
      v
[ Message Broker (Redis) ]
      |
      v
[ Worker Service ]
      |
      v
[ AI Agent (Ollama) ]
```

### Design Principles

* Loose coupling between services
* Async-first processing for bursty log traffic
* AI as an **analysis layer**, not a blocking dependency
* MVP-first: optimized for clarity and interview readiness

---

## 🧩 Microservices Overview

### 1. Feeder Service

* Reads and sends logs to the API service
* Simulates real-world log producers

### 2. API Service (FastAPI)

* Accepts incoming logs
* Performs validation and routing
* Pushes tasks to the message broker

### 3. Message Broker (Redis + Celery)

* Decouples ingestion from processing
* Smooths spikes in log volume
* Enables horizontal scaling of workers

### 4. Worker Service

* Consumes tasks from the broker
* Performs preprocessing and enrichment
* Dispatches logs to AI agents

### 5. AI Agent Service (Ollama)

* Local LLM-based analysis
* Generates summaries, explanations, and incident insights
* Latency-aware, non-blocking design

---

## 🐳 Running the Project

### Prerequisites

* Docker & Docker Compose
* Python 3.10+
* Ollama installed locally

### Start All Services

```bash
docker compose up --build
```

### Start a Single Service (Example)

```bash
docker compose up api
```

---

## 📊 What v1 Solves

* Demonstrates an **end-to-end incident pipeline**
* Shows how AI fits into real backend systems
* Handles asynchronous workloads safely
* Provides a clear scaling path without over-engineering

---

## 🛑 What v1 Intentionally Does NOT Include

* Kafka (planned upgrade from Redis)
* Advanced observability (Prometheus/Grafana)
* Multi-tenant auth or RBAC
* SLA enforcement

These are deliberately deferred to avoid premature complexity.

---

## 🗺️ Future Roadmap (Conceptual)

* Kafka-based streaming ingestion
* Advanced incident correlation
* Agent-based root cause analysis
* Production-grade observability

> These are planned **on paper only**; v1 is considered complete.

---

## 🎯 Project Status

**IncidentIQ v1 is complete and feature-frozen.**

The focus going forward is documentation, interview readiness, and architectural discussions — not feature creep.

---

