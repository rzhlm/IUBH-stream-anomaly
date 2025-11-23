from typing import TYPE_CHECKING

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

if TYPE_CHECKING:
    import numpy as np

INPUT_FILE: str = "./src/training/sensor-training-data.csv"
MODEL_FILE: str = "./src/training/model.joblib"


def train_model():
    # pass
    try:
        print(f"loading training data from {INPUT_FILE}")
        df: pd.DataFrame = pd.read_csv(INPUT_FILE)
        feature_cols: list[str] = [
            "temperature_c",
            "humidity_pct",
            "sound_db",
        ]

        X_train: np.ndarray = df[feature_cols].to_numpy()
        print("training IsolationForest")

        clf: IsolationForest = IsolationForest(n_estimators=100, contamination=0.01)
        clf.fit(X_train)

        joblib.dump(clf, MODEL_FILE)
        print("model saved")

    except FileNotFoundError:
        print(f"file not found: (inputfile) {INPUT_FILE}")
        print("remember to generate it first")


if __name__ == "__main__":
    train_model()
