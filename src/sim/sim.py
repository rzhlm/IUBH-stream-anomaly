import random
import time

import requests

# from datetime import datetime, timezone

API_URL = "http://localhost:8000"
INTERVAL = 1


def sensor_output() -> dict[str, float]:
    return {
        "temperature_c": random.gauss(24, 10),  # +3 above ideal
        "humidity_pct": random.gauss(55, 8),  # -5 from ideal
        "sound_db": random.gauss(48, 8),  # -2 from ideal
    }


def main() -> None:
    try:
        while True:
            try:
                sensor_data = sensor_output()

                r = requests.post(f"{API_URL}/score", json=sensor_data, timeout=3)
                r.raise_for_status()
                score = r.json()
                print(f"{score.get("score")=}, {score.get("is_problem")=}")
                print("for sensor data:")
                print(f"   {sensor_data["temperature_c"]=}")
                print(f"   {sensor_data["humidity_pct"]=}")
                print(f"   {sensor_data["sound_db"]=}")

            except requests.RequestException as e:
                print(f" ERROR: {e}")
            time.sleep(INTERVAL)
    except Exception as e:
        print(" Aborted!")
        print(f" Error: {e}")


if __name__ == "__main__":
    main()
