from fastapi import FastAPI
from datetime import datetime, timezone
from typing import Any


app = FastAPI()

THRESHOLD: float = 0.8


def calc_score(temp_c: float, humidity_pct: float, sound_db: float) -> float:
    temp_score = 1
    humid_score = 1
    sound_score = 1

    # Temperature Celsius: temp_c
    #
    # The further the temperature is from "normal", the worse
    # i.e. normal is 18°C to 24°C, midpoint 21°C
    # both negative and positive differences are bad
    # 
    if temp_c == -99: # sensor out of order
        temp_score == -1 # flag sensor being OoO
    elif (18 <= temp_c <= 24):
        temp_score = 0
    else:
        # range -270°C to 1500°C
        temp_score = abs(temp_c - 21)
    
    # Humidity %: humidity_pct
    #
    # any humidity different from 60% is not good.
    if humidity_pct == -99:
        temp_score = -1
    else:
        # range 0% to 100%
        humid_score = abs(humidity_pct - 0.60)

    # Sound dB: sound_db
    #
    # any sound different than 50 dB is not good.
    if sound_db == -99:
        sound_score = -1
    else:
        # range 0 to 310 dB
        sound_score = abs(sound_db - 50)
        

    
    score = 0.95
    
    return score



@app.get("/status")
def status():
    return {
        "status": "normal",
        "threshold": THRESHOLD,
        }

@app.post("/score")
def score(data: dict[str, Any]):
    #global THRESHOLD
    temp_c = float(data.get("temperature_c", -99))
    humidity_pct = float(data.get("humidity_pct", -99))
    sound_db = float(data.get("sound_db", -99))

    score = calc_score(temp_c, humidity_pct, sound_db)
    is_problem = score > THRESHOLD
    #print(is_problem)

    return {
        "score": score,
        "is_problem": is_problem
    }
    
    """
    return {
        "received": data,
        "timestamp": datetime.now(
                                  timezone.utc).isoformat()
    }
    """
