from datetime import datetime
from typing import List
from requests import RequestException
import logging

from schemas.agent_input import AgentInput
from schemas.agent_output import AgentOutput, IncidentInsight
from schemas.enums import SignalType, Severity, LogCategory
from LLMClient.OllamaClient import LLMClient

logger = logging.getLogger(__name__)

PRIORITY_TO_SEVERITY = {
    5: Severity.CRITICAL,
    4: Severity.CRITICAL,
    3: Severity.ERROR,
    2: Severity.WARN,
    1: Severity.INFO,
}

# ======================
# PIPELINE TOGGLES
# ======================
ENABLE_ROUTING_GATE = False     # ← set True for prod
ENABLE_NOISE_FILTER = False      # ← set True for prod
MIN_LOGS_FOR_LLM = 1            # ← set 2+ later


class AgentRunner:
    def __init__(self):
        self.llm_client = LLMClient()

    def run(self, agent_input: AgentInput) -> AgentOutput:
        logger.info(
            "AgentRunner start batch=%s priority=%s attention=%s",
            agent_input.trace.batch_id,
            agent_input.trace.routing.priority,
            agent_input.trace.routing.requires_attention,
        )

        # 1. Optional routing gate
        if ENABLE_ROUTING_GATE and not agent_input.routing.requires_attention:
            logger.info("Routing gate active → skipping LLM")
            insights = self._generate_insights(agent_input, agent_input.logs)
            return self._build_output(agent_input, insights)

        # 2. Filter logs (optional)
        relevant_logs = self._filter_relevant_logs(agent_input)

        # 3. Weak signal → rules
        if len(relevant_logs) < MIN_LOGS_FOR_LLM:
            logger.info(
                "Not enough logs for LLM (%d), using rules",
                len(relevant_logs),
            )
            insights = self._generate_insights(agent_input, relevant_logs)
            return self._build_output(agent_input, insights)

        # 4. LLM path
        try:
            logger.debug("Sending %d logs to LLM", len(relevant_logs))
            llm_payload = self._convert_to_llm_input(agent_input, relevant_logs)

            llm_response = self.llm_client.generate(llm_payload)
            logger.info("LLM response received")

            insights = self._convert_llm_response(agent_input, llm_response)

        except (RequestException, TimeoutError, ValueError) as e:
            logger.exception("LLM failed → fallback to rules")
            insights = self._generate_insights(agent_input, relevant_logs)

        return self._build_output(agent_input, insights)

    # ---------------------------------------------------

    def _filter_relevant_logs(self, agent_input: AgentInput):
        """
        Filter logs without mutating them.
        Synthetic forcing should NEVER happen in prod path.
        """
        if not ENABLE_NOISE_FILTER:
            return agent_input.logs

        # Example future filter (optional)
        return [
            log for log in agent_input.logs
            if log.signal_type != SignalType.NOISE
        ]



    # ---------------------------------------------------

    def _convert_to_llm_input(self, agent_input: AgentInput, logs: list):
        return {
            "raw_log_id": agent_input.raw_log_id,
            "source": agent_input.source,
            "host": agent_input.host,
            "logs": [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.severity.value,
                    "message": log.message or "<empty>",
                    "signal_type": log.signal_type.value,
                }
                for log in logs
            ],
        }


    # ---------------------------------------------------

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
                signal_type=(
                    SignalType.FAILURE
                    if llm_response.priority >= 4
                    else SignalType.DEGRADATION
                ),
                affected_services=services,
                probable_root_cause=None,
                recommended_actions=llm_response.recommended_actions,
            )
        ]

    # ---------------------------------------------------

    def _generate_insights(self, agent_input: AgentInput, logs) -> List[IncidentInsight]:
        if not logs:
            return []

        services = list({log.service for log in logs if log.service})

        highest_severity = max(
            (log.severity for log in logs),
            key=lambda s: list(Severity).index(s)
        )

        return [
            IncidentInsight(
                title=f"{highest_severity.value.upper()} activity detected",
                summary=(
                    f"{len(logs)} log events detected across "
                    f"{len(services)} services."
                ),
                severity=highest_severity,
                category=LogCategory.APPLICATION,
                signal_type=(
                    SignalType.FAILURE
                    if highest_severity in {Severity.ERROR, Severity.CRITICAL}
                    else SignalType.NOISE
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

    # ---------------------------------------------------

    def _build_output(self, agent_input: AgentInput, insights):
        return AgentOutput(
            generated_at=datetime.now(),
            trace_id=agent_input.trace.batch_id,
            priority=agent_input.trace.routing.priority,
            insights=insights,
            metadata={
                "source": agent_input.source,
                "host": agent_input.host,
                "total_logs": str(agent_input.trace.stats.total_logs),
            },
        )
