# Tuya Smart Meter Exporter

A lightweight Prometheus exporter for Tuya-based smart energy meter with 2 channels, packaged as a minimal Docker image.

## Features

- Collects real-time metrics from Tuya smart meters using the `tinytuya` library.
- Exposes metrics on `/metrics` for Prometheus scraping.
- Runs efficiently in Docker or with Docker Compose.
- Small image size based on Alpine Linux.

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t tuya-smart-meter-exporter .
```

### 2. Run the Exporter with Docker

Set your device's details as environment variables:

```bash
docker run -d -p 9999:9999 \
  -e EXPORTER_PORT=9999 \
  -e DEVICE_IP=<device-ip> \
  -e DEVICE_ID=<device-id> \
  -e DEVICE_LOCAL_KEY=<device-key> \
  tuya-smart-meter-exporter
```

### 3. Or Use Docker Compose

Edit `docker-compose.yaml` with your device info, then run:

```bash
docker compose up -d
```

Example `docker-compose.yaml`:
```yaml
services:
  tuya-smart-meter-exporter:
    image: cardif99/tuya-smart-meter-exporter:latest
    container_name: tuya-smart-meter-exporter
    environment:
      - EXPORTER_PORT=9999
      - DEVICE_IP=<device-ip>
      - DEVICE_ID=<device-id>
      - DEVICE_LOCAL_KEY=<device-key>
    restart: unless-stopped
    ports:
      - 9999:9999
```

### 4. Access Metrics

Visit [http://localhost:9999/metrics](http://localhost:9999/metrics) to see the exported metrics.

## Configuration

The exporter is configured via environment variables:

- `EXPORTER_PORT`: Port to expose the metrics endpoint (default: `9999`)
- `DEVICE_IP`: IP address of your Tuya smart meter
- `DEVICE_ID`: Device ID of your Tuya smart meter
- `DEVICE_LOCAL_KEY`: Local key for your Tuya smart meter

**All device variables are required.**

## Prometheus Integration

Add a scrape config to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'tuya-smart-meter'
    static_configs:
      - targets: ['localhost:9999']
```

## Development

Install dependencies locally:

```bash
pip install -r requirements.txt
```

Run the exporter:

```bash
export EXPORTER_PORT=9999
export DEVICE_IP=<device-ip>
export DEVICE_ID=<device-id>
export DEVICE_LOCAL_KEY=<device-key>
python src/tuya_exporter.py
```