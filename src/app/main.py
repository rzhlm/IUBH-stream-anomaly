# from datetime import datetime, timezone
# from typing import Any

# from datetime import datetime
import datetime

# import time
from contextlib import asynccontextmanager

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class SensorData(BaseModel):
    temperature_c: float
    humidity_pct: float
    sound_db: float


class PredictionOut(BaseModel):
    is_anomaly: bool
    anomaly_score: float
    status: str


ml_model = None
RECENT_SCORES: list[dict] = []
MAX_RECENT = 150
MODEL_FILE: str = "./src/training/model.joblib"


@asynccontextmanager
async def lifespan(app: FastAPI):
    global ml_model
    try:
        ml_model = joblib.load(MODEL_FILE)
        print("ML model loaded")
    except FileNotFoundError:
        print("model.joblib not found. Perhaps run training first")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/status")
def get_status():
    return {
        "service": "Anomaly Detection",
        "model_loaded": ml_model is not None,
    }


@app.post("/score", response_model=PredictionOut)
def predict_anomaly(data: SensorData):
    # start_time = time.perf_counter()
    if not ml_model:
        raise HTTPException(status_code=503, detail="Model not availalbe")

    features: np.ndarray = np.array(
        [[data.temperature_c, data.humidity_pct, data.sound_db]]
    )
    prediction: int = ml_model.predict(features)[0]  # -1: abnormal, 1: normal
    score: float = ml_model.decision_function(features)[0]  # lower is worse

    if prediction == -1:
        is_anomaly = True
    else:
        is_anomaly = False

    result = PredictionOut(
        is_anomaly=is_anomaly,
        anomaly_score=score,
        status="anomaly" if is_anomaly else "normal",
    )

    RECENT_SCORES.append(
        {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "temperature_c": data.temperature_c,
            "humidity_pct": data.humidity_pct,
            "sound_db": data.sound_db,
            "is_anomaly": is_anomaly,
            "anomaly_score": score,
        }
    )
    if len(RECENT_SCORES) > MAX_RECENT:
        RECENT_SCORES.pop(0)

    # return {
    # "is_anomaly": is_anomaly,
    # "anomaly_score": float(score),
    # "status": "Anomaly detected" if is_anomaly else "Normal",
    # }
    # duration_time = time.perf_counter() - start_time
    # print(f"inside API (POST): {duration_time=:.3f}")
    return result


# @app.get("/recent_scores", response_model = List[])
@app.get("/recent_scores")
def recent_scores(limit: int = 20):
    if limit <= 0:
        limit = 1
    return RECENT_SCORES[-limit:]
