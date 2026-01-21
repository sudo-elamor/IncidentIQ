import threading
from fastapi import FastAPI,Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from metrics.collector import collect

app = FastAPI()

@app.on_event("startup")
def start():
    t = threading.Thread(target=collect, daemon=True)
    t.start()

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )