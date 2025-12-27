import json
from datetime import datetime, timezone

def generate_log(row: dict, dataset: str):
    log = {
        "ingest_timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "feeder",
        "dataset": dataset,
        "data": {}
    }

    for key, value in row.items():
        if value is None or value == "":
            continue
        log["data"][key.lower()] = value
    
    COMMON_FIELDS = ["timestamp", "level", "message"]

    for field in COMMON_FIELDS:
        if field in log["data"]:
            log[field] = log["data"][field]


    return json.dumps(log)
