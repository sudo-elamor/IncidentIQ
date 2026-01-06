import json
from schemas import AgentInput

SYSTEM_PROMPT = """
You are an incident classification engine.

Return ONLY valid JSON.
Do NOT include explanations.

Fields:
priority: integer (0-5)
incident_type: short string
summary: one sentence
confidence: float (0-1)

Analyze the logs and decide severity.

Logs:
{LOGS}
"""

def build_prompt(agent_input: AgentInput) -> str:
    context = {
        "source": agent_input.source,
        "host": agent_input.host,
        "logs": [
            {"timestamp": l.timestamp, "level": l.level, "message": l.message, "signal_type": l.signal_type}
            for l in agent_input.logs
        ],
    }
    return f"{SYSTEM_PROMPT}\nAnalyze the following logs and classify the incident.\nInput:\n{json.dumps(context, indent=2)}"
