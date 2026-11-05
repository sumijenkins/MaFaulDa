import os
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import sklearn.tree._tree as _tree  # TREE_UNDEFINED için doğru import yolu

# 1. Dosya Yolları ve Sınıf Etiketleri
DATA_DIR = r"C:\Users\smyys\Projects\ESP8266-EdgeAI\03_Recorded_Sensor_Data\adxl_tracks"
FILES = {
    "Normal": os.path.join(DATA_DIR, "normal_001.csv"),
    "Imbalance": os.path.join(DATA_DIR, "imbalance_001.csv"),
    "Horizontal_Misalignment": os.path.join(DATA_DIR, "horizontal_001.csv"),
    "Vertical_Misalignment": os.path.join(DATA_DIR, "vertical_001.csv"),
}

WINDOW_SIZE = 50  # Her bir örnekleme penceresindeki satır sayısı
STEP_SIZE = 25  # Kaydırma adımı (overlap)


def extract_features(window_df):
  """X, Y, Z eksenleri için 18 temel istatistiksel özellik çıkarır"""
  features = []
  for col in ["X", "Y", "Z"]:
    data = window_df[col].values
    mean_val = np.mean(data)
    std_val = np.std(data)
    rms_val = np.sqrt(np.mean(data**2))
    p2p_val = np.ptp(data)  # Peak-to-Peak
    min_val = np.min(data)
    max_val = np.max(data)

    features.extend([mean_val, std_val, rms_val, p2p_val, min_val, max_val])
  return features


# 2. Verileri Okuma ve Pencereleme
X_list = []
y_list = []

class_mapping = {
    "Normal": 0,
    "Imbalance": 1,
    "Horizontal_Misalignment": 2,
    "Vertical_Misalignment": 3,
}

print("Veriler işleniyor ve özellikler çıkarılıyor...")
for label_name, file_path in FILES.items():
  if not os.path.exists(file_path):
    print(f"HATA: {file_path} bulunamadı!")
    continue

  df = pd.read_csv(file_path)
  df.columns = [c.strip() for c in df.columns]

  label_id = class_mapping[label_name]

  for i in range(0, len(df) - WINDOW_SIZE, STEP_SIZE):
    window = df.iloc[i : i + WINDOW_SIZE]
    feats = extract_features(window)
    X_list.append(feats)
    y_list.append(label_id)

X = np.array(X_list)
y = np.array(y_list)

print(
    f"Toplam {len(X)} adet pencere (örnek) başarıyla oluşturuldu. Model"
    " eğitiliyor..."
)

# 3. Model Eğitimi
clf = DecisionTreeClassifier(max_depth=5, random_state=42)
clf.fit(X, y)
print("Model eğitimi tamamlandı!")


# 4. Modeli ESP8266 için C++ Header Dosyasına Dönüştürme
def tree_to_c(tree, feature_names):
  tree_ = tree.tree_
  feature_name = [
      feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined"
      for i in tree_.feature
  ]

  code = []
  code.append("#ifndef SMALL_FAULT_MODEL_H")
  code.append("#define SMALL_FAULT_MODEL_H\n")
  code.append(
      "// Otomatik oluşturulmuş Edge AI Karar Ağacı Header Dosyası"
  )
  code.append("inline int predictFault(float features[]) {")

  def recurse(node, depth):
    indent = "    " * depth
    if tree_.feature[node] != _tree.TREE_UNDEFINED:
      name = feature_name[node]
      feat_idx = int(name.replace("f", ""))
      threshold = tree_.threshold[node]
      code.append(
          f"{indent}if (features[{feat_idx}] <= {threshold:.6f}) {{"
      )
      recurse(tree_.children_left[node], depth + 1)
      code.append(f"{indent}}} else {{")
      recurse(tree_.children_right[node], depth + 1)
      code.append(f"{indent}}}")
    else:
      class_counts = tree_.value[node][0]
      predicted_class = int(np.argmax(class_counts))
      code.append(f"{indent}return {predicted_class};")

  recurse(0, 1)
  code.append("}\n")
  code.append("#endif")
  return "\n".join(code)


feature_names = [f"f{i}" for i in range(18)]
c_code = tree_to_c(clf, feature_names)

# Header dosyasını doğrudan ana proje klasörüne kaydedelim ki ESP kodun rahat bulsun
output_header = os.path.join(
    os.path.dirname(DATA_DIR), "small_fault_model.h"
)
with open(output_header, "w", encoding="utf-8") as f:
  f.write(c_code)

print(
    f"Başarılı! ESP8266 için '{output_header}' dosyası otomatik olarak"
    " oluşturuldu."
)