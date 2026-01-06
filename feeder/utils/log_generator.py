import json
from datetime import datetime, timezone

def generate_log(row: dict, dataset: str):
    log = {
        "source" : "feeder",
        "host" : dataset,
        "logs": [{
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "INFO",
            "metadata": {}
    }]}

    for key, value in row.items():
        if value is None or value == "":
            continue
        log["logs"][0]["metadata"][key.lower()] = value
    
    COMMON_FIELDS = ["timestamp", "level", "message"]

    for field in COMMON_FIELDS:
        if field in log["logs"][0]["metadata"]:
            log["logs"][0][field] = log["logs"][0]["metadata"][field]


    return json.dumps(log)
