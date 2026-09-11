# Agent Notes

## Purpose

This repository documents a Proxmox deployment on laptop hardware, with reusable configuration and platform-specific fixes.

## Read first

- README.md
- common/monitoring/README.md
- platforms/macbook-pro-2019-t2/BOOT.md
- platforms/macbook-pro-2019-t2/REBOOT.md

## Important verified behavior

- Normal firmware reboot does not complete with the lid closed on the 2019 T2 MacBook Pro.
- kexec reboot works with the lid closed.
- Wake-on-LAN packets reach the Thunderbolt Ethernet adapter but do not wake the MacBook.
- Thunderbolt dock hot-unplug is not considered reliable.
- The unused ZFS import service caused a two-minute boot delay.
- `prometheus-node-exporter` exposes host metrics on port 9100.
- Custom Prometheus metrics use the node_exporter textfile collector at `/var/lib/prometheus/node-exporter/`.
- Thermal and power metrics update every minute.
- NVMe SMART metrics update every 15 minutes.
- The Apple NVMe returns `smartctl` exit status 4 because one optional error-log page is unsupported; valid SMART JSON is still returned.

## Repository rules

- Keep reusable configuration under `common/`.
- Keep hardware-specific fixes under `platforms/`.
- Keep the existing thermal CSV logger; Prometheus export is additive rather than a replacement.
- Keep host-side monitoring lightweight. Prometheus server, Grafana, and broader observability services belong off the hypervisor.
- Do not commit credentials, private keys, Wi-Fi passwords, logs, runtime CSV data, generated `.prom` files, or VM data.
- Distinguish verified fixes from experiments or hypotheses.
- Avoid re-testing known failed reboot and WoL approaches unless new evidence justifies it.

## Current platform

2019 Intel MacBook Pro with Apple T2 running Proxmox VE.
