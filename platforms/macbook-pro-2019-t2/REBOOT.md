# Closed-lid reboot

On this 2019 Intel MacBook Pro with Apple T2, a normal Linux reboot does not reliably restart the machine while the lid remains closed.

## Observed behavior

- Normal reboot with lid open: works
- Normal reboot with lid closed: Linux shuts down, but the next firmware boot does not start automatically
- Opening the lid or pressing a key allows boot to continue

## Tested workaround

The kernel parameter:

    reboot=pci

did not solve the issue.

## kexec test

Loading the current kernel:

    kexec -l /boot/vmlinuz-$(uname -r) \
      --initrd=/boot/initrd.img-$(uname -r) \
      --command-line="$(cat /proc/cmdline | sed 's/BOOT_IMAGE=[^ ]* //')"

Then rebooting with:

    systemctl kexec

worked successfully with the lid remaining closed.

After the kexec reboot, the following were verified:

- networking
- T2 BCE modules
- ACPI lid handling
- thermal logging

## Status

A cleaner system-wide solution for ordinary reboot behavior is still being investigated.
