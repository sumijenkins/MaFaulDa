
from pathlib import Path

import joblib
import pandas as pd

from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "features.csv"
MODEL_FILE = BASE_DIR / "small_fault_model.joblib"

FEATURE_COLUMNS = [f"feature_{i}" for i in range(18)]

CLASS_NAMES = [
    "normal",
    "imbalance",
    "horizontal-misalignment",
    "vertical-misalignment",
]


def main():
    data = pd.read_csv(DATA_FILE)

    X = data[FEATURE_COLUMNS]
    y = data["label"]
    groups = data["file_path"]

    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.25,
        random_state=42,
    )

    train_idx, test_idx = next(
        splitter.split(X, y, groups=groups)
    )

    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    for depth in [4, 6, 8, 10, 12]:
        model = DecisionTreeClassifier(
            max_depth=depth,
            class_weight="balanced",
            random_state=42,
        )

        model.fit(X_train, y_train)
        predictions = model.predict(X_test)

        print(f"\n--- Maksimum derinlik: {depth} ---")
        print("Düğüm sayısı:", model.tree_.node_count)
        print(
            "Accuracy:",
            round(accuracy_score(y_test, predictions), 4),
        )
        print(
            "Balanced accuracy:",
            round(
                balanced_accuracy_score(y_test, predictions),
                4,
            ),
        )

        print(
            classification_report(
                y_test,
                predictions,
                labels=[0, 1, 2, 3],
                target_names=CLASS_NAMES,
                zero_division=0,
            ),
        )

        output = BASE_DIR / f"small_fault_model_depth_{depth}.joblib"
        joblib.dump(model, output)
        print(
            f"Model boyutu: {output.stat().st_size / 1024:.2f} KB"
        )


if __name__ == "__main__":
    main()
