# proxmox-laptop

Reusable configs, fixes, and deployment notes for running Proxmox on laptop hardware.

This repository documents a real Proxmox deployment on a laptop used as an always-on home lab server. The goal is to keep useful configuration and hardware-specific fixes reproducible without storing machine state, credentials, or VM data.

## Current deployment

First platform:

- 2019 Intel MacBook Pro
- Proxmox VE
- closed-lid operation
- Thunderbolt dock networking
- Apple T2 keyboard and trackpad support
- display and Touch Bar power handling
- temperature logging
- kexec-based closed-lid reboot
- documented boot and Wake-on-LAN behavior

## Key findings

On the 2019 T2 MacBook Pro:

- normal firmware reboot does not complete with the lid closed
- the same behavior occurs from a clean Proxmox installer USB
- `reboot=pci`, `reboot=efi`, and `reboot=acpi` did not solve it
- kexec reboot works with the lid closed
- Wake-on-LAN packets reach the Thunderbolt Ethernet adapter, but do not wake the MacBook from suspend or power-off
- unused ZFS import services caused a two-minute boot delay and were disabled

## Repository layout

- `common/network` — reusable network configuration
- `common/thermal` — temperature logging
- `platforms/macbook-pro-2019-t2/lid` — closed-lid display handling
- `platforms/macbook-pro-2019-t2/t2` — Apple T2 support
- `platforms/macbook-pro-2019-t2/BOOT.md` — boot behavior and fixes
- `platforms/macbook-pro-2019-t2/REBOOT.md` — reboot and Wake-on-LAN findings
- `platforms/macbook-pro-2019-t2/wifi` — Apple Wi-Fi notes and configuration examples

More laptop platforms can be added under `platforms/`.
