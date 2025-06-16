# Tuya Smart Meter Exporter

A lightweight Prometheus exporter for Tuya-based Smart Energy Meter with 2 channels, packaged as a minimal Docker image.

## Features

- Collects real-time metrics from Tuya smart meters using the `tinytuya` library.
- Exposes metrics on `/metrics` for Prometheus scraping.
- Multi-device support via configuration.
- Efficient, small Docker image based on Alpine Linux.

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t tuya-smart-meter-exporter .
```

### 2. Run the Exporter

Replace the device configuration in `src/tuya_exporter.py` with your device's IP, ID, and local key.

```bash
docker run -d -p 9999:9999 --name tuya-exporter tuya-smart-meter-exporter
```

### 3. Access Metrics

Visit [http://localhost:9999/metrics](http://localhost:9999/metrics) to see the exported metrics.

## Configuration

Edit the `DEVICE_CONFIGS` list in `src/tuya_exporter.py` to add your Tuya smart meter(s):

```python
DEVICE_CONFIGS = [
    {
        "ip": "x.x.x.x",
        "device_id": "your_device_id",
        "local_key": "your_local_key"
    }
]
```

## Prometheus Integration

Add a scrape config to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'tuya-smart-meter'
    static_configs:
      - targets: ['tuya-exporter:9999']
```

## Requirements

- Docker
- Tuya smart meter (with local access enabled)

## Development

Install dependencies locally:

```bash
pip install -r requirements.txt
```

Run the exporter:

```bash
python src/tuya_exporter.py
```

## License

MIT License

---

**Note:**  
Make sure your Tuya device supports local access and you have the correct `device_id`