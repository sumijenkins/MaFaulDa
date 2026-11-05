
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
FS = 100
DURATION = 5
N_SAMPLES_PER_CLASS = 100
N = FS * DURATION

CLASSES = ["Normal", "Dengesizlik", "Yatay_Hizasizlik", "Dikey_Hizasizlik"]
BASE = np.array([0.57, 1.45, 9.23])
NOISE = 0.04

rng = np.random.default_rng(42)
all_data = []

for label in CLASSES:
    for sample_id in range(N_SAMPLES_PER_CLASS):
        t = np.arange(N) / FS
        x = BASE[0] + rng.normal(0, NOISE, N)
        y = BASE[1] + rng.normal(0, NOISE, N)
        z = BASE[2] + rng.normal(0, NOISE, N)

        phase = rng.uniform(0, 2 * np.pi)
        freq = rng.uniform(8, 15)

        if label == "Dengesizlik":
            signal = rng.uniform(0.3, 0.6) * np.sin(2*np.pi*freq*t + phase)
            x += signal
            y += 0.7 * signal

        elif label == "Yatay_Hizasizlik":
            x += 0.8 * np.sin(2*np.pi*freq*t + phase)
            y += 0.6 * np.sin(2*np.pi*(freq+3)*t + phase)

        elif label == "Dikey_Hizasizlik":
            z += 1.0 * np.sin(2*np.pi*freq*t + phase)

        recording_id = f"{label}_{sample_id + 1:03d}"

        all_data.append(pd.DataFrame({
            "sample_id": recording_id,
            "time_ms": t * 1000,
            "x": x,
            "y": y,
            "z": z,
            "label": label
        }))

df = pd.concat(all_data, ignore_index=True)
output_file = BASE_DIR / "synthetic_adxl345_dataset.csv"
df.to_csv(output_file, index=False)

print("Veri seti oluşturuldu:", output_file, df.shape)
print(df.groupby("label")["sample_id"].nunique())
