from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

BASE_DIR = Path(__file__).resolve().parent

print("1. Sentetik veri seti yükleniyor...")
df = pd.read_csv(BASE_DIR / "synthetic_adxl345_dataset.csv")

print("2. Özellikler çıkarılıyor...")
features_list = []
labels_list = []

for sample_id, group in df.groupby("sample_id"):
  label = group["label"].iloc[0]
  feat = []
  for col in ["x", "y", "z"]:
    vals = group[col].values
    feat.extend([
        np.mean(vals),
        np.std(vals),
        np.sqrt(np.mean(vals ** 2)),
        np.max(vals),
        np.min(vals),
        np.max(vals) - np.min(vals),  # Peak-to-Peak
    ])
  features_list.append(feat)
  labels_list.append(label)

X = np.array(features_list)
y = np.array(labels_list)

# Karar ağacını eğit (Derinliği küçük tutuyoruz ki ESP8266 zorlanmasın)
print("3. Karar ağacı modeli eğitiliyor...")
clf = DecisionTreeClassifier(max_depth=4, random_state=42)
clf.fit(X, y)

# 4. small_fault_model.h dosyasını otomatik oluştur
print("4. small_fault_model.h dosyası oluşturuluyor...")


# Sklearn ağacını C++ if-else yapısına dönüştüren basit bir export fonksiyonu
def tree_to_cpp(tree, feature_names):
  tree_ = tree.tree_

  def recurse(node, depth):
    indent = "    " * depth
    if tree_.feature[node] != -2:  # -2 means _tree.TREE_UNDEFINED
      name = feature_names[tree_.feature[node]]
      threshold = tree_.threshold[node]
      feat_idx = feature_names.index(name)
      res = (
          f"{indent}if (features[{feat_idx}] <= {threshold:.4f}) {{\n"
          + recurse(tree_.children_left[node], depth + 1)
          + f"{indent}}} else {{\n"
          + recurse(tree_.children_right[node], depth + 1)
          + f"{indent}}}\n"
      )
      return res
    else:
      class_idx = np.argmax(tree_.value[node][0])
      class_name = clf.classes_[class_idx]
      return f'{indent}return "{class_name}";\n'

  return recurse(0, 1)


feature_names = [
    "mean_x",
    "std_x",
    "rms_x",
    "max_x",
    "min_x",
    "p2p_x",
    "mean_y",
    "std_y",
    "rms_y",
    "max_y",
    "min_y",
    "p2p_y",
    "mean_z",
    "std_z",
    "rms_z",
    "max_z",
    "min_z",
    "p2p_z",
]

cpp_code = f"""// Otomatik üretilmiş Edge AI Model Dosyası
#ifndef SMALL_FAULT_MODEL_H
#define SMALL_FAULT_MODEL_H

#include <Arduino.h>

String predictFault(float features[]) {{
{tree_to_cpp(clf, feature_names)}
}}

#endif
"""

output_file = BASE_DIR / "small_fault_model.h"
output_file.write_text(cpp_code, encoding="utf-8")

print(
    "BAŞARILI! 'small_fault_model.h' dosyası hazır. Şimdi Arduino projenin"
    " içine atabilirsin."
)