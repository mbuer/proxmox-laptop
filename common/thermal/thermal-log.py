#!/usr/bin/env python3

import csv
import json
import os
import subprocess
from datetime import datetime

BASE = "/opt/proxmox-thermal"
LOGFILE = f"{BASE}/temps.csv"

data = json.loads(
    subprocess.check_output(["sensors", "-j"], text=True)
)

def find_value(chip_prefix, label, field):
    for chip, values in data.items():
        if chip.startswith(chip_prefix):
            if label in values:
                return values[label].get(field)
    return None

cpu = find_value("coretemp", "Package id 0", "temp1_input")

cores = []
for chip, values in data.items():
    if chip.startswith("coretemp"):
        for label, fields in values.items():
            if label.startswith("Core "):
                for key, value in fields.items():
                    if key.endswith("_input"):
                        cores.append(value)

cpu_max = max(cores) if cores else None
pch = find_value("pch_cannonlake", "temp1", "temp1_input")
gpu = find_value("amdgpu", "edge", "temp1_input")
nvme = find_value("nvme", "Composite", "temp1_input")
battery = find_value("BAT0", "temp", "temp1_input")

with open("/proc/loadavg") as f:
    load1 = float(f.read().split()[0])

row = [
    datetime.now().isoformat(timespec="seconds"),
    cpu,
    cpu_max,
    pch,
    gpu,
    nvme,
    battery,
    load1,
]

new_file = not os.path.exists(LOGFILE) or os.path.getsize(LOGFILE) == 0

with open(LOGFILE, "a", newline="") as f:
    writer = csv.writer(f)

    if new_file:
        writer.writerow([
            "timestamp",
            "cpu_package_c",
            "cpu_max_core_c",
            "pch_c",
            "gpu_c",
            "nvme_c",
            "battery_c",
            "load1",
        ])

    writer.writerow(row)

