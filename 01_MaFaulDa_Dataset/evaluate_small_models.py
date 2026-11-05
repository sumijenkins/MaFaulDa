
from pathlib import Path

import joblib
import pandas as pd

from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import accuracy_score, balanced_accuracy_score

BASE = Path(__file__).resolve().parent
data = pd.read_csv(BASE / "features.csv")

feature_cols = [f"feature_{i}" for i in range(18)]
X = data[feature_cols]
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

X_test = X.iloc[test_idx]
y_test = y.iloc[test_idx]

print("Derinlik | Düğüm | Accuracy | Balanced accuracy")

for depth in [4, 6, 8, 10, 12]:
    path = BASE / f"small_fault_model_depth_{depth}.joblib"
    model = joblib.load(path)
    predictions = model.predict(X_test)

    print(
        f"{depth:8} | "
        f"{model.tree_.node_count:5} | "
        f"{accuracy_score(y_test, predictions):.4f} | "
        f"{balanced_accuracy_score(y_test, predictions):.4f}"
    )
