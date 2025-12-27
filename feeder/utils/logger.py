import logging
import json
import requests
from config import LOG_MODE, LOG_FILE, HTTP_ENDPOINT, HTTP_TIMEOUT

# Configure logger instance
logger = logging.getLogger("feeder")
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Choose handler based on LOG_MODE
if LOG_MODE == "stdout":
    handler = logging.StreamHandler()
elif LOG_MODE == "file":
    handler = logging.FileHandler(LOG_FILE)
else:
    # For HTTP, still log locally as fallback
    handler = logging.StreamHandler()

handler.setFormatter(formatter)
logger.addHandler(handler)


def log_output(log: str):
    """
    Outputs a log according to LOG_MODE.
    Supports stdout, file, or HTTP POST.
    """
    log_dict = json.loads(log)

    if LOG_MODE in ("stdout", "file"):
        logger.info(json.dumps(log_dict))
    
    elif LOG_MODE == "http":
        try:
            resp = requests.post(
                HTTP_ENDPOINT, json={"log": log_dict}, timeout=HTTP_TIMEOUT
            )
            if resp.status_code >= 400:
                logger.warning(f"Failed to send log via HTTP: {resp.status_code}")
        except requests.RequestException as e:
            logger.error(f"Exception sending log via HTTP: {e}")
    
    else:
        logger.error(f"Unsupported LOG_MODE: {LOG_MODE}")
