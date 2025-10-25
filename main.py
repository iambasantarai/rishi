import time
from fastapi import FastAPI, status

tags_metadata = [
    {
        "name": "heartbeat",
        "description": "Heartbeat of a server",
    },
]

app = FastAPI(
    title="Rishi",
    version="0.0.1",
    openapi_tags=tags_metadata
)

@app.get("/heartbeat", status_code=status.HTTP_200_OK, tags=["heartbeat"])
def heartbeat():
    heartbeat = time.monotonic_ns()
    return {"heartbeat": heartbeat}
