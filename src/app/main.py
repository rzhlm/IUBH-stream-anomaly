# from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI

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
    if temp_c == -99:  # sensor out of order
        temp_score = -1  # flag sensor being OoO
    elif 18 <= temp_c <= 24:
        temp_score = 0
    else:
        # possible temp range -270°C to 1500°C
        # realistically, no production if:
        # temp < 5°C or temp > 60°C
        # so total useful range is 55°C
        if temp_c <= 5:
            temp_c = 5
        elif temp_c > 60:
            temp_c = 60
        temp_score = abs(temp_c - 21)  # between 21-5 and 55-21
        # := 16 and 34
        # normalize:
        temp_score /= 34  # 55
        # between 0 and 0.618

    print(f"{temp_c=}; {temp_score=}")

    # Humidity %: humidity_pct
    #
    # any humidity different from 60% is not good.
    if humidity_pct == -99:
        humid_score = -1  # out of order
    else:
        # range 0% to 100%
        humid_score = abs(humidity_pct - 60)
        # thus, between 0 and 40
        # back to a float%
        humid_score /= 40
    print(f"{humidity_pct=}; {humid_score=}")

    # Sound dB: sound_db
    #
    # any sound different than 50 dB is not good.
    if sound_db == -99:
        sound_score = -1  # out of order
    else:
        # possible range 0 to 310 dB
        # realistically:
        # more than 50 db is bad, if it's higher than 90 something is wrong,
        # less means something is wrong
        # working range: 0 to 90
        if sound_db >= 90:
            sound_db = 90
        sound_score = abs(sound_db - 50)  # between 0 and 50
        sound_score /= 50  # between 0 and 0.56
    print(f"{sound_db=}; {sound_score=}")

    # TODO: treat out-of-order values and ignore that sensor
    score = temp_score + humid_score + sound_score
    if score > 1:
        score = 1
    print(f"{score=}")

    # score = 0.95

    return score


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
