
from pathlib import Path
import csv

DATASET_DIR = Path(
    r"C:\Users\smyys\Projects\MaFaulDa\MAFAULDA"
)

CLASSES = [
    "normal",
    "imbalance",
    "horizontal-misalignment",
    "vertical-misalignment",
]


def inspect_csv(file_path):
    """CSV dosyasının satır ve sütun yapısını kontrol eder."""
    row_count = 0
    column_counts = set()
    invalid_rows = 0

    with file_path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.reader(file)

        for row in reader:
            if not row:
                continue

            row_count += 1
            column_counts.add(len(row))

            try:
                for value in row:
                    float(value)
            except ValueError:
                invalid_rows += 1

    return row_count, column_counts, invalid_rows


def main():
    if not DATASET_DIR.exists():
        print(f"Veri seti bulunamadı: {DATASET_DIR}")
        return

    for class_name in CLASSES:
        class_dir = DATASET_DIR / class_name
        files = sorted(class_dir.rglob("*.csv"))

        print(f"\nSınıf: {class_name}")
        print(f"CSV dosyası sayısı: {len(files)}")

        if not files:
            print("UYARI: Bu sınıfta CSV dosyası bulunamadı.")
            continue

        sample_file = files[0]
        rows, columns, invalid_rows = inspect_csv(sample_file)

        print(f"Örnek dosya: {sample_file.name}")
        print(f"Satır sayısı: {rows}")
        print(f"Sütun sayıları: {sorted(columns)}")
        print(f"Sayısal olmayan satır sayısı: {invalid_rows}")

    print("\nKontrol tamamlandı.")


if __name__ == "__main__":
    main()
