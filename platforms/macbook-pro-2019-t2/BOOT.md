# Boot behavior

## Slow boot caused by unused ZFS import

The host initially took roughly two minutes longer to boot because:

    systemd-udev-settle.service

was being started by:

    zfs-import-cache.service

The journal showed:

    systemd-udev-settle.service is deprecated.
    Please fix zfs-import-cache.service not to pull it in.

The host does not use ZFS:

    zpool status
    no pools available

    zpool list
    no pools available

Both ZFS import services were unnecessary.

The cache import service was disabled:

    systemctl disable zfs-import-cache.service

`zfs-import-scan.service` was already disabled.

After the change:

    systemctl --failed
    0 loaded units listed.

Boot time improved to approximately:

    2.6s kernel + 17.1s userspace = 19.7s total

The remaining largest boot item was:

    ifupdown2-pre.service ~10s
