from fastapi import FastAPI
from pydantic import ValidationError
from schemas import AgentInput, LLMResponse
from client import OllamaClient
from prompt_builder import build_prompt
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


@app.post("/generate", response_model=LLMResponse)
def generate_incident(agent_input: AgentInput):
    prompt = build_prompt(agent_input)
    raw_response = client.generate(prompt)

    logger.warning("LLM raw output:\n%s", raw_response)

    try:
        raw = raw_response.strip()

        start = raw.find("{")
        end = raw.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("No JSON object found in LLM output")

        raw_json = raw[start:end+1]
        parsed = json.loads(raw_json)

        return LLMResponse(**parsed)

    except Exception as e:
        logger.exception("Invalid LLM output, falling back")
        return LLMResponse(
            priority=0,
            incident_type="unknown",
            summary="LLM output invalid",
            confidence=0.0,
            metadata={"error": str(e)}
        )
