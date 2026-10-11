"""Build the public NASA C-MAPSS portfolio data.

The raw data are downloaded from NASA's Open Data Portal and are not
committed to the repository. Run this script from its own directory.
"""

from __future__ import annotations

import json
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


DATA_URL = "https://data.nasa.gov/docs/legacy/CMAPSSData.zip"
ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
ZIP_PATH = RAW / "CMAPSSData.zip"
NAMES = ["engine", "cycle", "setting_1", "setting_2", "setting_3"] + [
    f"sensor_{index}" for index in range(1, 22)
]


def ensure_data() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    if not ZIP_PATH.exists():
        urllib.request.urlretrieve(DATA_URL, ZIP_PATH)
    required = ["train_FD001.txt", "test_FD001.txt", "RUL_FD001.txt"]
    if not all((RAW / name).exists() for name in required):
        with zipfile.ZipFile(ZIP_PATH) as archive:
            for name in required:
                archive.extract(name, RAW)


def read_cycles(filename: str) -> pd.DataFrame:
    return pd.read_csv(RAW / filename, sep=r"\s+", header=None, names=NAMES)


def add_features(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    sensors = [name for name in NAMES if name.startswith("sensor_")]
    grouped = result.groupby("engine", sort=False)
    for sensor in sensors:
        result[f"{sensor}_delta"] = grouped[sensor].diff().fillna(0)
        result[f"{sensor}_mean5"] = (
            grouped[sensor].rolling(5, min_periods=1).mean().reset_index(level=0, drop=True)
        )
    return result


def main() -> None:
    ensure_data()
    train = read_cycles("train_FD001.txt")
    test = read_cycles("test_FD001.txt")
    truth = pd.read_csv(RAW / "RUL_FD001.txt", sep=r"\s+", header=None, names=["rul"])
    truth["engine"] = np.arange(1, len(truth) + 1)

    max_cycle = train.groupby("engine")["cycle"].transform("max")
    train["rul"] = (max_cycle - train["cycle"]).clip(upper=125)

    raw_sensors = [name for name in NAMES if name.startswith("sensor_")]
    useful_sensors = [name for name in raw_sensors if train[name].std() > 1e-6]
    correlations = train[useful_sensors].corrwith(train["rul"], method="spearman").abs()
    selected_sensors = correlations.nlargest(12).index.tolist()

    train_f = add_features(train)
    test_f = add_features(test)
    features = ["cycle", "setting_1", "setting_2", "setting_3"]
    for sensor in selected_sensors:
        features.extend([sensor, f"{sensor}_delta", f"{sensor}_mean5"])

    development = train_f[train_f["engine"] <= 80]
    validation = train_f[train_f["engine"] > 80]
    validation_model = RandomForestRegressor(
        n_estimators=220,
        max_depth=16,
        min_samples_leaf=3,
        max_features=0.75,
        n_jobs=-1,
        random_state=2026,
    )
    validation_model.fit(development[features], development["rul"])
    validation_prediction = validation_model.predict(validation[features])

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=16,
        min_samples_leaf=3,
        max_features=0.75,
        n_jobs=-1,
        random_state=2026,
    )
    model.fit(train_f[features], train_f["rul"])

    last_rows = test_f.loc[test_f.groupby("engine")["cycle"].idxmax()].copy()
    last_rows["actual_rul"] = truth.set_index("engine").loc[last_rows["engine"], "rul"].to_numpy()
    last_rows["predicted_rul"] = np.clip(model.predict(last_rows[features]), 0, 125)
    last_rows["absolute_error"] = (last_rows["predicted_rul"] - last_rows["actual_rul"]).abs()

    feature_importance = pd.Series(model.feature_importances_, index=features)
    grouped_importance = {}
    for feature, value in feature_importance.items():
        root = feature.split("_delta")[0].split("_mean5")[0]
        grouped_importance[root] = grouped_importance.get(root, 0.0) + float(value)
    importance = sorted(grouped_importance.items(), key=lambda item: item[1], reverse=True)[:8]

    trajectory_sensors = [name for name, _ in importance if name.startswith("sensor_")][:3]
    if len(trajectory_sensors) < 3:
        trajectory_sensors = selected_sensors[:3]
    means = train[trajectory_sensors].mean()
    scales = train[trajectory_sensors].std().replace(0, 1)
    trajectories = {}
    for engine, group in test.groupby("engine", sort=True):
        stride = max(1, int(np.ceil(len(group) / 70)))
        sampled = group.iloc[::stride].copy()
        if sampled.index[-1] != group.index[-1]:
            sampled = pd.concat([sampled, group.iloc[[-1]]])
        normalized = (sampled[trajectory_sensors] - means) / scales
        trajectories[str(int(engine))] = {
            "cycle": sampled["cycle"].astype(int).tolist(),
            "series": {
                sensor.replace("sensor_", "Sensor "): normalized[sensor].round(3).tolist()
                for sensor in trajectory_sensors
            },
        }

    rmse = float(mean_squared_error(last_rows["actual_rul"], last_rows["predicted_rul"]) ** 0.5)
    output = {
        "source": {
            "name": "NASA C-MAPSS Jet Engine Simulated Data",
            "url": "https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data",
            "subset": "FD001",
        },
        "metrics": {
            "training_rows": int(len(train)),
            "training_engines": int(train["engine"].nunique()),
            "test_engines": int(test["engine"].nunique()),
            "validation_rmse": round(float(mean_squared_error(validation["rul"], validation_prediction) ** 0.5), 2),
            "validation_mae": round(float(mean_absolute_error(validation["rul"], validation_prediction)), 2),
            "validation_r2": round(float(r2_score(validation["rul"], validation_prediction)), 3),
            "official_test_rmse": round(rmse, 2),
            "official_test_mae": round(float(mean_absolute_error(last_rows["actual_rul"], last_rows["predicted_rul"])), 2),
            "within_20_cycles": round(float((last_rows["absolute_error"] <= 20).mean()), 3),
        },
        "predictions": [
            {
                "engine": int(row.engine),
                "actual": round(float(row.actual_rul), 1),
                "predicted": round(float(row.predicted_rul), 1),
                "error": round(float(row.absolute_error), 1),
            }
            for row in last_rows.itertuples()
        ],
        "importance": [
            {"feature": name.replace("_", " ").title(), "value": round(value, 4)}
            for name, value in importance
        ],
        "trajectory_sensors": [sensor.replace("sensor_", "Sensor ") for sensor in trajectory_sensors],
        "trajectories": trajectories,
    }
    (ROOT / "data.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output["metrics"], indent=2))


if __name__ == "__main__":
    main()
