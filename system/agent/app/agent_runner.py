from datetime import datetime
from typing import List
import uuid

from schemas.agent_input import AgentInput
from schemas.agent_output import AgentOutput, IncidentInsight
from schemas.enums import SignalType, Severity, LogCategory


class AgentRunner:
    """
    V1 agent runner
    """

    def run(self, agent_input: AgentInput) -> AgentOutput:
        relevant_logs = self._filter_relevant_logs(agent_input)
        insights = self._generate_insights(agent_input, relevant_logs)

        return AgentOutput(
            generated_at=datetime.now(),
            trace_id = agent_input.trace.batch_id,
            priority = agent_input.routing.priority,
            insights = insights,
            metadata = {
                "source" : agent_input.trace.source,
                "host" : agent_input.trace.host,
                "total_logs" : agent_input.stats.total_logs,
            }
        )
    
    def _filter_relevant_logs(self, agent_input: AgentInput):
        return [
            log for log in agent_input.logs
            if log.signal_type != SignalType.NOISE
        ]
    
    def _generate_insights(self, agent_input: AgentInput, logs) -> List[IncidentInsight]:
        if not logs:
            return []

        services = list(
            {log.service for log in logs if log.service}
        )

        highest_severity = max(
            (log.severity for log in logs),
            key=lambda s: list(Severity).index(s)
        )

        dominant_category = max(
            (log.category for log in logs),
            key=lambda c: sum(1 for l in logs if l.category == c)
        )

        return [
            IncidentInsight(
                title=f"{highest_severity.value.upper()} detected in system",
                summary=(
                    f"{len(logs)} significant log events detected across "
                    f"{len(services)} services."
                ),
                severity=highest_severity,
                category=dominant_category,
                signal_type=(
                    SignalType.FAILURE
                    if highest_severity in {Severity.ERROR, Severity.CRITICAL}
                    else SignalType.DEGRADATION
                ),
                affected_services=services,
                probable_root_cause=None,  # V1 placeholder
                recommended_actions=[
                    "Inspect service logs",
                    "Check recent deployments",
                    "Validate system health metrics",
                ],
            )
        ]

