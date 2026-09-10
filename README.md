# proxmox-laptop

Reusable configs, fixes, and deployment notes for running Proxmox on laptop hardware.

This repository documents a real Proxmox deployment on a laptop used as an always-on home lab server. The goal is to keep the useful configuration and hardware-specific fixes reproducible without storing machine state, credentials, or VM data.

## Current deployment

First platform:

- 2019 Intel MacBook Pro
- Proxmox VE
- closed-lid operation
- Thunderbolt dock networking
- Apple T2 keyboard and trackpad support
- display and Touch Bar power handling
- temperature logging
- experimental closed-lid reboot handling

## Repository layout

- `common/network` — reusable network configuration
- `common/thermal` — temperature logging
- `platforms/macbook-pro-2019-t2/lid` — closed-lid display handling
- `platforms/macbook-pro-2019-t2/t2` — Apple T2 support
- `platforms/macbook-pro-2019-t2/wifi` — Apple Wi-Fi notes and configuration examples

More laptop platforms can be added under `platforms/`.
