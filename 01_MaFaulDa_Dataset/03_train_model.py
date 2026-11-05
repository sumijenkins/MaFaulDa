
from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    balanced_accuracy_score,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "features.csv"
MODEL_FILE = BASE_DIR / "fault_model.joblib"

FEATURE_COLUMNS = [
    f"feature_{i}" for i in range(18)
]

CLASS_NAMES = [
    "normal",
    "imbalance",
    "horizontal-misalignment",
    "vertical-misalignment",
]


def main():
    if not DATA_FILE.exists():
        print("features.csv bulunamadı.")
        return

    data = pd.read_csv(DATA_FILE)

    X = data[FEATURE_COLUMNS]
    y = data["label"]
    groups = data["file_path"]

    # Aynı CSV dosyasının pencereleri iki tarafa da dağılmasın.
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

    print("Eğitim penceresi:", len(X_train))
    print("Test penceresi:", len(X_test))
    print(
        "Eğitim dosyası:",
        groups.iloc[train_idx].nunique()
    )
    print(
        "Test dosyası:",
        groups.iloc[test_idx].nunique()
    )

    model = make_pipeline(
        SimpleImputer(strategy="median"),
        RandomForestClassifier(
            n_estimators=150,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
    )

    print("\nModel eğitiliyor...")
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print("\nAccuracy:", round(
        accuracy_score(y_test, predictions), 4
    ))
    print("Balanced accuracy:", round(
        balanced_accuracy_score(y_test, predictions), 4
    ))

    print("\nSınıflandırma raporu:")
    print(
        classification_report(
            y_test,
            predictions,
            labels=[0, 1, 2, 3],
            target_names=CLASS_NAMES,
            zero_division=0,
        )
    )

    print("Confusion matrix:")
    print(confusion_matrix(
        y_test,
        predictions,
        labels=[0, 1, 2, 3],
    ))

    joblib.dump(model, MODEL_FILE)
    print("\nModel kaydedildi:", MODEL_FILE.resolve())


if __name__ == "__main__":
    main()
