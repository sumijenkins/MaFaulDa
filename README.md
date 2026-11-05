# ESP8266 Edge AI - Makine Ariza Tespiti

ADXL345 ivmeolcerinden alinan X, Y ve Z ekseni verilerini kucuk karar agaci modelleriyle siniflandirarak makine arizalarini ESP8266 uzerinde tespit eden bir Edge AI projesi. ESP8266 olcumleri ve tahminleri HTTP JSON API'si uzerinden sunar; Python/Flask dashboard'u bu verileri goruntuler.

## Tespit edilen siniflar

- Normal
- Dengesizlik (imbalance)
- Yatay hizasizlik (horizontal misalignment)
- Dikey hizasizlik (vertical misalignment)

## Donanim ve baglantilar

- ESP8266 gelistirme karti
- ADXL345 ivmeolcer (I2C: SDA -> D2, SCL -> D1)
- Istege bagli BMP180 sicaklik/basinc sensoru (ayni I2C hatti)

Firmware, `ESP8266_FaultDetection/Esp8266_edgeai/Esp8266_edgeai.ino` dosyasindadir. Arduino IDE'de ESP8266 kart destegini ve Adafruit ADXL345, Adafruit Unified Sensor ve Adafruit BMP085 kutuphanelerini yukleyin; ardindan bu sketch'i karta yukleyin. BMP180 bagli degilse ivmeolcer tabanli tahmin calismaya devam eder.

Kart `Machine-Monitor` adli Wi-Fi erisim noktasi olusturur ve olcumleri `http://192.168.4.1/data` adresinde sunar. Kaynak koddaki varsayilan Wi-Fi parolasini gercek kullanimdan once degistirin; parola firmware seri cikisinda da yazdirilir.

## Python dashboard

Python 3 ile dashboard bagimliliklarini kurun:

```powershell
cd ESP8266_FaultDetection/python-dashboard
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Bilgisayari ESP8266'nin `Machine-Monitor` agina bagladiktan sonra `http://127.0.0.1:5000` adresini acin. Dashboard, ESP8266 API'sini `http://192.168.4.1/data` adresinden okur. Farkli bir ag veya adres kullaniyorsaniz `app.py` icindeki `ESP_URL` degerini guncelleyin.

## Veri ve model egitimi

- `01_MaFaulDa_Dataset/`: MaFaulDa veri seti icin ozellik cikarma, model egitimi, karsilastirma ve disari aktarma betikleri. Ham MaFaulDa veri seti depoya dahil degildir. `02_extract_features.py` icindeki `DATASET_DIR` degerini kendi veri setinizin konumuna gore ayarlayin; betik `features.csv` olusturur.
- `02_Synthetic_Data/`: Sentetik ADXL345 verisi uretme ve karar agaci egitme betikleri; uretilen veri ve model dosyalari da klasordedir.
- `03_Recorded_Sensor_Data/`: Sensor verisini seri porttan kaydetme, kayitlari karsilastirma ve kayitli verilerden model egitme betikleri. Seri portu kullanmadan once `record_data.py` icindeki `PORT` degerini ayarlayin.
- `ESP8266_FaultDetection/`: ESP8266 firmware'i, model baslik dosyasi ve Flask dashboard.
- `FaultDetection/` ve `SyntheticFaultDetection/`: Diger firmware/model varyantlari.

Model egitimi icin ilgili betigin klasorune gecin ve o betigin Python bagimliliklarini kurun. MaFaulDa veri akisi ham veri seti gerektirir; sentetik veri akisi ise `02_Synthetic_Data/generate_dataset.py` ve ardindan `08_train_synthetic_model.py` ile calistirilabilir.

## API ornegi

`GET /data` yaniti ivmeolcer eksenlerini, sicaklik/basinc durumunu ve model tahminini JSON olarak icerir:

```json
{
  "x": 0.12,
  "y": 0.34,
  "z": 9.81,
  "temperature": 24.5,
  "pressure": 100812,
  "bmpReady": true,
  "prediction": 0,
  "fault": "Normal"
}
```

## Guvenlik ve kullanim

Varsayilan erisim noktasi parolasini paylasmadan veya cihazi kullanmadan once degistirin. Bu proje egitim ve prototipleme amaclidir; guvenlik-kritik makine durdurma veya koruma sistemlerinin yerine kullanilmamalidir.