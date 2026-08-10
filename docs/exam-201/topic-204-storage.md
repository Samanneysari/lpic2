# Topic 204: Advanced Storage Administration

Objectives: 204.1, 204.2, and 204.3

<!-- BEGIN BEGINNER FOUNDATION -->
## Learn the idea before running commands

### Why advanced storage uses layers

Advanced storage combines devices to gain redundancy, capacity, flexible allocation, or remote access. Each layer solves a different problem:

- Linux software RAID combines block devices and can survive selected device failures.
- LVM groups storage into physical volumes, volume groups, and logical volumes.
- iSCSI presents remote storage as local SCSI block devices.
- Multipath combines several paths to the same storage device for resilience and load distribution.

These layers may be stacked. For example, two disks can form RAID1, the RAID device can become an LVM physical volume, and logical volumes can contain filesystems. Troubleshooting must follow the layers from the application down to the physical or remote device.

### RAID concepts

RAID0 stripes data and has no redundancy. RAID1 mirrors data. RAID5 and RAID6 use distributed parity, while RAID10 combines mirrors and striping. RAID is not a backup: deletion, corruption, malware, and site loss can affect every member.

A degraded array is still operating without its expected protection. Replace failed members and monitor rebuild progress. Never assemble, create, or zero metadata on uncertain devices.

### LVM concepts

A **physical volume** is storage prepared for LVM. A **volume group** pools one or more physical volumes. A **logical volume** allocates part of that pool as a block device. Extending a logical volume and extending its filesystem are separate operations, even when a convenience option can perform both.

Snapshots use copy-on-write storage and need free extents. They are useful for consistent short-term operations but are not permanent backups.

### Remote and multipath storage

An iSCSI initiator connects to a target and discovers logical units. Authentication, network isolation, persistent naming, and startup ordering matter. Device names such as /dev/sdb can change, so use stable WWIDs, UUIDs, mapper names, or LVM identifiers.

Before any destructive storage command, record the topology with lsblk, blkid, RAID status, LVM reports, and multipath information. Back up important data and test recovery.
<!-- END BEGINNER FOUNDATION -->

> RAID, LVM, format, and encryption commands can destroy data. Use empty virtual disks and verify names with lsblk.

## 204.1 Software RAID

| Level | Minimum | Main property |
|---|---:|---|
| RAID 0 | 2 | Striping, no redundancy |
| RAID 1 | 2 | Mirroring |
| RAID 5 | 3 | Striping with one-device parity tolerance |

RAID is not a backup.

~~~bash
sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/vdb1 /dev/vdc1
watch cat /proc/mdstat
sudo mdadm --detail /dev/md0
sudo mdadm --detail --scan
~~~

<!-- LINE-BY-LINE 1 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/vdb1 /dev/vdc1</code> | sudo requests administrator privileges for this operation. Creates, assembles, inspects, monitors, or changes Linux software RAID. |
| 2 | <code>watch cat /proc/mdstat</code> | Runs the following command repeatedly so changes such as RAID rebuild progress can be observed. |
| 3 | <code>sudo mdadm --detail /dev/md0</code> | sudo requests administrator privileges for this operation. Creates, assembles, inspects, monitors, or changes Linux software RAID. |
| 4 | <code>sudo mdadm --detail --scan</code> | sudo requests administrator privileges for this operation. Creates, assembles, inspects, monitors, or changes Linux software RAID. |

Failure and replacement lab:

~~~bash
sudo mdadm /dev/md0 --fail /dev/vdb1
sudo mdadm /dev/md0 --remove /dev/vdb1
sudo mdadm /dev/md0 --add /dev/vdd1
watch cat /proc/mdstat
~~~

<!-- LINE-BY-LINE 2 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo mdadm /dev/md0 --fail /dev/vdb1</code> | sudo requests administrator privileges for this operation. Creates, assembles, inspects, monitors, or changes Linux software RAID. |
| 2 | <code>sudo mdadm /dev/md0 --remove /dev/vdb1</code> | sudo requests administrator privileges for this operation. Creates, assembles, inspects, monitors, or changes Linux software RAID. |
| 3 | <code>sudo mdadm /dev/md0 --add /dev/vdd1</code> | sudo requests administrator privileges for this operation. Creates, assembles, inspects, monitors, or changes Linux software RAID. |
| 4 | <code>watch cat /proc/mdstat</code> | Runs the following command repeatedly so changes such as RAID rebuild progress can be observed. |

Save assembly information in the distribution mdadm.conf. Older tools used partition type 0xFD for Linux RAID autodetect.

## 204.2 Storage device access

- /dev/hd*: historical IDE
- /dev/sd*: SCSI, SATA, USB, and many virtual disks
- /dev/nvme*: NVMe controllers and namespaces

~~~bash
lsblk -o NAME,MODEL,SERIAL,SIZE,ROTA,TYPE,MOUNTPOINTS
lspci -k
cat /proc/interrupts
sudo hdparm -I /dev/sdX
sudo sdparm --all /dev/sdX
sudo nvme list
sudo nvme smart-log /dev/nvme0
sudo fstrim -av
~~~

<!-- LINE-BY-LINE 3 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>lsblk -o NAME,MODEL,SERIAL,SIZE,ROTA,TYPE,MOUNTPOINTS</code> | Displays block devices and their parent-child relationships. |
| 2 | <code>lspci -k</code> | Lists PCI devices; -k also shows the kernel driver and candidate modules for each device. |
| 3 | <code>cat /proc/interrupts</code> | Prints or combines files; when redirected it can write the shown data to a file. |
| 4 | <code>sudo hdparm -I /dev/sdX</code> | sudo requests administrator privileges for this operation. Queries or changes ATA/SATA device parameters; write options can be risky. |
| 5 | <code>sudo sdparm --all /dev/sdX</code> | sudo requests administrator privileges for this operation. Queries or changes SCSI device parameters. |
| 6 | <code>sudo nvme list</code> | sudo requests administrator privileges for this operation. Queries or manages NVMe devices using the selected subcommand. |
| 7 | <code>sudo nvme smart-log /dev/nvme0</code> | sudo requests administrator privileges for this operation. Queries or manages NVMe devices using the selected subcommand. |
| 8 | <code>sudo fstrim -av</code> | sudo requests administrator privileges for this operation. Discards unused blocks on storage that safely supports trim. |

Do not change device settings until you understand support and persistence. AHCI is a common SATA interface. NVMe uses PCI Express. fstrim reports unused blocks to suitable storage.

### iSCSI and SAN

- target: storage server
- initiator: client
- IQN: iSCSI qualified name
- LUN: logical unit number
- WWN or WWID: stable storage identifier
- SAN: storage area network
- AoE: ATA over Ethernet
- FCoE: Fibre Channel over Ethernet

~~~bash
sudo iscsiadm -m discovery -t sendtargets -p storage.realsam.ir
sudo iscsiadm -m node
sudo iscsiadm -m session
systemctl status iscsid
~~~

<!-- LINE-BY-LINE 4 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo iscsiadm -m discovery -t sendtargets -p storage.realsam.ir</code> | sudo requests administrator privileges for this operation. Discovers and manages iSCSI targets, node records, and sessions. |
| 2 | <code>sudo iscsiadm -m node</code> | sudo requests administrator privileges for this operation. Discovers and manages iSCSI targets, node records, and sessions. |
| 3 | <code>sudo iscsiadm -m session</code> | sudo requests administrator privileges for this operation. Discovers and manages iSCSI targets, node records, and sessions. |
| 4 | <code>systemctl status iscsid</code> | Inspects or changes systemd units, targets, enablement, or system state. |

iscsid.conf controls initiator behavior. scsi_id obtains identifiers. Multipath uses WWIDs to recognize paths to the same LUN.

## 204.3 LVM

LVM layers are physical volume, volume group, and logical volume.

~~~bash
sudo pvcreate /dev/vdb /dev/vdc
sudo vgcreate vg_realsam /dev/vdb /dev/vdc
sudo lvcreate -L 5G -n lv_data vg_realsam
sudo mkfs.ext4 /dev/vg_realsam/lv_data
sudo mount /dev/vg_realsam/lv_data /srv/data
pvs
vgs
lvs -a -o +devices
~~~

<!-- LINE-BY-LINE 5 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo pvcreate /dev/vdb /dev/vdc</code> | sudo requests administrator privileges for this operation. Initializes a device as an LVM physical volume and may overwrite old metadata. |
| 2 | <code>sudo vgcreate vg_realsam /dev/vdb /dev/vdc</code> | sudo requests administrator privileges for this operation. Creates an LVM volume group from the listed physical volumes. |
| 3 | <code>sudo lvcreate -L 5G -n lv_data vg_realsam</code> | sudo requests administrator privileges for this operation. Creates an LVM logical volume or snapshot. |
| 4 | <code>sudo mkfs.ext4 /dev/vg_realsam/lv_data</code> | sudo requests administrator privileges for this operation. Creates a new ext4 filesystem and overwrites existing filesystem metadata on the target. |
| 5 | <code>sudo mount /dev/vg_realsam/lv_data /srv/data</code> | sudo requests administrator privileges for this operation. Attaches a filesystem to the directory tree, remounts it, or displays mount data. |
| 6 | <code>pvs</code> | Reports LVM physical volumes. |
| 7 | <code>vgs</code> | Reports LVM volume groups. |
| 8 | <code>lvs -a -o +devices</code> | Reports LVM logical volumes. |

Extend ext4:

~~~bash
sudo lvextend -L +2G /dev/vg_realsam/lv_data
sudo resize2fs /dev/vg_realsam/lv_data
~~~

<!-- LINE-BY-LINE 6 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo lvextend -L +2G /dev/vg_realsam/lv_data</code> | sudo requests administrator privileges for this operation. Expands a logical volume; the filesystem also needs growth unless the shown option performs both. |
| 2 | <code>sudo resize2fs /dev/vg_realsam/lv_data</code> | sudo requests administrator privileges for this operation. Resizes an ext filesystem after its block device size is correct. |

Grow XFS:

~~~bash
sudo lvextend -L +2G /dev/vg_realsam/lv_xfs
sudo xfs_growfs /srv/xfs
~~~

<!-- LINE-BY-LINE 7 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo lvextend -L +2G /dev/vg_realsam/lv_xfs</code> | sudo requests administrator privileges for this operation. Expands a logical volume; the filesystem also needs growth unless the shown option performs both. |
| 2 | <code>sudo xfs_growfs /srv/xfs</code> | sudo requests administrator privileges for this operation. Grows a mounted XFS filesystem to use available device space. |

XFS cannot shrink. For a shrinkable filesystem, reduce the filesystem before the LV and follow its offline procedure.

Snapshots:

~~~bash
sudo lvcreate -L 1G -s -n lv_data_snap /dev/vg_realsam/lv_data
sudo lvs
sudo lvremove /dev/vg_realsam/lv_data_snap
~~~

<!-- LINE-BY-LINE 8 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo lvcreate -L 1G -s -n lv_data_snap /dev/vg_realsam/lv_data</code> | sudo requests administrator privileges for this operation. Creates an LVM logical volume or snapshot. |
| 2 | <code>sudo lvs</code> | sudo requests administrator privileges for this operation. Reports LVM logical volumes. |
| 3 | <code>sudo lvremove /dev/vg_realsam/lv_data_snap</code> | sudo requests administrator privileges for this operation. Deletes an LVM logical volume after confirmation and destroys access to its data. |

A full classic snapshot becomes invalid. It is not a backup when stored on the same disks.

~~~bash
sudo vgchange -ay vg_realsam
sudo vgchange -an vg_realsam
~~~

<!-- LINE-BY-LINE 9 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo vgchange -ay vg_realsam</code> | sudo requests administrator privileges for this operation. Activates or deactivates volume groups. |
| 2 | <code>sudo vgchange -an vg_realsam</code> | sudo requests administrator privileges for this operation. Activates or deactivates volume groups. |

Check mounts before deactivation. LVM configuration is under /etc/lvm/lvm.conf and mappings appear under /dev/mapper/.

## Exam checklist

mdadm.conf, mdadm, /proc/mdstat, partition type 0xFD, hdparm, sdparm, nvme, tune2fs, fstrim, sysctl, iscsiadm, scsi_id, iscsid, iscsid.conf, WWID, WWN, LUN, pv*, vg*, lv*, mount, /dev/mapper/, and lvm.conf.

## Mini lab

Build RAID 1 on empty virtual disks, create LVM on it, create and extend a filesystem, make a snapshot, simulate one failed RAID member, and document recovery.
