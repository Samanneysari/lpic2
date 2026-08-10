# Topic 203: Filesystems and Devices

Objectives: 203.1, 203.2, and 203.3

A block device stores blocks. A filesystem organizes those blocks into files, directories, metadata, permissions, and free space.

## 203.1 Operate the Linux filesystem

### Mounts and fstab

~~~bash
lsblk -f
blkid
findmnt
mount
cat /proc/mounts
~~~

/etc/mtab may link to /proc/self/mounts. The kernel view in /proc/mounts is more reliable than assuming mtab is a separate file.

An /etc/fstab line has six fields:

~~~text
UUID=1111-2222  /srv/data  ext4  defaults,noatime  0  2
~~~

1. device, label, UUID, or network source
2. mount point
3. filesystem type
4. options
5. dump flag
6. fsck order

Use UUIDs because device names can change. Test fstab without rebooting:

~~~bash
sudo findmnt --verify
sudo mount -a
~~~

A bad entry can delay boot. Options such as nofail, _netdev, x-systemd.automount, and x-systemd.device-timeout may be appropriate.

### systemd mount units

/srv/data becomes srv-data.mount.

~~~bash
systemctl status srv-data.mount
systemd-escape -p --suffix=mount /srv/data
~~~

systemd can generate units from fstab or use administrator-written .mount and .automount units.

### Swap

~~~bash
swapon --show
free -h
sudo mkswap /dev/DEVICE
sudo swapon /dev/DEVICE
sudo swapoff /dev/DEVICE
~~~

Swap-file example:

~~~bash
sudo fallocate -l 2G /swapfile
sudo chmod 0600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
~~~

Some filesystems need a different swap-file procedure. sync flushes buffered writes; it is not a backup.

## 203.2 Maintain filesystems

Never repair a mounted writable filesystem.

### ext2, ext3, and ext4

~~~bash
sudo mkfs.ext4 /dev/DEVICE
sudo fsck.ext4 -f /dev/DEVICE
sudo tune2fs -l /dev/DEVICE
sudo dumpe2fs -h /dev/DEVICE
sudo debugfs /dev/DEVICE
~~~

debugfs can damage data; use read-only operation unless a tested recovery requires a write.

### XFS

~~~bash
sudo mkfs.xfs /dev/DEVICE
xfs_info /mountpoint
sudo xfs_repair -n /dev/DEVICE
sudo xfsdump -f backup.xfs /mountpoint
sudo xfsrestore -f backup.xfs /restore
~~~

XFS can grow while mounted but cannot shrink. xfs_check is an older exam term and is obsolete on many current systems.

### Btrfs

~~~bash
sudo btrfs filesystem show
sudo btrfs subvolume list /srv
sudo btrfs subvolume create /srv/app
sudo btrfs subvolume snapshot -r /srv/app /srv/snapshots/app-001
sudo btrfs filesystem usage /srv
sudo btrfs scrub start -Bd /srv
~~~

A snapshot on the same storage is not a separate backup. btrfs-convert must be tested and backed up first. ZFS awareness includes pools, datasets, checksums, snapshots, and copy-on-write.

### SMART

~~~bash
sudo smartctl -a /dev/sdX
sudo smartctl -t short /dev/sdX
sudo smartctl -l selftest /dev/sdX
systemctl status smartd
~~~

Replace failing storage and restore redundancy before experimenting.

## 203.3 Filesystem options

### AutoFS

/etc/auto.master:

~~~text
/srv/auto  /etc/auto.realsam  --timeout=60
~~~

/etc/auto.realsam:

~~~text
files  -fstype=nfs4,rw  files.realsam.ir:/exports/team
~~~

~~~bash
sudo automount -m
sudo systemctl reload autofs
~~~

### Optical images

ISO9660 is common for CD images. UDF supports newer optical media. HFS, Joliet, Rock Ridge, and El Torito are awareness terms.

~~~bash
mkisofs -o realsam-tools.iso directory/
sudo mount -o loop,ro realsam-tools.iso /mnt/iso
~~~

### LUKS and dm-crypt

~~~bash
sudo cryptsetup luksFormat /dev/DEVICE
sudo cryptsetup open /dev/DEVICE realsam_secure
sudo mkfs.ext4 /dev/mapper/realsam_secure
sudo cryptsetup close realsam_secure
~~~

These commands alter data. Use an empty lab device. Back up the LUKS header and protect recovery keys.

## Exam checklist

/etc/fstab, /etc/mtab, /proc/mounts, mount, umount, blkid, sync, swapon, swapoff, mkfs, mkswap, fsck, tune2fs, dumpe2fs, debugfs, btrfs, btrfs-convert, xfs_info, xfs_check, xfs_repair, xfsdump, xfsrestore, smartd, smartctl, /etc/auto.master, mkisofs, and cryptsetup.

## Mini lab

Attach an empty virtual disk. Create a filesystem, mount it by UUID, validate fstab, create and remove a swap file, inspect SMART data, configure AutoFS, and use another disposable device for LUKS.
