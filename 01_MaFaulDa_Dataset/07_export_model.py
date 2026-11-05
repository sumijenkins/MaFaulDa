
from pathlib import Path

import joblib
from micromlgen import port

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "small_fault_model_depth_12.joblib"
OUTPUT_PATH = BASE_DIR / "fault_model.h"

if not MODEL_PATH.exists():
    print("Model bulunamadı:", MODEL_PATH.resolve())
    raise SystemExit(1)

model = joblib.load(MODEL_PATH)

# Karar ağacını C++ koduna dönüştür.
c_code = port(model)

OUTPUT_PATH.write_text(c_code, encoding="utf-8")

print("Dönüştürme tamamlandı.")
print("Çıktı:", OUTPUT_PATH.resolve())
print(f"Dosya boyutu: {OUTPUT_PATH.stat().st_size / 1024:.2f} KB")
print("\nDosyanın ilk 15 satırı:")

for line in c_code.splitlines()[:15]:
    print(line)
