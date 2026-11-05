
from pathlib import Path

import joblib
from micromlgen import port

BASE_DIR = Path(__file__).resolve().parent
MODEL_FILE = BASE_DIR / "synthetic_fault_model.joblib"
OUTPUT_FILE = BASE_DIR / "synthetic_fault_model.h"

saved = joblib.load(MODEL_FILE)
model = saved["model"]

# Karar ağacını C++ koduna dönüştür
cpp_code = port(model)

OUTPUT_FILE.write_text(cpp_code, encoding="utf-8")

print("C++ model dosyası oluşturuldu:", OUTPUT_FILE)
print("Sınıf sırası:", saved["classes"])
print("Özellik sırası:")
for i, name in enumerate(saved["features_per_axis"]):
    print(i, name)
