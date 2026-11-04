# Home Assistant PC REST API

[![English](https://img.shields.io/badge/Language-English-blue)](#-english)
[![Türkçe](https://img.shields.io/badge/Dil-Türkçe-red)](#-türkçe)

---

## 🇬🇧 English

A simple FastAPI service that runs on your computer so Home Assistant can control power actions and read local sensor data. It works on **Windows**, **Linux**, and **macOS**, is protected with an API key, and can advertise itself on the LAN via **mDNS** as `ha-pc.local`.

### 🛠 Technologies Used
- **Python** (Programming Language)
- **FastAPI** (REST API Framework)
- **Uvicorn** (ASGI Server)
- **psutil** (System / Sensor Metrics)
- **Zeroconf** (mDNS / Bonjour Discovery)
- **python-dotenv / pydantic-settings** (Configuration)

### 📋 Prerequisites
To run this project, you need:
- **Python 3.10+**
- A local network connection to your Home Assistant instance

Install dependencies inside a virtual environment:
```bash
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set at least:
```env
API_KEY=your-long-random-secret
HOST=0.0.0.0
PORT=8765
MDNS_ENABLED=true
MDNS_NAME=ha-pc
```

### 🚀 How to Run
```bash
python -m app.main
```

The API listens on `http://0.0.0.0:8765` by default.  
Swagger docs: `http://<pc-ip>:8765/docs`  
mDNS URL: `http://ha-pc.local:8765`

All endpoints except `/health` require the `X-Api-Key` header.

#### Main Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check (+ platform / mDNS info) |
| POST | `/power/shutdown` | Shut down |
| POST | `/power/restart` | Restart |
| POST | `/power/sleep` | Sleep / suspend |
| POST | `/power/hibernate` | Hibernate |
| POST | `/power/lock` | Lock session |
| POST | `/power/cancel` | Cancel pending shutdown/restart |
| GET | `/sensors` | All sensors |
| GET | `/sensors/cpu` | CPU |
| GET | `/sensors/memory` | Memory |
| GET | `/sensors/disks` | Disks |
| GET | `/sensors/network` | Network |
| GET | `/sensors/temperatures` | Temperatures |
| GET | `/sensors/battery` | Battery |
| GET | `/sensors/system` | Hostname / uptime |

Example request:
```bash
curl.exe -H "X-Api-Key: your-long-random-secret" http://ha-pc.local:8765/sensors
```

After changing `.env`, restart the app so the new values are loaded.

#### Home Assistant Example
```yaml
rest:
  - resource: http://ha-pc.local:8765/sensors
    headers:
      X-Api-Key: your-long-random-secret
    scan_interval: 30
    sensor:
      - name: PC CPU
        value_template: "{{ value_json.cpu.percent }}"
        unit_of_measurement: "%"
      - name: PC RAM
        value_template: "{{ value_json.memory.percent }}"
        unit_of_measurement: "%"

rest_command:
  pc_shutdown:
    url: "http://ha-pc.local:8765/power/shutdown"
    method: POST
    headers:
      X-Api-Key: "your-long-random-secret"
      Content-Type: "application/json"
    payload: '{"delay_seconds": 0}'
```

`rest_command` actions appear as **services** (`rest_command.pc_shutdown`), not as sensor entities. If `.local` does not resolve from Home Assistant, use the PC LAN IP instead.

*Note: Allow inbound TCP `8765` in your firewall. Keep the API on your local network and use a strong `API_KEY`.*

---

## 🇹🇷 Türkçe

Bilgisayarında çalışan basit bir FastAPI servisi. Home Assistant üzerinden güç komutlarını (kapatma, yeniden başlatma, uyku, kilitleme vb.) gönderebilir ve CPU/RAM/disk gibi yerel sensör verilerini okuyabilir. **Windows**, **Linux** ve **macOS** destekler; API key ile korunur ve LAN üzerinde **mDNS** ile `ha-pc.local` olarak duyurulabilir.

### 🛠 Kullanılan Teknolojiler
- **Python** (Programlama Dili)
- **FastAPI** (REST API Çatısı)
- **Uvicorn** (ASGI Sunucu)
- **psutil** (Sistem / Sensör Metrikleri)
- **Zeroconf** (mDNS / Bonjour Keşif)
- **python-dotenv / pydantic-settings** (Yapılandırma)

### 📋 Gereksinimler
Projeyi çalıştırmak için aşağıdakilere ihtiyacınız vardır:
- **Python 3.10+**
- Home Assistant ile aynı yerel ağ bağlantısı

Sanal ortam kurup bağımlılıkları yükleyin:
```bash
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

`.env` dosyasını düzenleyip en azından şunları ayarlayın:
```env
API_KEY=your-long-random-secret
HOST=0.0.0.0
PORT=8765
MDNS_ENABLED=true
MDNS_NAME=ha-pc
```

### 🚀 Nasıl Çalıştırılır?
```bash
python -m app.main
```

API varsayılan olarak `http://0.0.0.0:8765` adresinde dinler.  
Swagger dokümantasyonu: `http://<pc-ip>:8765/docs`  
mDNS adresi: `http://ha-pc.local:8765`

`/health` dışındaki tüm endpointler `X-Api-Key` header’ı ister.

#### Ana Endpointler
| Method | Path | Açıklama |
|--------|------|----------|
| GET | `/health` | Sağlık kontrolü (+ platform / mDNS bilgisi) |
| POST | `/power/shutdown` | Bilgisayarı kapat |
| POST | `/power/restart` | Yeniden başlat |
| POST | `/power/sleep` | Uyku / suspend |
| POST | `/power/hibernate` | Hazırda beklet |
| POST | `/power/lock` | Oturumu kilitle |
| POST | `/power/cancel` | Bekleyen kapatma/yeniden başlatmayı iptal et |
| GET | `/sensors` | Tüm sensörler |
| GET | `/sensors/cpu` | CPU |
| GET | `/sensors/memory` | Bellek |
| GET | `/sensors/disks` | Diskler |
| GET | `/sensors/network` | Ağ |
| GET | `/sensors/temperatures` | Sıcaklıklar |
| GET | `/sensors/battery` | Batarya |
| GET | `/sensors/system` | Hostname / uptime |

Örnek istek:
```bash
curl.exe -H "X-Api-Key: your-long-random-secret" http://ha-pc.local:8765/sensors
```

`.env` değiştirdikten sonra uygulamayı yeniden başlatın; aksi halde eski değerler bellekte kalır.

#### Home Assistant Örneği
```yaml
rest:
  - resource: http://ha-pc.local:8765/sensors
    headers:
      X-Api-Key: your-long-random-secret
    scan_interval: 30
    sensor:
      - name: PC CPU
        value_template: "{{ value_json.cpu.percent }}"
        unit_of_measurement: "%"
      - name: PC RAM
        value_template: "{{ value_json.memory.percent }}"
        unit_of_measurement: "%"

rest_command:
  pc_shutdown:
    url: "http://ha-pc.local:8765/power/shutdown"
    method: POST
    headers:
      X-Api-Key: "your-long-random-secret"
      Content-Type: "application/json"
    payload: '{"delay_seconds": 0}'
```

`rest_command` öğeleri sensör olarak değil, **servis** olarak gelir (`rest_command.pc_shutdown`). Home Assistant `.local` çözemezse PC’nin LAN IP’sini kullanın.

*Not: Güvenlik duvarında `8765` portunu açın. API’yi yalnızca yerel ağda tutun ve güçlü bir `API_KEY` kullanın.*
