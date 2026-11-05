
from pathlib import Path
import joblib

BASE_DIR = Path(__file__).resolve().parent
MODEL_FILE = BASE_DIR / "fault_model.joblib"

if not MODEL_FILE.exists():
    print("Model dosyası bulunamadı.")
    raise SystemExit

model_size = MODEL_FILE.stat().st_size

model = joblib.load(MODEL_FILE)
classifier = model.named_steps["randomforestclassifier"]

print("Model dosyası:", MODEL_FILE.resolve())
print(f"Model dosya boyutu: {model_size / 1024:.2f} KB")
print("Ağaç sayısı:", len(classifier.estimators_))
print("Sınıf sayısı:", len(classifier.classes_))
print("Sınıflar:", classifier.classes_)
print(
    "Toplam ağaç düğümü:",
    sum(tree.tree_.node_count for tree in classifier.estimators_)
)
