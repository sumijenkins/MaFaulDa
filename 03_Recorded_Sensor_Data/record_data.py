import csv
import time
import serial
from pathlib import Path

PORT = "COM10"
BAUD = 115200
DATA_DIR = Path(__file__).resolve().parent / "adxl_tracks"
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("Seri port açılıyor...")
try:
  # Portu doğrudan açıyoruz
  ser = serial.Serial(PORT, BAUD, timeout=1)

  # Port açıldıktan HEMEN SONRA DTR ve RTS'yi kapatıyoruz (Kritik nokta!)
  ser.dtr = False
  ser.rts = False

except Exception as e:
  print(f"HATA: Port açılamadı! Detay: {e}")
  exit()

print("Bağlantı kuruldu. ESP8266 verileri bekleniyor...")
time.sleep(2)  # Kısa bir bekleme

csv_filename = DATA_DIR / "vertical_001.csv"
print(f"Veriler '{csv_filename}' dosyasına kaydedilmeye başlandı...\n")

veri_sayisi = 0

with open(
    csv_filename, mode="w", newline="", encoding="utf-8", buffering=1
) as f:
  writer = csv.writer(f)
  # CSV Başlıkları
  writer.writerow(["Time_ms", "X", "Y", "Z"])

  start_time = time.time()

  # 25 saniye boyunca dinle
  while time.time() - start_time < 25:
    if ser.in_waiting > 0:
      raw_line = ser.readline()
      try:
        line = raw_line.decode("utf-8", errors="ignore").strip()
      except:
        continue

      if not line:
        continue

      # Ekrana okunan satırı basalım ki akışı görebilelim
      print("Okunan:", line)

      if line == "BEGIN" or line == "END":
        continue

      parts = line.split(",")
      if len(parts) >= 4:
        try:
          t_ms = float(parts[0])
          x = float(parts[1])
          y = float(parts[2])
          z = float(parts[3])

          writer.writerow([t_ms, x, y, z])
          f.flush()
          veri_sayisi += 1
        except ValueError:
          pass

ser.close()
print("\n----------------------------------------")
print(
    f"İşlem tamam! Toplam {veri_sayisi} satır veri '{csv_filename}' dosyasına"
    " kaydedildi."
)