import os
import json
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2:3b")

        logger.info("OllamaClient initialized base_url=%s model=%s", self.base_url, self.model)

    def generate(self, prompt: str) -> str:
        """
        Streaming-safe generation.
        Returns final aggregated response string.
        """

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 160,
                "temperature": 0.2,
                "top_p": 0.9,
                "repeat_penalty": 1.1
            }
        }


        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=True,
                timeout=(5, None),
            )
            resp.raise_for_status()

            output_chunks = []

            for line in resp.iter_lines():
                if not line:
                    continue

                data = json.loads(line)

                if data.get("response"):
                    output_chunks.append(data["response"])

                if data.get("done"):
                    break

            final_output = "".join(output_chunks).strip()
            return final_output

        except requests.exceptions.Timeout:
            logger.exception("Ollama request timed out")
            raise

        except Exception as e:
            logger.exception("Ollama generation failed")
            raise RuntimeError(f"Ollama error: {e}")
