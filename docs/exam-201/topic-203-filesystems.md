# Topic 203: Filesystems and Devices

Objectives: 203.1, 203.2, and 203.3

<!-- BEGIN BEGINNER FOUNDATION -->
## Learn the idea before running commands

### From a disk to a usable directory

Linux storage is built in layers. A physical or virtual block device can contain a partition table. A partition or logical volume can contain a filesystem. The filesystem is attached to the single Linux directory tree at a **mount point**. Applications then access files through normal paths without needing to know which device holds them.

A filesystem stores file data plus metadata such as owners, permissions, timestamps, and allocation information. In inode-based filesystems, a directory maps a name to an inode. A hard link is another name for the same inode. A symbolic link is a separate file containing a path.

### Mounting and /etc/fstab

A manual mount lasts until unmount or reboot. /etc/fstab describes filesystems that should be mounted automatically. Its six fields are:

1. device identifier, preferably a UUID or label;
2. mount point;
3. filesystem type;
4. comma-separated mount options;
5. dump backup flag;
6. filesystem-check order.

An incorrect fstab entry can delay or stop startup. Create the mount point, validate the line with findmnt --verify, and test with mount -a before rebooting.

### Filesystem creation and repair

Creating a filesystem destroys the previous filesystem metadata on the selected device. Always verify the exact device with lsblk, blkid, and the storage design before using any mkfs command. Repair tools should normally run on an unmounted filesystem. XFS and ext filesystems use different creation, inspection, growth, and repair tools.

### Space, inodes, and quotas

A filesystem can run out of data blocks or inodes. The df -h command measures space; df -i measures inode use. Quotas limit usage by user, group, or project. Permissions decide whether access is allowed; quotas decide how much storage may be consumed. These are different controls.

Use mount options such as nodev, nosuid, and noexec only after checking application needs. They reduce risk but can break software that legitimately requires the blocked behavior.
<!-- END BEGINNER FOUNDATION -->

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

<!-- LINE-BY-LINE 1 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>lsblk -f</code> | Displays block devices and their parent-child relationships. |
| 2 | <code>blkid</code> | Prints stable block identifiers such as UUID, label, and filesystem type. |
| 3 | <code>findmnt</code> | Displays mounts or validates fstab and mount relationships. |
| 4 | <code>mount</code> | Attaches a filesystem to the directory tree, remounts it, or displays mount data. |
| 5 | <code>cat /proc/mounts</code> | Prints or combines files; when redirected it can write the shown data to a file. |

/etc/mtab may link to /proc/self/mounts. The kernel view in /proc/mounts is more reliable than assuming mtab is a separate file.

An /etc/fstab line has six fields:

~~~text
UUID=1111-2222  /srv/data  ext4  defaults,noatime  0  2
~~~

<!-- LINE-BY-LINE 2 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>UUID=1111-2222  /srv/data  ext4  defaults,noatime  0  2</code> | Defines an fstab mount using a stable UUID, followed by mount point, filesystem type, options, dump flag, and check order. |

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

<!-- LINE-BY-LINE 3 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo findmnt --verify</code> | sudo requests administrator privileges for this operation. Displays mounts or validates fstab and mount relationships. |
| 2 | <code>sudo mount -a</code> | sudo requests administrator privileges for this operation. Attaches a filesystem to the directory tree, remounts it, or displays mount data. |

A bad entry can delay boot. Options such as nofail, _netdev, x-systemd.automount, and x-systemd.device-timeout may be appropriate.

### systemd mount units

/srv/data becomes srv-data.mount.

~~~bash
systemctl status srv-data.mount
systemd-escape -p --suffix=mount /srv/data
~~~

<!-- LINE-BY-LINE 4 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>systemctl status srv-data.mount</code> | Inspects or changes systemd units, targets, enablement, or system state. |
| 2 | <code>systemd-escape -p --suffix=mount /srv/data</code> | Converts a path or name into a valid systemd unit name. |

systemd can generate units from fstab or use administrator-written .mount and .automount units.

### Swap

~~~bash
swapon --show
free -h
sudo mkswap /dev/DEVICE
sudo swapon /dev/DEVICE
sudo swapoff /dev/DEVICE
~~~

<!-- LINE-BY-LINE 5 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>swapon --show</code> | Enables swap or reports active swap areas. |
| 2 | <code>free -h</code> | Reports RAM and swap use; human-readable output is requested where shown. |
| 3 | <code>sudo mkswap /dev/DEVICE</code> | sudo requests administrator privileges for this operation. Writes swap-area metadata to the selected device or file. |
| 4 | <code>sudo swapon /dev/DEVICE</code> | sudo requests administrator privileges for this operation. Enables swap or reports active swap areas. |
| 5 | <code>sudo swapoff /dev/DEVICE</code> | sudo requests administrator privileges for this operation. Disables the selected swap area after pages are moved elsewhere. |

Swap-file example:

~~~bash
sudo fallocate -l 2G /swapfile
sudo chmod 0600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
~~~

<!-- LINE-BY-LINE 6 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo fallocate -l 2G /swapfile</code> | sudo requests administrator privileges for this operation. Allocates space for a file efficiently, here for a swap file. |
| 2 | <code>sudo chmod 0600 /swapfile</code> | sudo requests administrator privileges for this operation. Changes permission bits; verify the exact path before recursive use. |
| 3 | <code>sudo mkswap /swapfile</code> | sudo requests administrator privileges for this operation. Writes swap-area metadata to the selected device or file. |
| 4 | <code>sudo swapon /swapfile</code> | sudo requests administrator privileges for this operation. Enables swap or reports active swap areas. |

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

<!-- LINE-BY-LINE 7 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo mkfs.ext4 /dev/DEVICE</code> | sudo requests administrator privileges for this operation. Creates a new ext4 filesystem and overwrites existing filesystem metadata on the target. |
| 2 | <code>sudo fsck.ext4 -f /dev/DEVICE</code> | sudo requests administrator privileges for this operation. Checks or repairs an unmounted ext4 filesystem. |
| 3 | <code>sudo tune2fs -l /dev/DEVICE</code> | sudo requests administrator privileges for this operation. Displays or changes ext filesystem parameters. |
| 4 | <code>sudo dumpe2fs -h /dev/DEVICE</code> | sudo requests administrator privileges for this operation. Prints ext filesystem superblock and block-group information. |
| 5 | <code>sudo debugfs /dev/DEVICE</code> | sudo requests administrator privileges for this operation. Opens the ext filesystem debugger; write mode can damage data. |

debugfs can damage data; use read-only operation unless a tested recovery requires a write.

### XFS

~~~bash
sudo mkfs.xfs /dev/DEVICE
xfs_info /mountpoint
sudo xfs_repair -n /dev/DEVICE
sudo xfsdump -f backup.xfs /mountpoint
sudo xfsrestore -f backup.xfs /restore
~~~

<!-- LINE-BY-LINE 8 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo mkfs.xfs /dev/DEVICE</code> | sudo requests administrator privileges for this operation. Creates a new XFS filesystem and overwrites existing filesystem metadata on the target. |
| 2 | <code>xfs_info /mountpoint</code> | Shows the geometry and enabled features of an XFS filesystem. |
| 3 | <code>sudo xfs_repair -n /dev/DEVICE</code> | sudo requests administrator privileges for this operation. Checks or repairs an unmounted XFS filesystem. |
| 4 | <code>sudo xfsdump -f backup.xfs /mountpoint</code> | sudo requests administrator privileges for this operation. Creates an XFS-aware backup stream. |
| 5 | <code>sudo xfsrestore -f backup.xfs /restore</code> | sudo requests administrator privileges for this operation. Restores files from an xfsdump stream. |

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

<!-- LINE-BY-LINE 9 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo btrfs filesystem show</code> | sudo requests administrator privileges for this operation. Runs the selected Btrfs filesystem, subvolume, balance, scrub, or device operation. |
| 2 | <code>sudo btrfs subvolume list /srv</code> | sudo requests administrator privileges for this operation. Runs the selected Btrfs filesystem, subvolume, balance, scrub, or device operation. |
| 3 | <code>sudo btrfs subvolume create /srv/app</code> | sudo requests administrator privileges for this operation. Runs the selected Btrfs filesystem, subvolume, balance, scrub, or device operation. |
| 4 | <code>sudo btrfs subvolume snapshot -r /srv/app /srv/snapshots/app-001</code> | sudo requests administrator privileges for this operation. Runs the selected Btrfs filesystem, subvolume, balance, scrub, or device operation. |
| 5 | <code>sudo btrfs filesystem usage /srv</code> | sudo requests administrator privileges for this operation. Runs the selected Btrfs filesystem, subvolume, balance, scrub, or device operation. |
| 6 | <code>sudo btrfs scrub start -Bd /srv</code> | sudo requests administrator privileges for this operation. Runs the selected Btrfs filesystem, subvolume, balance, scrub, or device operation. |

A snapshot on the same storage is not a separate backup. btrfs-convert must be tested and backed up first. ZFS awareness includes pools, datasets, checksums, snapshots, and copy-on-write.

### SMART

~~~bash
sudo smartctl -a /dev/sdX
sudo smartctl -t short /dev/sdX
sudo smartctl -l selftest /dev/sdX
systemctl status smartd
~~~

<!-- LINE-BY-LINE 10 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo smartctl -a /dev/sdX</code> | sudo requests administrator privileges for this operation. Reads SMART identity, health, attributes, logs, or test results. |
| 2 | <code>sudo smartctl -t short /dev/sdX</code> | sudo requests administrator privileges for this operation. Reads SMART identity, health, attributes, logs, or test results. |
| 3 | <code>sudo smartctl -l selftest /dev/sdX</code> | sudo requests administrator privileges for this operation. Reads SMART identity, health, attributes, logs, or test results. |
| 4 | <code>systemctl status smartd</code> | Inspects or changes systemd units, targets, enablement, or system state. |

Replace failing storage and restore redundancy before experimenting.

## 203.3 Filesystem options

### AutoFS

/etc/auto.master:

~~~text
/srv/auto  /etc/auto.realsam  --timeout=60
~~~

<!-- LINE-BY-LINE 11 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>/srv/auto  /etc/auto.realsam  --timeout=60</code> | Maps the /srv/auto autofs mount point to the named indirect map and sets the idle timeout. |

/etc/auto.realsam:

~~~text
files  -fstype=nfs4,rw  files.realsam.ir:/exports/team
~~~

<!-- LINE-BY-LINE 12 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>files  -fstype=nfs4,rw  files.realsam.ir:/exports/team</code> | Defines the autofs key files, requests an NFSv4 read-write mount, and names the remote export. |

~~~bash
sudo automount -m
sudo systemctl reload autofs
~~~

<!-- LINE-BY-LINE 13 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo automount -m</code> | sudo requests administrator privileges for this operation. Runs the automounter or validates an autofs map according to the shown options. |
| 2 | <code>sudo systemctl reload autofs</code> | sudo requests administrator privileges for this operation. Inspects or changes systemd units, targets, enablement, or system state. |

### Optical images

ISO9660 is common for CD images. UDF supports newer optical media. HFS, Joliet, Rock Ridge, and El Torito are awareness terms.

~~~bash
mkisofs -o realsam-tools.iso directory/
sudo mount -o loop,ro realsam-tools.iso /mnt/iso
~~~

<!-- LINE-BY-LINE 14 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>mkisofs -o realsam-tools.iso directory/</code> | Builds an ISO 9660 filesystem image from a directory tree. |
| 2 | <code>sudo mount -o loop,ro realsam-tools.iso /mnt/iso</code> | sudo requests administrator privileges for this operation. Attaches a filesystem to the directory tree, remounts it, or displays mount data. |

### LUKS and dm-crypt

~~~bash
sudo cryptsetup luksFormat /dev/DEVICE
sudo cryptsetup open /dev/DEVICE realsam_secure
sudo mkfs.ext4 /dev/mapper/realsam_secure
sudo cryptsetup close realsam_secure
~~~

<!-- LINE-BY-LINE 15 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo cryptsetup luksFormat /dev/DEVICE</code> | sudo requests administrator privileges for this operation. Creates, opens, closes, or inspects encrypted block-device mappings. |
| 2 | <code>sudo cryptsetup open /dev/DEVICE realsam_secure</code> | sudo requests administrator privileges for this operation. Creates, opens, closes, or inspects encrypted block-device mappings. |
| 3 | <code>sudo mkfs.ext4 /dev/mapper/realsam_secure</code> | sudo requests administrator privileges for this operation. Creates a new ext4 filesystem and overwrites existing filesystem metadata on the target. |
| 4 | <code>sudo cryptsetup close realsam_secure</code> | sudo requests administrator privileges for this operation. Creates, opens, closes, or inspects encrypted block-device mappings. |

These commands alter data. Use an empty lab device. Back up the LUKS header and protect recovery keys.

## Exam checklist

/etc/fstab, /etc/mtab, /proc/mounts, mount, umount, blkid, sync, swapon, swapoff, mkfs, mkswap, fsck, tune2fs, dumpe2fs, debugfs, btrfs, btrfs-convert, xfs_info, xfs_check, xfs_repair, xfsdump, xfsrestore, smartd, smartctl, /etc/auto.master, mkisofs, and cryptsetup.

## Mini lab

Attach an empty virtual disk. Create a filesystem, mount it by UUID, validate fstab, create and remove a swap file, inspect SMART data, configure AutoFS, and use another disposable device for LUKS.
