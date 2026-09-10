# Apple T2 support

The 2019 Intel MacBook Pro uses the Apple T2 chip for several internal devices, including the keyboard and trackpad.

This Proxmox host uses the standalone t2bce driver.

## Build dependencies

Install:

    apt install build-essential git proxmox-headers-$(uname -r)

## Driver

Repository:

    https://github.com/deqrocks/t2bce.git

Example installation:

    cd /opt
    git clone https://github.com/deqrocks/t2bce.git
    cd t2bce
    make
    make install
    depmod -a

Load the modules:

    modprobe t2bce_dma
    modprobe t2bce_core
    modprobe t2bce_vhci

Persistent module loading is configured in:

    /etc/modules-load.d/t2bce.conf

Then:

    update-initramfs -u

## Verification

    lsmod | grep t2bce

Expected modules include:

    t2bce_dma
    t2bce_core
    t2bce_vhci

t2bce_audio may also load automatically.
