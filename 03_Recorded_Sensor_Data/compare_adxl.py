
from pathlib import Path
import re
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "adxl_tracks"

FILES = {
    "Sabit": DATA_DIR / "adxl345_static.txt",
    "Hareketli": DATA_DIR / "adxl345_moving.txt",
}

# Arduino Serial Monitor zaman damgalarını da destekler.
pattern = re.compile(
    r"(\d+),\s*(-?\d+(?:\.\d+)?),\s*"
    r"(-?\d+(?:\.\d+)?),\s*(-?\d+(?:\.\d+)?)\s*$"
)

def load_data(path):
    rows = []

    with path.open("r", encoding="utf-8-sig", errors="ignore") as f:
        for line in f:
            match = pattern.search(line.strip())

            if match:
                rows.append([float(value) for value in match.groups()])

    if not rows:
        raise ValueError(
            f"Veri bulunamadi: {path}\n"
            "Dosyada time_ms,x,y,z ve sayisal olcum satirlari olmali."
        )

    return pd.DataFrame(rows, columns=["time_ms", "x", "y", "z"])


for label, path in FILES.items():
    if not path.exists():
        print(f"\nDOSYA BULUNAMADI: {path}")
        continue

    df = load_data(path)
    axes = ["x", "y", "z"]

    # Yerçekimi ve sabit eksen ofsetini yaklaşık ayır.
    dynamic = df[axes] - df[axes].mean()

    print(f"\n{'=' * 40}")
    print(f"Durum: {label}")
    print(f"Dosya: {path.name}")
    print(f"Okunan örnek sayisi: {len(df)}")

    if len(df) > 1:
        elapsed = (df["time_ms"].max() - df["time_ms"].min()) / 1000
        print(f"Kayit suresi: {elapsed:.2f} saniye")
        if elapsed > 0:
            print(f"Ortalama kayit hizi: {len(df) / elapsed:.1f} ornek/s")

    for axis in axes:
        print(f"\n{axis.upper()} ekseni:")
        print(f"  Ortalama ivme: {df[axis].mean():.3f} m/s^2")
        print(f"  Standart sapma: {df[axis].std():.4f} m/s^2")
        print(f"  Min / Max: {df[axis].min():.3f} / {df[axis].max():.3f}")
        print(
            "  Ofseti cikarilmis RMS: "
            f"{np.sqrt(np.mean(dynamic[axis] ** 2)):.4f} m/s^2"
        )

print("\nAnaliz tamamlandi.")
