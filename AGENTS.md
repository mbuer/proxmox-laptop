# Agent Notes

## Purpose
This repository documents a Proxmox deployment on laptop hardware, with reusable configuration and platform-specific fixes.

## Read first
- README.md
- platforms/macbook-pro-2019-t2/BOOT.md
- platforms/macbook-pro-2019-t2/REBOOT.md

## Important verified behavior
- Normal firmware reboot does not complete with the lid closed on the 2019 T2 MacBook Pro.
- kexec reboot works with the lid closed.
- Wake-on-LAN packets reach the Thunderbolt Ethernet adapter but do not wake the MacBook.
- Thunderbolt dock hot-unplug is not considered reliable.
- The unused ZFS import service caused a two-minute boot delay.

## Repository rules
- Keep reusable configuration under `common/`.
- Keep hardware-specific fixes under `platforms/`.
- Do not commit credentials, private keys, Wi-Fi passwords, logs, or VM data.
- Distinguish verified fixes from experiments or hypotheses.
- Avoid re-testing known failed reboot and WoL approaches unless new evidence justifies it.

## Current platform
2019 Intel MacBook Pro with Apple T2 running Proxmox VE.
