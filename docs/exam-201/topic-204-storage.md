# Topic 204: Advanced Storage Administration

Objectives: 204.1, 204.2, and 204.3

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

Failure and replacement lab:

~~~bash
sudo mdadm /dev/md0 --fail /dev/vdb1
sudo mdadm /dev/md0 --remove /dev/vdb1
sudo mdadm /dev/md0 --add /dev/vdd1
watch cat /proc/mdstat
~~~

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

Extend ext4:

~~~bash
sudo lvextend -L +2G /dev/vg_realsam/lv_data
sudo resize2fs /dev/vg_realsam/lv_data
~~~

Grow XFS:

~~~bash
sudo lvextend -L +2G /dev/vg_realsam/lv_xfs
sudo xfs_growfs /srv/xfs
~~~

XFS cannot shrink. For a shrinkable filesystem, reduce the filesystem before the LV and follow its offline procedure.

Snapshots:

~~~bash
sudo lvcreate -L 1G -s -n lv_data_snap /dev/vg_realsam/lv_data
sudo lvs
sudo lvremove /dev/vg_realsam/lv_data_snap
~~~

A full classic snapshot becomes invalid. It is not a backup when stored on the same disks.

~~~bash
sudo vgchange -ay vg_realsam
sudo vgchange -an vg_realsam
~~~

Check mounts before deactivation. LVM configuration is under /etc/lvm/lvm.conf and mappings appear under /dev/mapper/.

## Exam checklist

mdadm.conf, mdadm, /proc/mdstat, partition type 0xFD, hdparm, sdparm, nvme, tune2fs, fstrim, sysctl, iscsiadm, scsi_id, iscsid, iscsid.conf, WWID, WWN, LUN, pv*, vg*, lv*, mount, /dev/mapper/, and lvm.conf.

## Mini lab

Build RAID 1 on empty virtual disks, create LVM on it, create and extend a filesystem, make a snapshot, simulate one failed RAID member, and document recovery.
