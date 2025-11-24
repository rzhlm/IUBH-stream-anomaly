import csv
import random
import sys
import time

import requests

# from datetime import datetime, timezone

API_URL: str = "http://localhost:8000"
SLEEP_INTERVAL: int = 1
TRAINING_FILE: str = "./src/training/sensor-training-data.csv"
ANOMALY_FREQUENCY: int = 10  # how often to generate anomalous data


def generate_single(is_anomaly: bool = False) -> dict[str, float]:
    if is_anomaly:
        # pass
        return {
            "temperature_c": round(random.gauss(80, 2), 3),
            "humidity_pct": round(random.gauss(10, 5), 3),
            "sound_db": round(random.gauss(90, 5), 3),
        }
    else:
        return {
            "temperature_c": round(random.gauss(21, 2), 3),
            "humidity_pct": round(random.gauss(60, 5), 3),
            "sound_db": round(random.gauss(50, 5), 3),
        }


def generate_all(filename: str, n_rows: int = 1_000):
    print(f"generate {n_rows} of training data, into {filename}")
    with open(filename, mode="w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "temperature_c",
                "humidity_pct",
                "sound_db",
            ],
        )
        writer.writeheader()

        for i in range(n_rows):
            is_anomaly = True if i % 100 == 0 else False  # creating 1% abnormals
            data = generate_single(is_anomaly=is_anomaly)
            writer.writerow(data)

    print("finished")


def run_simulation():
    print("-" * 80)
    print("starting live stream (simulated)")
    counter: int = 0

    try:
        while True:
            # force an anomaly based on setting
            force_anomaly: bool = (counter % ANOMALY_FREQUENCY == 0) and (counter > 0)
            data: dict[str, float] = generate_single(is_anomaly=force_anomaly)

            try:
                resp: requests.Response = requests.post(
                    f"{API_URL}/score", json=data, timeout=3
                )
                if resp.status_code != 200:
                    print(
                        f"ERROR in live stream, API server returns {resp.status_code}!"
                    )
                    print(f"response: {resp.text}")
                    continue
                result: dict[str, bool | float | str] = resp.json()

                status: str = "ANOMALY" if result["is_anomaly"] else "NORMAL"
                print(
                    f"sent: {data=} with {status=} and score: {result['anomaly_score']}"
                )
            except requests.exceptions.JSONDecodeError:
                print(f"live stream: JSON ERROR. API server says: {resp.text}")
            except Exception as e:
                print(f"general simulation failure: error: {e}")

            counter += 1
            counter = 1 if counter >= 5_000 # to avoid high mem use / overflow when running for long periods of time
            time.sleep(SLEEP_INTERVAL)

    except KeyboardInterrupt:
        print("\n stopping.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "train":
        generate_all(TRAINING_FILE)
    else:
        run_simulation()
