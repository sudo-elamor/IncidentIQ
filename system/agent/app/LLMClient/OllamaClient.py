import os
import requests

from schemas.agent_input import AgentInput
from schemas.llm_response import LLMResponse


class LLMClient:
    def __init__(self, timeout: int = 120):
        #self.base_url = os.getenv("LLM_BASE_URL")

        self.base_url = os.getenv("LLM_BASE_URL")
        self.timeout = timeout

    def generate(self, agent_input: AgentInput) -> LLMResponse:
        url = f"{self.base_url}/generate"
        print("payload",agent_input)
        response = requests.post(
            url,
            json=agent_input,
            timeout=self.timeout,
        )

        response.raise_for_status()
        return LLMResponse(**response.json())
