# Closed-lid reboot

On this 2019 Intel MacBook Pro with Apple T2, a normal firmware reboot does not complete while the lid remains closed.

Linux shuts down cleanly, but the next firmware boot does not start until the lid is opened or a key is pressed.

## Verified behavior

- Normal reboot with lid open: works
- Normal reboot with lid closed: fails
- Opening the lid after the failed reboot allows boot to continue
- `reboot=pci`: did not solve the issue
- `reboot=efi`: did not solve the issue
- `reboot=acpi`: did not solve the issue
- T2 BCE modules unloaded before reboot: still fails
- custom ACPI lid/backlight handler disabled before reboot: still fails
- clean Proxmox installer USB environment: same closed-lid reboot failure

The installer USB test is important because it reproduces the problem without the installed host configuration, custom lid scripts, T2 BCE setup, or kexec configuration.

This strongly suggests the behavior is related to the MacBook firmware/platform rather than the Proxmox installation.

## kexec

A kexec reboot works successfully with the lid remaining closed.

kexec skips the Apple firmware reboot path and jumps directly from the running Linux kernel into a new Linux kernel.

Manual test:

    kexec -l /boot/vmlinuz-$(uname -r) \
      --initrd=/boot/initrd.img-$(uname -r) \
      --command-line="$(cat /proc/cmdline | sed 's/BOOT_IMAGE=[^ ]* //')"

Then:

    systemctl kexec

After the kexec reboot, the following were verified:

- networking
- T2 BCE modules
- ACPI lid handling
- thermal logging

## kexec-tools configuration

The Proxmox installation does not provide `/vmlinuz` and `/initrd.img` symlinks.

The default `/etc/default/kexec` configuration therefore failed to preload a kernel.

Using:

    USE_GRUB_CONFIG=true

allows `kexec-load-kernel` to select the default kernel and initrd from GRUB.

Verification:

    kexec-load-kernel
    cat /sys/kernel/kexec_loaded

Expected result:

    1

When a kexec kernel is preloaded, systemd can use it for a kexec reboot.

## Wake-on-LAN

The CalDigit TS4 Intel Ethernet interface reports:

    Supports Wake-on: pumbg
    Wake-on: g

Magic packets were verified reaching the interface from another machine using tcpdump:

    tcpdump -ni ents4 udp port 9

However:

- Wake-on-LAN from full shutdown did not power on the MacBook
- Wake-on-LAN from suspend did not wake the MacBook
- the TS4 Ethernet interface remained powered after shutdown

This suggests the Ethernet controller receives standby power, but the MacBook firmware/T2 platform does not propagate the Thunderbolt/PCIe wake event into a system power-on or wake.

## Recommended operation

Routine remote reboot:

    systemctl kexec

Full hardware reset:

    shutdown -h now

A full shutdown still performs a complete hardware and firmware reset, but powering the MacBook back on currently requires local interaction.

