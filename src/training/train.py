"""
trains the ML prediction model (IsolationForest) on the training data
saves it using the common joblib structure
"""

from typing import TYPE_CHECKING

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

INPUT_FILE: str = "./src/training/sensor-training-data.csv"
MODEL_FILE: str = "./src/training/model.joblib"


def train_model():
    """trains the ML on the input file"""
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

        print(" ### ")
        print(" training data :")
        for col in feature_cols:
            print(f"{col}: mean={df[col].mean():.2f}, std.s={df[col].std():.2f}")

        y_pred = clf.predict(X_train)
        scores = clf.decision_function(X_train)
        n_anomalies = np.sum(y_pred == -1)
        n_normals = np.sum(y_pred == 1)

        print("\n=== Model on training data ===")
        print(f"Normal points:  {n_normals}")
        print(f"Anomalies:      {n_anomalies}")
        print(f"Anomaly ratio:  {n_anomalies / len(X_train):.3f}")
        print(
            f"Score stats:    min={scores.min():.3f}, max={scores.max():.3f}, mean={scores.mean():.3f}"
        )

        joblib.dump(clf, MODEL_FILE)
        print("model saved")

    except FileNotFoundError:
        print(f"file not found: (inputfile) {INPUT_FILE}")
        print("remember to generate it first")


if __name__ == "__main__":
    train_model()
