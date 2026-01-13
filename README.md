# ATS Mileage Sync Service

ATS Mileage Sync Service, TNB Mobil ATS SOAP servisinden araç kilometre verilerini alarak
Microsoft SQL Server veritabanına güvenli, izlenebilir ve idempotent şekilde aktaran
Python tabanlı bir batch ETL servisidir.

Servis günlük olarak çalışacak şekilde tasarlanmıştır ve tüm kayıt işlemleri tek bir
transaction içinde gerçekleştirilir. İşlem sonunda yalnızca **tek bir özet mail**
gönderilir.

## İçindekiler

- [Özellikler](#özellikler)
- [Mimari Özet](#mimari-özet)
- [Proje Yapısı](#proje-yapısı)
- [Gereksinimler](#gereksinimler)
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
- [Yapılandırma](#yapılandırma)
- [Lisans](#lisans)

---

## Özellikler

- SOAP Web Service üzerinden kilometre verisi çekme
- XML parsing ve veri doğrulama
- MSSQL transaction yönetimi (commit / rollback)
- Duplicate (aynı gün–aynı device) kayıtları otomatik skip etme
- Günlük **tek summary mail**
- Hata durumunda **tek error mail**
- Docker uyumlu (container job pattern)
- Windows Task Scheduler / Linux cron ile çalıştırılabilir

---

## Mimari Özet

```text
SOAP Service
    |
    v
XML Fetch
    |
    v
XML Parse
    |
    v
MSSQL INSERT (Transaction)
    |
    +--> COMMIT   -> Summary Mail
    |
    +--> ROLLBACK -> Error Mail
```

---

## Proje Yapısı

### Application Layer
- `main.py` – Entry point
- `job.py` – ETL orchestration

### Integration Layer
- `soap_client.py` – SOAP client
- `parser.py` – XML parser

### Infrastructure Layer
- `db.py` – MSSQL operations
- `mail_client.py` – Mail sender
- `logger.py` – Logging
- `config.py` – Environment config

### Deployment
- `Dockerfile`
- `docker-compose.yml`

---

## Gereksinimler

### Yerel Çalıştırma

- Python 3.10+
- MSSQL ODBC Driver 17
- SQL Server erişimi
- SMTP erişimi

### Docker ile Çalıştırma

- Docker Engine 20+
- Docker Compose (opsiyonel)

---

## Kurulum

### Yerel Kurulum

1. Sanal ortam oluşturun:
   ```bash
   python -m venv venv
   ```

2. Sanal ortamı etkinleştirin:
   ```bash
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

### Docker ile Kurulum

Dockerfile ve docker-compose.yml dosyalarını kullanarak container oluşturun.

```bash
docker build -t ats-mileage-sync .
```

---

## Kullanım

### Yerel Çalıştırma

Servisi çalıştırmak için:

```bash
python -m src.main
```

Belirli bir tarih için çalıştırmak:

```bash
python -m src.main --date 2026-01-06
```

### Otomatik Çalıştırma

- **Windows**: Task Scheduler ile `scripts/run_daily.sh` betiğini günlük çalıştırın.
- **Linux**: Cron job ile `scripts/run_daily.sh` betiğini günlük çalıştırın.

### Docker ile Çalıştırma

```bash
docker run ats-mileage-sync
```

---

## Yapılandırma

Ortam değişkenlerini `.env` dosyasında ayarlayın:

```env
# SOAP
SOAP_URL=xxxx
SOAP_ACTION=xxxx
SOAP_USERNAME=xxxxx
SOAP_PASSWORD=xxxxx
SOAP_COMPANY_CODE=xxxx

# MSSQL
MSSQL_DRIVER=ODBC Driver 17 for SQL Server
MSSQL_SERVER=xxxx
MSSQL_DATABASE=xxxx
MSSQL_USER=xxxx
MSSQL_PASSWORD=xxxxx

# Application
DEDUPLICATE=true

# Mail
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=xxxx
SMTP_PASSWORD=xxxxx
MAIL_FROM=xxxx
MAIL_TO=xxxx
```

---

## Lisans

Bu proje [LICENSE](LICENSE) dosyasında belirtilen lisans altında lisanslanmıştır.
