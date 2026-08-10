# Topic 202: System Startup

Objectives: 202.1, 202.2, and 202.3

<!-- BEGIN BEGINNER FOUNDATION -->
## Learn the idea before running commands

### What happens when Linux starts

Startup is a sequence of separate components. Firmware initializes hardware and selects a boot device. The bootloader loads a Linux kernel and an initial RAM filesystem. The kernel initializes core hardware, mounts the temporary initramfs environment, discovers the real root filesystem, and starts PID 1. On most current distributions PID 1 is systemd, which starts units needed for the selected target.

The initramfs is a small temporary root filesystem. It contains the drivers and tools needed before the normal root filesystem is available, such as storage, RAID, LVM, encryption, or network-root support. A system may fail before reaching the real root filesystem if the initramfs is missing a required driver.

### Bootloader and systemd roles

GRUB 2 chooses the kernel, initramfs, and kernel command line. Its generated configuration should normally be changed through distribution-supported source files and regeneration tools, not edited blindly.

Systemd expresses work as units. Service units start daemons, socket units can activate services on demand, mount units represent filesystems, and target units group other units. Dependencies and ordering are separate ideas: Requires= describes a dependency relationship, while After= describes ordering.

### Runlevels and targets

Traditional SysV init uses numbered runlevels and scripts under /etc/init.d. Systemd uses targets such as multi-user.target and graphical.target, while providing compatibility mappings for common runlevels. The exam expects knowledge of both models because older systems and scripts still exist.

### Safe diagnosis and recovery

1. Identify the last successful startup stage.
2. Read the current boot journal and failed units.
3. Validate configuration before enabling or restarting a service.
4. Use rescue or emergency targets only with console access.
5. Remount filesystems and change passwords only when you understand the security and recovery impact.
6. Fix the cause, restore the normal target, and verify a complete reboot.

A boot delay is not always a bootloader problem. It may be a missing device in /etc/fstab, a network-online dependency, a failed filesystem check, a slow DNS lookup, or a service timeout.
<!-- END BEGINNER FOUNDATION -->

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

<!-- LINE-BY-LINE 1 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo systemctl edit sshd.service</code> | sudo requests administrator privileges for this operation. Inspects or changes systemd units, targets, enablement, or system state. |
| 2 | <code>sudo systemctl daemon-reload</code> | sudo requests administrator privileges for this operation. Inspects or changes systemd units, targets, enablement, or system state. |
| 3 | <code>systemd-delta</code> | Shows local systemd overrides that differ from packaged unit files. |

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

<!-- LINE-BY-LINE 2 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>systemctl get-default</code> | Inspects or changes systemd units, targets, enablement, or system state. |
| 2 | <code>systemctl set-default multi-user.target</code> | Inspects or changes systemd units, targets, enablement, or system state. |
| 3 | <code>systemctl list-units --type=service</code> | Inspects or changes systemd units, targets, enablement, or system state. |
| 4 | <code>systemctl list-unit-files</code> | Inspects or changes systemd units, targets, enablement, or system state. |
| 5 | <code>systemctl status service</code> | Inspects or changes systemd units, targets, enablement, or system state. |
| 6 | <code>systemctl enable --now service</code> | Inspects or changes systemd units, targets, enablement, or system state. |
| 7 | <code>systemctl disable --now service</code> | Inspects or changes systemd units, targets, enablement, or system state. |
| 8 | <code>systemctl mask service</code> | Inspects or changes systemd units, targets, enablement, or system state. |
| 9 | <code>systemctl cat service</code> | Inspects or changes systemd units, targets, enablement, or system state. |
| 10 | <code>systemctl list-dependencies multi-user.target</code> | Inspects or changes systemd units, targets, enablement, or system state. |

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

<!-- LINE-BY-LINE 3 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>runlevel</code> | Shows the previous and current SysV runlevel where compatibility support exists. |
| 2 | <code>telinit 3</code> | Requests a SysV runlevel change or init control action. |
| 3 | <code>chkconfig --list</code> | Displays or changes SysV service enablement on older RHEL-family systems. |
| 4 | <code>update-rc.d service defaults</code> | Manages SysV startup links on Debian-family systems. |

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

<!-- LINE-BY-LINE 4 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo systemctl rescue</code> | sudo requests administrator privileges for this operation. Inspects or changes systemd units, targets, enablement, or system state. |
| 2 | <code>sudo systemctl emergency</code> | sudo requests administrator privileges for this operation. Inspects or changes systemd units, targets, enablement, or system state. |

Emergency mode starts fewer services and may mount root read-only. Remount only when needed:

~~~bash
mount -o remount,rw /
~~~

<!-- LINE-BY-LINE 5 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>mount -o remount,rw /</code> | Attaches a filesystem to the directory tree, remounts it, or displays mount data. |

Before running fsck, the target filesystem must be unmounted or mounted read-only. Running a repair against an active writable filesystem can destroy data.

~~~bash
fsck -f /dev/DEVICE
~~~

<!-- LINE-BY-LINE 6 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>fsck -f /dev/DEVICE</code> | Checks filesystems according to the shown target or fstab policy. |

Use a recovery environment for the root filesystem.

### BIOS, UEFI, and bootloader installation

BIOS systems commonly use boot code in the MBR or a BIOS boot partition. UEFI systems load EFI programs from the EFI System Partition, normally mounted at /boot/efi.

~~~bash
findmnt /boot/efi
efibootmgr -v
ls -R /boot/efi/EFI
~~~

<!-- LINE-BY-LINE 7 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>findmnt /boot/efi</code> | Displays mounts or validates fstab and mount relationships. |
| 2 | <code>efibootmgr -v</code> | Displays or edits UEFI firmware boot entries. |
| 3 | <code>ls -R /boot/efi/EFI</code> | Lists the requested files and metadata. |

Bootloader installation examples:

~~~bash
sudo grub-install /dev/sdX
sudo grub2-install /dev/sdX
~~~

<!-- LINE-BY-LINE 8 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo grub-install /dev/sdX</code> | sudo requests administrator privileges for this operation. Installs GRUB boot code and support files for the selected platform. |
| 2 | <code>sudo grub2-install /dev/sdX</code> | sudo requests administrator privileges for this operation. Installs GRUB 2 boot code and support files on distributions using this name. |

Do not run these examples without identifying firmware mode, disk, partition layout, and distribution procedure. Installing to the wrong disk can make the system unbootable.

NVMe devices use names such as /dev/nvme0n1 and partitions such as /dev/nvme0n1p1.

### initrd and initramfs

The early userspace image must contain drivers needed to reach root storage, including RAID, LVM, encryption, and filesystems.

~~~bash
lsinitramfs /boot/initrd.img-"$(uname -r)"
lsinitrd /boot/initramfs-"$(uname -r)".img
~~~

<!-- LINE-BY-LINE 9 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>lsinitramfs /boot/initrd.img-"$(uname -r)"</code> | Lists files inside an initramfs image on Debian-family systems. |
| 2 | <code>lsinitrd /boot/initramfs-"$(uname -r)".img</code> | Lists files inside an initramfs image on RHEL-family systems. |

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

<!-- LINE-BY-LINE 10 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>systemd-analyze</code> | Measures boot performance or displays the dependency critical path. |
| 2 | <code>systemd-analyze blame</code> | Measures boot performance or displays the dependency critical path. |
| 3 | <code>systemd-analyze critical-chain</code> | Measures boot performance or displays the dependency critical path. |
| 4 | <code>journalctl -b -p warning</code> | Reads structured systemd journal records with the shown unit or time filter. |
| 5 | <code>journalctl -b -1</code> | Reads structured systemd journal records with the shown unit or time filter. |

## Mini lab

In a disposable VM, inspect firmware mode, list the ESP or MBR layout, identify the default target, create a harmless service override, boot once into rescue.target, and review the previous boot journal.
