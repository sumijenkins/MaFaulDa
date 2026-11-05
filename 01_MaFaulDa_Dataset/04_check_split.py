
from pathlib import Path

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

BASE_DIR = Path(__file__).resolve().parent
data = pd.read_csv(BASE_DIR / "features.csv")

splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.25,
    random_state=42,
)

train_idx, test_idx = next(
    splitter.split(
        data,
        data["label"],
        groups=data["file_path"],
    )
)

train = data.iloc[train_idx]
test = data.iloc[test_idx]

print("\nEĞİTİM DOSYALARININ SINIF DAĞILIMI")
print(
    train.groupby("class_name")["file_path"]
    .nunique()
)

print("\nTEST DOSYALARININ SINIF DAĞILIMI")
print(
    test.groupby("class_name")["file_path"]
    .nunique()
)

print("\nTEST PENCERELERİNİN SINIF DAĞILIMI")
print(test["class_name"].value_counts())

print("\nEğitim ve test dosyaları ortak mı?")
print(
    set(train["file_path"]).intersection(
        set(test["file_path"])
    )
)
