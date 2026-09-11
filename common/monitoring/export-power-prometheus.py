#!/usr/bin/env python3

import os

OUTPUT_FILE = "/var/lib/prometheus/node-exporter/proxmox_power.prom"
TEMP_FILE = OUTPUT_FILE + ".tmp"

def read(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

ac_online = read("/sys/class/power_supply/ADP1/online")
battery_capacity = read("/sys/class/power_supply/BAT0/capacity")
battery_cycles = read("/sys/class/power_supply/BAT0/cycle_count")
battery_status = read("/sys/class/power_supply/BAT0/status")

with open(TEMP_FILE, "w") as f:
    if ac_online is not None:
        f.write("# HELP proxmox_ac_power_connected Whether external AC power is connected.\n")
        f.write("# TYPE proxmox_ac_power_connected gauge\n")
        f.write(f"proxmox_ac_power_connected {ac_online}\n")

    if battery_capacity is not None:
        f.write("# HELP proxmox_battery_charge_percent Current battery charge percentage.\n")
        f.write("# TYPE proxmox_battery_charge_percent gauge\n")
        f.write(f"proxmox_battery_charge_percent {battery_capacity}\n")

    if battery_cycles is not None:
        f.write("# HELP proxmox_battery_cycle_count Battery cycle count.\n")
        f.write("# TYPE proxmox_battery_cycle_count gauge\n")
        f.write(f"proxmox_battery_cycle_count {battery_cycles}\n")

    if battery_status:
        safe_status = battery_status.replace("\\", "\\\\").replace('"', '\\"')
        f.write("# HELP proxmox_battery_status Current battery status.\n")
        f.write("# TYPE proxmox_battery_status gauge\n")
        f.write(f'proxmox_battery_status{{status="{safe_status}"}} 1\n')

os.chmod(TEMP_FILE, 0o644)
os.replace(TEMP_FILE, OUTPUT_FILE)
