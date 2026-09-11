# Prometheus host monitoring

This directory contains the Proxmox-side components used to expose host health metrics to Prometheus.

The design keeps the hypervisor lightweight: the Proxmox host collects and exposes measurements, while a separate Prometheus server will later store the time series, evaluate them, and provide them to Grafana.

## Architecture

    Proxmox host
        │
        ├── node_exporter native collectors
        │     ├── CPU
        │     ├── memory
        │     ├── filesystem
        │     ├── network
        │     └── operating-system metrics
        │
        ├── thermal-log.py
        │     ├── temps.csv
        │     └── export-prometheus.py
        │           └── proxmox_thermal.prom
        │
        ├── Linux power_supply interface
        │     └── export-power-prometheus.py
        │           └── proxmox_power.prom
        │
        └── smartctl
              └── export-smart-prometheus.py
                    └── proxmox_nvme.prom

                             │
                             ▼
                   node_exporter :9100
                             │
                             │ scrape
                             ▼
                    Prometheus server
                             │
                             ▼
                        Grafana OSS

## Prometheus and node_exporter

`node_exporter` is not the Prometheus server.

It runs on the monitored machine and exposes measurements through an HTTP endpoint:

    http://<proxmox-host>:9100/metrics

A Prometheus server periodically **scrapes** that endpoint and stores the measurements as time series.

The Debian `prometheus-node-exporter` package already exposes most normal Linux host information, including:

- CPU utilization and load
- memory and swap
- filesystem usage and inode statistics
- network traffic and errors
- uptime
- kernel and operating-system information

Custom collectors are used only for hardware information that node_exporter does not expose conveniently by itself.

## Textfile collector

node_exporter includes a **textfile collector** for custom metrics.

On this system it reads:

    /var/lib/prometheus/node-exporter/

Scripts can place Prometheus-formatted `.prom` files there and node_exporter automatically includes them in `/metrics`.

For example:

    proxmox_battery_charge_percent 82

The custom exporters write these files atomically:

1. Write the new metrics to a temporary file.
2. Finish writing the complete file.
3. Replace the existing `.prom` file.

This prevents node_exporter from reading a partially written metrics file during a scrape.

## Thermal monitoring

The existing thermal logger remains responsible for collecting temperature history:

    /opt/proxmox-thermal/thermal-log.py

It runs once per minute and writes:

    /opt/proxmox-thermal/temps.csv

The CSV is retained independently of Prometheus and is rotated daily with seven compressed rotations.

After each thermal sample, `export-prometheus.py` reads the newest CSV row and writes:

    /var/lib/prometheus/node-exporter/proxmox_thermal.prom

### Thermal metrics

| Metric | Meaning |
| --- | --- |
| `proxmox_thermal_cpu_package_celsius` | CPU package temperature |
| `proxmox_thermal_cpu_max_core_celsius` | Hottest CPU core |
| `proxmox_thermal_pch_celsius` | Platform Controller Hub temperature |
| `proxmox_thermal_gpu_celsius` | Discrete GPU temperature |
| `proxmox_thermal_nvme_celsius` | NVMe temperature reported through hwmon |
| `proxmox_thermal_battery_celsius` | Battery temperature |

The one-minute interval is intentional. Temperatures can change quickly enough that this gives useful resolution while generating very little data.

## Power and battery monitoring

`export-power-prometheus.py` reads Linux power-supply information from:

    /sys/class/power_supply/

On the current MacBook Pro:

    ADP1 = AC adapter
    BAT0 = battery

Metrics are written to:

    /var/lib/prometheus/node-exporter/proxmox_power.prom

### Power metrics

| Metric | Meaning |
| --- | --- |
| `proxmox_ac_power_connected` | `1` when external power is connected |
| `proxmox_battery_charge_percent` | Current battery charge |
| `proxmox_battery_cycle_count` | Battery cycle count |
| `proxmox_battery_status{status="..."}` | Kernel-reported battery state |

The current Linux/T2 power-supply interface does not expose usable `energy_full` and `energy_full_design` values, so battery-health percentage is not calculated.

Power metrics are refreshed once per minute together with the thermal measurements.

## NVMe SMART monitoring

`export-smart-prometheus.py` collects SSD health information with:

    smartctl -a -j /dev/nvme0

JSON output is used instead of parsing the human-readable SMART report.

Metrics are written to:

    /var/lib/prometheus/node-exporter/proxmox_nvme.prom

### NVMe metrics

| Metric | Type | Meaning |
| --- | --- | --- |
| `proxmox_nvme_critical_warning` | gauge | NVMe critical-warning bit field |
| `proxmox_nvme_available_spare_percent` | gauge | Remaining spare capacity |
| `proxmox_nvme_percentage_used` | gauge | SSD endurance consumed |
| `proxmox_nvme_media_errors_total` | counter | Media/data-integrity errors |
| `proxmox_nvme_error_log_entries_total` | counter | NVMe error-log entries |
| `proxmox_nvme_unsafe_shutdowns_total` | counter | Unsafe shutdown count |
| `proxmox_nvme_power_cycles_total` | counter | SSD power cycles |
| `proxmox_nvme_power_on_hours` | counter | SSD operating hours |
| `proxmox_nvme_data_units_read_total` | counter | NVMe data units read |
| `proxmox_nvme_data_units_written_total` | counter | NVMe data units written |

SMART information is refreshed every 15 minutes.

Unlike temperature, SSD wear and error counters change slowly. Polling SMART every minute would provide little additional value.

### Apple NVMe quirk

The Apple SSD reports:

    Read 1 entries from Error Information Log failed:
    Invalid Log Page (0x109)

This causes `smartctl` to return exit status `4`.

The SSD still returns valid health information including wear, available spare, critical-warning state, media errors, power statistics, and data counters.

The exporter therefore validates the returned JSON instead of treating this exit status alone as SSD failure.

## Scheduling

Thermal and power metrics share the existing one-minute timer:

    proxmox-thermal.timer
            │
            ▼
    proxmox-thermal.service
            ├── thermal-log.py
            ├── export-prometheus.py
            └── export-power-prometheus.py

NVMe SMART uses a separate 15-minute timer:

    proxmox-smart-prometheus.timer
            │
            ▼
    proxmox-smart-prometheus.service
            └── export-smart-prometheus.py

Both services use `Type=oneshot`.

They run their task and exit, so this state after successful execution is normal:

    Active: inactive (dead)

The important result is:

    status=0/SUCCESS

The timers remain active and trigger the services again at their configured intervals.

## Sampling vs. scraping

These are different concepts.

**Sampling** is how often a local collector obtains a new measurement.

**Scraping** is how often Prometheus asks node_exporter for the currently available metrics.

For example:

    temperature sensor
          │
          │ once per minute
          ▼
    thermal collector
          │
          ▼
    proxmox_thermal.prom
          │
          ▼
    node_exporter
          │
          │ Prometheus scrape
          ▼
    Prometheus time-series database

If Prometheus later scrapes every 15 seconds while the thermal collector updates once per minute, Prometheus will see the same thermal value several times until the next sample is created.

A faster scrape interval does not increase the resolution of the underlying measurement.

## Validation

Check node_exporter:

    systemctl status prometheus-node-exporter

Confirm port 9100:

    ss -ltnp | grep 9100

Inspect custom metrics:

    curl -s http://127.0.0.1:9100/metrics | grep '^proxmox_'

Check scheduled collectors:

    systemctl list-timers --all | grep proxmox

Inspect generated textfiles:

    ls -lh /var/lib/prometheus/node-exporter/

## Network exposure

node_exporter currently listens on:

    *:9100

This makes the metrics endpoint reachable through the Proxmox host's network interfaces.

The intended design is for the future Prometheus server to scrape this endpoint over the trusted local network.

Port `9100` should not be exposed directly to the public Internet. Access restrictions belong in the Proxmox firewall/security configuration.

## Future integration

The next monitoring layer will live outside the hypervisor:

    Proxmox node_exporter
            │
            ▼
       Prometheus
            │
            ▼
       Grafana OSS

Later monitoring can add:

- Proxmox node and VM state
- storage health
- backup success/failure
- service availability
- alerting
- additional Linux hosts
- SNMP-based network-device monitoring

Those components belong on the monitoring infrastructure rather than on the Proxmox host itself.

This keeps the hypervisor focused on running workloads while still exposing enough information to understand its health.
