
from pathlib import Path
import numpy as np
import pandas as pd

DATASET_DIR = Path(
    r"C:\Users\smyys\Projects\MaFaulDa\MAFAULDA"
)

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "features.csv"

CLASSES = {
    "normal": 0,
    "imbalance": 1,
    "horizontal-misalignment": 2,
    "vertical-misalignment": 3,
}

WINDOW_SIZE = 5000
STEP_SIZE = 5000


def extract_features(signal):
    """Üç eksenden temel istatistiksel özellikleri çıkarır."""
    features = []

    for axis in range(signal.shape[1]):
        x = signal[:, axis].astype(np.float64)

        features.extend([
            np.mean(x),
            np.std(x),
            np.sqrt(np.mean(x ** 2)),
            np.min(x),
            np.max(x),
            np.max(x) - np.min(x),
        ])

    return features


def main():
    rows = []

    for class_name, label in CLASSES.items():
        files = sorted(
            (DATASET_DIR / class_name).rglob("*.csv")
        )

        print(f"\n{class_name}: {len(files)} dosya")

        for file_index, file_path in enumerate(files, start=1):
            # Yalnızca 2, 3 ve 4. sütunları okuyoruz.
            data = pd.read_csv(
                file_path,
                header=None,
                usecols=[1, 2, 3]
            ).to_numpy(dtype=np.float32)

            for start in range(
                0, len(data) - WINDOW_SIZE + 1, STEP_SIZE
            ):
                window = data[start:start + WINDOW_SIZE]

                features = extract_features(window)

                rows.append({
                    **{
                        f"feature_{i}": value
                        for i, value in enumerate(features)
                    },
                    "label": label,
                    "class_name": class_name,
                    "file_name": file_path.name,
                    "file_path": str(file_path),
                })

            if file_index % 10 == 0 or file_index == len(files):
                print(
                    f"  İşlenen dosya: {file_index}/{len(files)}"
                )

    if not rows:
        print("Hiç özellik çıkarılamadı.")
        return

    result = pd.DataFrame(rows)
    result.to_csv(OUTPUT_FILE, index=False)

    print("\nÖzellik çıkarma tamamlandı.")
    print("Toplam pencere:", len(result))
    print("Çıktı dosyası:", OUTPUT_FILE.resolve())
    print("\nSınıf başına pencere sayısı:")
    print(result["class_name"].value_counts())


if __name__ == "__main__":
    main()
