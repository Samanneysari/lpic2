# Topic 202: System Startup

Objectives: 202.1, 202.2, and 202.3

## The boot chain

A normal boot follows this path:

1. BIOS or UEFI initializes hardware.
2. Firmware selects a boot device.
3. A bootloader loads the kernel and initramfs.
4. The kernel initializes CPU, memory, and drivers.
5. Initramfs finds and mounts the real root filesystem.
6. The kernel starts PID 1, normally systemd.
7. systemd reaches the configured target and starts services.

Knowing the stage tells you where to troubleshoot.

## 202.1 Customize system startup

systemd unit locations have different priority:

- /usr/lib/systemd/system/ or /lib/systemd/system/: vendor units
- /run/systemd/system/: runtime units
- /etc/systemd/system/: administrator units and overrides

Do not edit a vendor unit directly. Create an override:

~~~bash
sudo systemctl edit sshd.service
sudo systemctl daemon-reload
systemd-delta
~~~

Useful commands:

~~~bash
systemctl get-default
systemctl set-default multi-user.target
systemctl list-units --type=service
systemctl list-unit-files
systemctl status service
systemctl enable --now service
systemctl disable --now service
systemctl mask service
systemctl cat service
systemctl list-dependencies multi-user.target
~~~

Targets replace the common role of SysV runlevels. rescue.target is similar to single-user maintenance. multi-user.target is a non-graphical multi-user state. graphical.target adds the graphical environment.

SysV knowledge remains in the objectives:

- /etc/inittab
- /etc/init.d/
- /etc/rc.d/
- init and telinit
- chkconfig
- update-rc.d

~~~bash
runlevel
telinit 3
chkconfig --list
update-rc.d service defaults
~~~

Use these only on systems that implement the matching compatibility layer.

## 202.2 System recovery

### GRUB 2

GRUB configuration and command names differ by distribution, but /boot/grub/, /boot/grub2/, and /boot/efi/ are important.

At the GRUB menu, edit a temporary boot entry to:

- select an older kernel
- remove a bad kernel option
- add systemd.unit=rescue.target
- add systemd.unit=emergency.target
- use a distribution recovery option

Temporary edits are lost after reboot.

### Rescue and emergency modes

~~~bash
sudo systemctl rescue
sudo systemctl emergency
~~~

Emergency mode starts fewer services and may mount root read-only. Remount only when needed:

~~~bash
mount -o remount,rw /
~~~

Before running fsck, the target filesystem must be unmounted or mounted read-only. Running a repair against an active writable filesystem can destroy data.

~~~bash
fsck -f /dev/DEVICE
~~~

Use a recovery environment for the root filesystem.

### BIOS, UEFI, and bootloader installation

BIOS systems commonly use boot code in the MBR or a BIOS boot partition. UEFI systems load EFI programs from the EFI System Partition, normally mounted at /boot/efi.

~~~bash
findmnt /boot/efi
efibootmgr -v
ls -R /boot/efi/EFI
~~~

Bootloader installation examples:

~~~bash
sudo grub-install /dev/sdX
sudo grub2-install /dev/sdX
~~~

Do not run these examples without identifying firmware mode, disk, partition layout, and distribution procedure. Installing to the wrong disk can make the system unbootable.

NVMe devices use names such as /dev/nvme0n1 and partitions such as /dev/nvme0n1p1.

### initrd and initramfs

The early userspace image must contain drivers needed to reach root storage, including RAID, LVM, encryption, and filesystems.

~~~bash
lsinitramfs /boot/initrd.img-"$(uname -r)"
lsinitrd /boot/initramfs-"$(uname -r)".img
~~~

If the root device is not found, check kernel command-line UUIDs, storage modules, LVM or RAID assembly, encryption, and initramfs contents.

## 202.3 Alternate bootloaders

Know the purpose of:

- SYSLINUX: boot from FAT filesystems
- EXTLINUX: boot from Linux filesystems
- ISOLINUX: boot ISO media
- PXELINUX: network boot for BIOS clients
- systemd-boot: simple UEFI boot manager
- U-Boot: common on embedded systems
- shim.efi: signed first-stage loader used with Secure Boot
- grubx64.efi: GRUB EFI binary

PXE provides firmware network boot. A BIOS PXE client commonly retrieves pxelinux.0. UEFI clients need an EFI executable. Configuration may be stored under pxelinux.cfg/.

Files and terms include syslinux, extlinux, isolinux.bin, isolinux.cfg, isohdpfx.bin, efiboot.img, pxelinux.0, shim.efi, and grubx64.efi.

## Troubleshooting map

| Failure | Start here |
|---|---|
| No boot device | Firmware order, disk visibility, ESP or boot code |
| GRUB prompt | GRUB files, root prefix, configuration |
| Kernel panic | Kernel option, root device, initramfs, driver |
| Emergency mode | journal, fstab, failed mounts, fsck |
| Service delays | systemd-analyze, critical-chain, unit logs |

~~~bash
systemd-analyze
systemd-analyze blame
systemd-analyze critical-chain
journalctl -b -p warning
journalctl -b -1
~~~

## Mini lab

In a disposable VM, inspect firmware mode, list the ESP or MBR layout, identify the default target, create a harmless service override, boot once into rescue.target, and review the previous boot journal.
