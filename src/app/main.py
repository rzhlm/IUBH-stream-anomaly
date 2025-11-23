# from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI

app = FastAPI()

THRESHOLD: float = 0.8


@app.get("/status")
def status():
    return {
        "status": "normal",
        "threshold": THRESHOLD,
    }


@app.post("/score")
def score(data: dict[str, Any]):
    # global THRESHOLD
    temp_c = float(data.get("temperature_c", -99))
    humidity_pct = float(data.get("humidity_pct", -99))
    sound_db = float(data.get("sound_db", -99))

    score = calc_score(temp_c, humidity_pct, sound_db)
    is_problem = score > THRESHOLD
    # print(is_problem)

    return {"score": score, "is_problem": is_problem}
