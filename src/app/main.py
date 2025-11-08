
from fastapi import FastAPI
from datetime import datetime, timezone
from typing import Any

app = FastAPI()

@app.get("/status")
def status():
    return {"status": "normal"}

@app.post("/score")
def score(data: dict[str, Any]):
    return {
        "received": data,
        "timestamp": datetime.now(
                                  timezone.utc).isoformat()
    }
