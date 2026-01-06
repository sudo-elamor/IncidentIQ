from datetime import datetime
from typing import List
import uuid

from schemas.agent_input import (
    AgentInput,
    AgentLog,
    LogStats,
    RoutingHint,
    AgentTrace,
)

from schemas.log_ingest import LogIngestRequest
from schemas.enums import SignalType
from tools.classifier import classify_log

def build_agent_input(payload: LogIngestRequest) -> AgentInput:
    enriched_logs: List[AgentLog] = []
    services = set()

    failure_count = degradation_count = noise_count = 0
    timestamps = []

    for log in payload.logs:
        classification = classify_log(log)

        if classification.signal_type == SignalType.FAILURE:
            failure_count += 1
        elif classification.signal_type == SignalType.DEGRADATION:
            degradation_count += 1
        else:
            noise_count += 1
        
        if log.service:
            services.add(log.service)
        
        timestamps.append(log.timestamp)

        enriched_logs.append(
            AgentLog(
                timestamp = log.timestamp,
                severity = classification.severity,
                category = classification.category,
                signal_type = classification.signal_type,
                service = log.service,
                message = log.message or "",
                metadata = log.metadata or {},
            )
        )
    
    stats = LogStats(
        total_logs = len(payload.logs),
        failure_count = failure_count,
        degradation_count = degradation_count,
        noise_count = noise_count,
        services_involved = list(services),
        window_start = min(timestamps),
        window_end = max(timestamps),
    )

    if failure_count > 0:
        priority = 5
        requires_attention = True
    elif degradation_count > 0:
        priority = 3
        requires_attention = True
    else:
        priority = 1
        requires_attention = False
    
    routing = RoutingHint(
        priority = priority,
        requires_attention = requires_attention,
    )

    trace = AgentTrace(
        source = payload.source or "",
        host = payload.host or "",
        batch_id = str(uuid.uuid4()),
        received_at = datetime.now(),
    )

    return AgentInput(
        trace = trace,
        logs = enriched_logs,
        stats = stats,
        routing = routing,
    )