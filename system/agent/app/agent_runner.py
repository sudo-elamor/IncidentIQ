from datetime import datetime
from typing import List
from requests import RequestException

from schemas.agent_input import AgentInput
from schemas.agent_output import AgentOutput, IncidentInsight
from schemas.enums import SignalType, Severity, LogCategory
from LLMClient.OllamaClient import LLMClient
import logging

logger = logging.getLogger(__name__)

PRIORITY_TO_SEVERITY = {
    3: Severity.CRITICAL,
    2: Severity.ERROR,
    1: Severity.WARN,
    0: Severity.INFO,
}


class AgentRunner:
    def __init__(self):
        self.llm_client = LLMClient()

    def run(self, agent_input: AgentInput) -> AgentOutput:
        relevant_logs = self._filter_relevant_logs(agent_input)

        if relevant_logs:
            try:
                llm_payload = self._convert_to_llm_input(agent_input, relevant_logs)
                print("payload sent to llm", llm_payload)
                llm_response = self.llm_client.generate(llm_payload)
                logger.info("LLM response received %s", llm_response)
                insights = self._convert_llm_response(relevant_logs, llm_response)
            except (RequestException, TimeoutError, ValueError) as e:
                logger.exception("LLM failed, falling back to rule engine")
                insights = self._generate_insights(agent_input, relevant_logs)
        else:
            logger.warning("No relevant logs for LLM, using rule engine directly")
            insights = self._generate_insights(agent_input, agent_input.logs)

            return AgentOutput(
                generated_at=datetime.now(),
                trace_id=agent_input.trace.batch_id,
                priority=agent_input.routing.priority,
                insights=insights,
                metadata={
                    "source": agent_input.trace.source,
                    "host": agent_input.trace.host,
                    "total_logs": str(agent_input.stats.total_logs),
                },
            )

    def _convert_llm_response(
        self, agent_input: AgentInput, llm_response
    ) -> List[IncidentInsight]:
        services = list(
            {log.service for log in agent_input.logs if log.service}
        )

        return [
            IncidentInsight(
                title=llm_response.incident_type.replace("_", " ").title(),
                summary=llm_response.summary,
                severity=PRIORITY_TO_SEVERITY.get(
                    llm_response.priority, Severity.INFO
                ),
                category=LogCategory.APPLICATION,
                signal_type=SignalType.FAILURE,
                affected_services=services,
                probable_root_cause=None,
                recommended_actions=llm_response.recommended_actions,
            )
        ]

    def _filter_relevant_logs(self, agent_input: AgentInput):
        return [
            log for log in agent_input.logs
            #if log.signal_type != SignalType.NOISE
        ]
    
    def _convert_to_llm_input(self, agent_input: AgentInput, logs: list):
        """
        Convert AgentInput + filtered logs into LLM-friendly schema.
        """
        return {
            "source": agent_input.trace.source,
            "host": agent_input.trace.host,
            "logs": [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.severity.value,       # use enum value
                    "message": log.message,
                    "signal_type": log.signal_type.value,  # required by LLM
                }
                for log in logs
            ],
        }





    def _generate_insights(self, agent_input: AgentInput, logs) -> List[IncidentInsight]:
        if not logs:
            return []

        services = list({log.service for log in logs if log.service})

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
                probable_root_cause=None,
                recommended_actions=[
                    "Inspect service logs",
                    "Check recent deployments",
                    "Validate system health metrics",
                ],
            )
        ]
