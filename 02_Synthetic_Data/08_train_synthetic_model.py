
from pathlib import Path

import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "synthetic_adxl345_dataset.csv"
MODEL_FILE = BASE_DIR / "synthetic_fault_model.joblib"

df = pd.read_csv(CSV_FILE)

FEATURE_COLUMNS = ["x", "y", "z"]
LABEL_COLUMN = "label"

def extract_features(window):
    features = []

    for axis in FEATURE_COLUMNS:
        values = window[axis].to_numpy(dtype=float)

        features.extend([
            np.mean(values),
            np.std(values),
            np.sqrt(np.mean(values ** 2)),
            np.min(values),
            np.max(values),
            np.max(values) - np.min(values)
        ])

    return features

X = []
y = []

for sample_id, window in df.groupby("sample_id", sort=False):
    X.append(extract_features(window))
    y.append(window[LABEL_COLUMN].iloc[0])

X = np.asarray(X, dtype=float)
y = np.asarray(y)

encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.25,
    random_state=42,
    stratify=y_encoded
)

model = DecisionTreeClassifier(
    max_depth=5,
    random_state=42
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)

print("Doğruluk:", round(accuracy_score(y_test, predictions), 3))
print("\nSınıflandırma raporu:")
print(
    classification_report(
        y_test,
        predictions,
        labels=np.arange(len(encoder.classes_)),
        target_names=encoder.classes_,
        zero_division=0
    )
)

joblib.dump(
    {
        "model": model,
        "classes": encoder.classes_.tolist(),
        "features_per_axis": [
            "mean", "std", "rms", "min", "max", "range"
        ],
        "axes": FEATURE_COLUMNS
    },
    MODEL_FILE
)

print(f"\nModel kaydedildi: {MODEL_FILE}")
print("Ağaç düğüm sayısı:", model.tree_.node_count)
print("Ağaç derinliği:", model.get_depth())
