#!/usr/bin/env python3

import csv
import os

CSV_FILE = "/opt/proxmox-thermal/temps.csv"
OUTPUT_FILE = "/var/lib/prometheus/node-exporter/proxmox_thermal.prom"
TEMP_FILE = OUTPUT_FILE + ".tmp"

METRICS = {
    "cpu_package_c": "proxmox_thermal_cpu_package_celsius",
    "cpu_max_core_c": "proxmox_thermal_cpu_max_core_celsius",
    "pch_c": "proxmox_thermal_pch_celsius",
    "gpu_c": "proxmox_thermal_gpu_celsius",
    "nvme_c": "proxmox_thermal_nvme_celsius",
    "battery_c": "proxmox_thermal_battery_celsius",
}

with open(CSV_FILE, newline="") as f:
    rows = list(csv.DictReader(f))

if not rows:
    raise RuntimeError("No thermal samples found")

latest = rows[-1]

with open(TEMP_FILE, "w") as f:
    for column, metric in METRICS.items():
        value = latest.get(column)

        if value not in (None, ""):
            f.write(
                f"# HELP {metric} Temperature reported by Proxmox thermal logger.\n"
            )
            f.write(f"# TYPE {metric} gauge\n")
            f.write(f"{metric} {value}\n")

os.chmod(TEMP_FILE, 0o644)
os.replace(TEMP_FILE, OUTPUT_FILE)
