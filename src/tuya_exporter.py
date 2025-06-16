from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST, CollectorRegistry
from wsgiref.simple_server import make_server
import time
import tinytuya
import threading

# Exporter Configuration
EXPORTER_PORT = 9999

# Device Configuration
DEVICE_CONFIGS = [
    {
        "ip": "",
        "device_id": "",
        "local_key": ""
    }
]

# Prometheus Metrics
registry = CollectorRegistry()
metrics = {
    "current_a": Gauge("tuya_current_a", "Current in A.", ["device_id"], registry=registry),
    "current_b": Gauge("tuya_current_b", "Current in A.", ["device_id"], registry=registry),
    "direction_current_a": Gauge("tuya_direction_current_a", "Direction of current 1 is forward, 0 is reverse.", ["device_id"], registry=registry),
    "direction_current_b": Gauge("tuya_direction_current_b", "Direction of current 1 is forward, 0 is reverse.", ["device_id"], registry=registry),
    "energy_forward_a": Gauge("tuya_energy_forward_a", "Forward energy in kWh.", ["device_id"], registry=registry),
    "energy_forward_b": Gauge("tuya_energy_forward_b", "Forward energy in kWh.", ["device_id"], registry=registry),
    "energy_reverse_a": Gauge("tuya_energy_reverse_a", "Reverse energy in kWh.", ["device_id"], registry=registry),
    "energy_reverse_b": Gauge("tuya_energy_reverse_b", "Reverse energy in kWh.", ["device_id"], registry=registry),
    "power_a": Gauge("tuya_power_a", "Power in W.", ["device_id"], registry=registry),
    "power_b": Gauge("tuya_power_b", "Power in W.", ["device_id"], registry=registry),
    "power_factor_a": Gauge("tuya_power_factor_a", "Power factor.", ["device_id"], registry=registry),
    "power_factor_b": Gauge("tuya_power_factor_b", "Power factor.", ["device_id"], registry=registry),
    "forward_energy_total": Gauge("tuya_forward_energy_total", "Total forward energy in kWh.", ["device_id"], registry=registry),
    "reverse_energy_total": Gauge("tuya_reverse_energy_total", "Total reverse energy in kWh.", ["device_id"], registry=registry),
    "total_power": Gauge("tuya_total_power", "Total power in W.", ["device_id"], registry=registry),
    "frequency": Gauge("tuya_frequency", "Frequency in Hz.", ["device_id"], registry=registry),
    "voltage": Gauge("tuya_voltage", "Voltage in V.", ["device_id"], registry=registry),
}

# Tuya Device Data Points (DPS)
DPS_CURRENT_A                     = '105'
DPS_CURRENT_B                     = '110'
DPS_DIR_CUR_A                     = '124'
DPS_DIR_CUR_B                     = '125'
DPS_ENERGY_FORWARD_A              = '107'
DPS_ENERGY_FORWARD_B              = '112'
DPS_ENERGY_REVERSE_A              = '108'
DPS_ENERGY_REVERSE_B              = '113'
DPS_POWER_A                       = '106'
DPS_POWER_B                       = '111'
DPS_POWER_FACTOR_A                = '104'
DPS_POWER_FACTOR_B                = '109'
DPS_FORWARD_ENERGY_TOTAL          = '1'
DPS_REVERSE_ENERGY_TOTAL          = '2'
DPS_TOTAL_POWER                   = '103'
DPS_FREQ                          = '102'
DPS_VOLTAGE                       = '101'

device_metrics = {config["device_id"]: {
    "current_a": float("nan"),
    "current_b": float("nan"),
    "direction_current_a": float("nan"),
    "direction_current_b": float("nan"),
    "energy_forward_a": float("nan"),
    "energy_forward_b": float("nan"),
    "energy_reverse_a": float("nan"),
    "energy_reverse_b": float("nan"),
    "power_a": float("nan"),
    "power_b": float("nan"),
    "power_factor_a": float("nan"),
    "power_factor_b": float("nan"),
    "forward_energy_total": float("nan"),
    "reverse_energy_total": float("nan"),
    "total_power": float("nan"),
    "frequency": float("nan"),
    "voltage": float("nan")
} for config in DEVICE_CONFIGS}

def update_device_metrics(device_config):
    """Continuously fetch metrics for a device in the background."""
    device_id = device_config["device_id"]
    device = tinytuya.Device(device_config["device_id"], device_config["ip"], device_config["local_key"])
    device.set_socketTimeout(3)
    last_successful_version = None
    while True:
        try:
            # Try last successful version first for efficiency
            versions_to_try = [last_successful_version] if last_successful_version else []
            versions_to_try += [v for v in [3.4, 3.3, 3.2, 3.1, 3.0] if v != last_successful_version]
            for version in versions_to_try:
                try:
                    device.set_version(version)
                    device.updatedps(["18", "19", "20"])
                    data = device.status()
                    if "Error" not in data:
                        device_metrics[device_id] = {
                            "current_a": float(data["dps"].get(DPS_CURRENT_A, 0)) / 1000.0,
                            "current_b": float(data["dps"].get(DPS_CURRENT_B, 0)) / 1000.0,
                            "direction_current_a": int(data["dps"].get(DPS_DIR_CUR_A, 0)),
                            "direction_current_b": int(data["dps"].get(DPS_DIR_CUR_B, 0)),
                            "energy_forward_a": float(data["dps"].get(DPS_ENERGY_FORWARD_A, 0)) / 100.0,
                            "energy_forward_b": float(data["dps"].get(DPS_ENERGY_FORWARD_B, 0)) / 100.0,
                            "energy_reverse_a": float(data["dps"].get(DPS_ENERGY_REVERSE_A, 0)) / 100.0,
                            "energy_reverse_b": float(data["dps"].get(DPS_ENERGY_REVERSE_B, 0)) / 100.0,
                            "power_a": float(data["dps"].get(DPS_POWER_A, 0)) / 10.0,
                            "power_b": float(data["dps"].get(DPS_POWER_B, 0)) / 10.0,
                            "power_factor_a": float(data["dps"].get(DPS_POWER_FACTOR_A, 0)) / 100.0,
                            "power_factor_b": float(data["dps"].get(DPS_POWER_FACTOR_B, 0)) / 100.0,
                            "forward_energy_total": float(data["dps"].get(DPS_FORWARD_ENERGY_TOTAL, 0)) / 100.0,
                            "reverse_energy_total": float(data["dps"].get(DPS_REVERSE_ENERGY_TOTAL, 0)) / 100.0,
                            "total_power": float(data["dps"].get(DPS_TOTAL_POWER, 0)) / 10.0,
                            "frequency": float(data["dps"].get(DPS_FREQ, 0)) / 100.0,
                            "voltage": float(data["dps"].get(DPS_VOLTAGE, 0)) / 10.0
                        }
                        print(f"Updated metrics for device {device_id} using version {version}")
                        last_successful_version = version
                        break
                except Exception as ex:
                    print(f"Exception while setting version {version} for device {device_id}: {type(ex).__name__}: {ex}")
                    continue
            else:
                raise Exception(f"Failed to connect to device {device_id}")
        except Exception as e:
            print(f"Error updating device {device_id}: {e}")
            # Set all values to NaN when device update fails
            for key in device_metrics[device_id]:
                device_metrics[device_id][key] = float("nan")
        time.sleep(10)

def start_background_updater():
    """Start background threads to update metrics for all devices."""
    for config in DEVICE_CONFIGS:
        threading.Thread(target=update_device_metrics, args=(config,), daemon=True).start()

# Cache for metrics output
_metrics_cache = {
    "data": None,
    "timestamp": 0
}
_metrics_cache_lock = threading.Lock()
_METRICS_CACHE_TTL = 5  # seconds

def metrics_app(environ, start_response):
    """WSGI application for Prometheus metrics."""
    if environ["PATH_INFO"] == "/metrics":
        for device_id, metrics_data in device_metrics.items():
            metrics["current_a"].labels(device_id=device_id).set(metrics_data["current_a"])
            metrics["current_b"].labels(device_id=device_id).set(metrics_data["current_b"])
            metrics["direction_current_a"].labels(device_id=device_id).set(metrics_data["direction_current_a"])
            metrics["direction_current_b"].labels(device_id=device_id).set(metrics_data["direction_current_b"])
            metrics["energy_forward_a"].labels(device_id=device_id).set(metrics_data["energy_forward_a"])
            metrics["energy_forward_b"].labels(device_id=device_id).set(metrics_data["energy_forward_b"])
            metrics["energy_reverse_a"].labels(device_id=device_id).set(metrics_data["energy_reverse_a"])
            metrics["energy_reverse_b"].labels(device_id=device_id).set(metrics_data["energy_reverse_b"])
            metrics["power_a"].labels(device_id=device_id).set(metrics_data["power_a"])
            metrics["power_b"].labels(device_id=device_id).set(metrics_data["power_b"])
            metrics["power_factor_a"].labels(device_id=device_id).set(metrics_data["power_factor_a"])
            metrics["power_factor_b"].labels(device_id=device_id).set(metrics_data["power_factor_b"])
            metrics["forward_energy_total"].labels(device_id=device_id).set(metrics_data["forward_energy_total"])
            metrics["reverse_energy_total"].labels(device_id=device_id).set(metrics_data["reverse_energy_total"])
            metrics["total_power"].labels(device_id=device_id).set(metrics_data["total_power"])
            metrics["frequency"].labels(device_id=device_id).set(metrics_data["frequency"])
            metrics["voltage"].labels(device_id=device_id).set(metrics_data["voltage"])
        now = time.time()
        with _metrics_cache_lock:
            if (_metrics_cache["data"] is None) or (now - _metrics_cache["timestamp"] > _METRICS_CACHE_TTL):
                _metrics_cache["data"] = generate_latest(registry)
                _metrics_cache["timestamp"] = now
            data = _metrics_cache["data"]
        start_response("200 OK", [("Content-type", CONTENT_TYPE_LATEST)])
        return [data]
    start_response("404 Not Found", [("Content-type", "text/plain")])

if __name__ == "__main__":
    print(f"Starting server on http://localhost:{EXPORTER_PORT}/metrics")
    start_background_updater()
    try:
        make_server("0.0.0.0", EXPORTER_PORT, metrics_app).serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server.")
