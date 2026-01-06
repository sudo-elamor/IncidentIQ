from schemas.log_ingest import LogIngestRequest
from celery_app import celery_app
from datetime import datetime
from agent_runner import AgentRunner
from build_agent_input import build_agent_input


@celery_app.task(name="incidentiq.agent.process_log")
def process_log(payload: dict):
    #print("Processing log payload:",payload)
    ingest = LogIngestRequest(**payload)
    agent_input = build_agent_input(ingest)

    runner = AgentRunner()
    output = runner.run(agent_input)

    print("Agent inference:",output)