from fastapi import FastAPI, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from schemas import AgentInput, LLMResponse
from client import OllamaClient
from db.session import SessionLocal
from db.models.agent_results import AgentResult
from prompt_builder import build_prompt
from metrics import (
    llm_api_requests_total,
    llm_api_success_total,
    llm_api_failure_total,
    llm_api_parse_failure_total,
    llm_api_llm_error_total
)
import json
import logging
import os

logger = logging.getLogger(__name__)
app = FastAPI(title="LLM Service")

client = OllamaClient()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")


@app.on_event("startup")
def warmup_llm():
    try:
        client.generate("Return OK")
        logger.info("LLM warmed up successfully")
    except Exception as e:
        logger.warning(f"LLM warmup failed: {e}")


@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.post("/generate", response_model=LLMResponse)
def generate_incident(agent_input: AgentInput):
    llm_api_requests_total.inc()

    try:
        prompt = build_prompt(agent_input)

        try:
            print("\n\n\nprompt sent to llm for generation",prompt,"\n\n\n")
            raw_response = client.generate(prompt)
        except Exception as e:
            llm_api_llm_error_total.inc()
            llm_api_failure_total.inc()
            logger.exception("LLM invocation failed")
            raise e

        logger.warning("LLM raw output:\n%s", raw_response)

        raw = raw_response.strip()
        start = raw.find("{")
        end = raw.rfind("}")

        if start == -1 or end == -1:
            llm_api_parse_failure_total.inc()
            llm_api_failure_total.inc()
            raise ValueError("No JSON object found in LLM output")

        raw_json = raw[start:end + 1]
        parsed = json.loads(raw_json)

        response = LLMResponse(**parsed)

        with SessionLocal() as db:
            db.add(
                AgentResult(
                    raw_log_id=agent_input.raw_log_id,
                    batch_id=str(agent_input.raw_log_id),
                    source=agent_input.source,

                    priority=response.priority,
                    incident_type=response.incident_type,
                    summary=response.summary,
                    confidence=response.confidence,

                    insights=parsed,         
                    meta=agent_input.dict(),
                )
            )
            db.commit()


        llm_api_success_total.inc()
        return LLMResponse(**parsed)

    except Exception as e:
        logger.exception("Invalid LLM output, falling back")

        return LLMResponse(
            priority=0,
            incident_type="unknown",
            summary="LLM output invalid",
            confidence=0.0,
            metadata={"error": str(e)},
        )
