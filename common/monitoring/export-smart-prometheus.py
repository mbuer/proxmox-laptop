#!/usr/bin/env python3

import json
import os
import subprocess

OUTPUT_FILE = "/var/lib/prometheus/node-exporter/proxmox_nvme.prom"
TEMP_FILE = OUTPUT_FILE + ".tmp"

result = subprocess.run(
    ["smartctl", "-a", "-j", "/dev/nvme0"],
    capture_output=True,
    text=True,
)

if not result.stdout.strip():
    raise RuntimeError("smartctl returned no JSON output")

data = json.loads(result.stdout)

health = data.get("nvme_smart_health_information_log")
if not health:
    raise RuntimeError("NVMe SMART health data missing")

metrics = [
    ("proxmox_nvme_critical_warning", "gauge", health["critical_warning"]),
    ("proxmox_nvme_available_spare_percent", "gauge", health["available_spare"]),
    ("proxmox_nvme_percentage_used", "gauge", health["percentage_used"]),
    ("proxmox_nvme_media_errors_total", "counter", health["media_errors"]),
    ("proxmox_nvme_error_log_entries_total", "counter", health["num_err_log_entries"]),
    ("proxmox_nvme_unsafe_shutdowns_total", "counter", health["unsafe_shutdowns"]),
    ("proxmox_nvme_power_cycles_total", "counter", health["power_cycles"]),
    ("proxmox_nvme_power_on_hours", "counter", health["power_on_hours"]),
    ("proxmox_nvme_data_units_read_total", "counter", health["data_units_read"]),
    ("proxmox_nvme_data_units_written_total", "counter", health["data_units_written"]),
]

with open(TEMP_FILE, "w") as f:
    for metric, metric_type, value in metrics:
        f.write(f"# TYPE {metric} {metric_type}\n")
        f.write(f"{metric} {value}\n")

os.chmod(TEMP_FILE, 0o644)
os.replace(TEMP_FILE, OUTPUT_FILE)
