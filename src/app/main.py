
from fastapi import FastAPI
from datetime import datetime, timezone
from typing import Any

app = FastAPI()

def calc_score(temp_c: float, humidity_pct: float, sound_db: float) -> float:
    score = 0.95
    
    return score



@app.get("/status")
def status():
    return {"status": "normal"}

@app.post("/score")
def score(data: dict[str, Any]):
    temp_c = float(data.get("temperature_c", -99))
    humidity_pct = float(data.get("humidity_pct", -99))
    sound_db = float(data.get("sound_db", -99))

    score = calc_score(temp_c, humidity_pct, sound_db)
    is_problem = lambda x:  x > 0.9
    #print(is_problem)

    return {
        "score": score,
        "is_problem": is_problem(score)
    }
    
    """
    return {
        "received": data,
        "timestamp": datetime.now(
                                  timezone.utc).isoformat()
    }
    """
