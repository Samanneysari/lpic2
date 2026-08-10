# Topic 206: System Maintenance

Objectives: 206.1, 206.2, and 206.3

<!-- BEGIN BEGINNER FOUNDATION -->
## Learn the idea before running commands

### What system maintenance includes

System maintenance keeps a server supportable through controlled software installation, backups, user communication, and recovery. The exam includes source-code builds because administrators sometimes need software that is unavailable as a package. In production, a maintained distribution package is usually easier to update, audit, and remove.

A typical source build has four phases: inspect documentation, configure build options, compile, and install. Build as an unprivileged user. Use elevated privileges only for the final controlled installation, preferably through a package-building or staged-install method so every installed file can be tracked.

### Backups are a recovery system

A command that copies files is not by itself a backup strategy. Define what is protected, how often it changes, how long versions are retained, where copies are stored, how encryption keys are protected, and how restoration is tested.

A useful backup design follows the 3-2-1 idea: multiple copies, more than one storage type, and one copy separated from the main system. Database and application consistency may require snapshots, dumps, or application-aware hooks.

### Planned maintenance

Before maintenance:

1. describe the change and risk;
2. confirm console or recovery access;
3. create and verify a backup;
4. notify affected users;
5. record the current versions and service state;
6. prepare a rollback procedure.

During maintenance, make one controlled change at a time and keep timestamps. Afterward, validate service health, logs, ports, application behavior, monitoring, and backups.

### Recovery thinking

Recovery begins by identifying whether the failure is in firmware, bootloader, kernel/initramfs, root filesystem, systemd, networking, or the application. Rescue media and chroot environments can repair an installed system, but mounted filesystems, pseudo-filesystems, DNS, and boot mode must be handled correctly.

Never test the only copy of a backup by overwriting the live system. Restore into an isolated location first and compare the result.
<!-- END BEGINNER FOUNDATION -->

## 206.1 Build from source

Prefer trusted packages when possible. Read README and INSTALL first.

~~~bash
tar -xf source.tar
tar -xzf source.tar.gz
tar -xjf source.tar.bz2
tar -xJf source.tar.xz
gunzip file.gz
~~~

<!-- LINE-BY-LINE 1 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>tar -xf source.tar</code> | Creates, lists, or extracts an archive with the shown compression and path options. |
| 2 | <code>tar -xzf source.tar.gz</code> | Creates, lists, or extracts an archive with the shown compression and path options. |
| 3 | <code>tar -xjf source.tar.bz2</code> | Creates, lists, or extracts an archive with the shown compression and path options. |
| 4 | <code>tar -xJf source.tar.xz</code> | Creates, lists, or extracts an archive with the shown compression and path options. |
| 5 | <code>gunzip file.gz</code> | Decompresses a gzip-compressed file. |

Traditional build:

~~~bash
tar -xJf program-1.0.tar.xz
cd program-1.0
./configure --prefix=/usr/local
make
make check
sudo make install
~~~

<!-- LINE-BY-LINE 2 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>tar -xJf program-1.0.tar.xz</code> | Creates, lists, or extracts an archive with the shown compression and path options. |
| 2 | <code>cd program-1.0</code> | Changes the shell's working directory. |
| 3 | <code>./configure --prefix=/usr/local</code> | Checks build dependencies and prepares project-specific Makefiles using the shown options. |
| 4 | <code>make</code> | Runs a target from the project's Makefile, such as compilation, installation, or cleanup. |
| 5 | <code>make check</code> | Runs a target from the project's Makefile, such as compilation, installation, or cleanup. |
| 6 | <code>sudo make install</code> | sudo requests administrator privileges for this operation. Runs a target from the project's Makefile, such as compilation, installation, or cleanup. |

/usr/src is a traditional source location. /usr/local keeps local software separate from distribution files.

~~~bash
uname -m
./configure --help
make -j"$(nproc)"
sudo install -m 0755 program /usr/local/bin/program
patch -p1 < fix.patch
~~~

<!-- LINE-BY-LINE 3 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>uname -m</code> | Prints kernel release, architecture, or other system identity data. |
| 2 | <code>./configure --help</code> | Checks build dependencies and prepares project-specific Makefiles using the shown options. |
| 3 | <code>make -j"$(nproc)"</code> | Runs a target from the project's Makefile, such as compilation, installation, or cleanup. |
| 4 | <code>sudo install -m 0755 program /usr/local/bin/program</code> | sudo requests administrator privileges for this operation. Creates a file or directory with explicit owner, group, and permission mode. |
| 5 | <code>patch -p1 < fix.patch</code> | Applies a unified or context diff to a source tree. |

Verify upstream signatures or checksums. Record version, URL, options, installed files, and uninstall steps.

## 206.2 Backups

A plan defines scope, frequency, retention, encryption, off-site copies, integrity, and restoration. Protect /etc, application and user data, databases, keys, automation, and package lists. Exclude pseudo-filesystems such as /proc, /sys, /run, and /dev from ordinary file backup.

### tar

~~~bash
sudo tar --one-file-system -czpf etc-backup.tar.gz /etc
tar -tzf etc-backup.tar.gz
sudo tar -xzpf etc-backup.tar.gz -C /restore
~~~

<!-- LINE-BY-LINE 4 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo tar --one-file-system -czpf etc-backup.tar.gz /etc</code> | sudo requests administrator privileges for this operation. Creates, lists, or extracts an archive with the shown compression and path options. |
| 2 | <code>tar -tzf etc-backup.tar.gz</code> | Creates, lists, or extracts an archive with the shown compression and path options. |
| 3 | <code>sudo tar -xzpf etc-backup.tar.gz -C /restore</code> | sudo requests administrator privileges for this operation. Creates, lists, or extracts an archive with the shown compression and path options. |

### rsync

~~~bash
sudo rsync -aHAX --numeric-ids /srv/data/ /backup/data/
sudo rsync -aHAXn --delete /srv/data/ /backup/data/
~~~

<!-- LINE-BY-LINE 5 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo rsync -aHAX --numeric-ids /srv/data/ /backup/data/</code> | sudo requests administrator privileges for this operation. Synchronizes file trees while preserving the selected metadata. |
| 2 | <code>sudo rsync -aHAXn --delete /srv/data/ /backup/data/</code> | sudo requests administrator privileges for this operation. Synchronizes file trees while preserving the selected metadata. |

The trailing slash matters. Preview destructive options with -n.

### dd

~~~bash
sudo dd if=/dev/DEVICE of=/backup/device.img bs=4M status=progress conv=fsync
sha256sum /backup/device.img
~~~

<!-- LINE-BY-LINE 6 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo dd if=/dev/DEVICE of=/backup/device.img bs=4M status=progress conv=fsync</code> | sudo requests administrator privileges for this operation. Copies blocks between the selected input and output; a wrong output target can destroy data. |
| 2 | <code>sha256sum /backup/device.img</code> | Calculates or checks a SHA-256 digest so a download can be verified. |

Reversing if and of destroys the source.

Tape devices include /dev/st* and /dev/nst*. mt controls tape position:

~~~bash
mt -f /dev/nst0 status
~~~

<!-- LINE-BY-LINE 7 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>mt -f /dev/nst0 status</code> | Controls a tape device, such as rewind, status, or file positioning. |

Network backup products named by the objectives include Amanda, Bacula, Bareos, and BackupPC.

A live database needs an application-consistent dump, snapshot, or backup API. A backup is not proven until a restore succeeds.

~~~bash
sha256sum backup-file
tar -tf archive.tar
~~~

<!-- LINE-BY-LINE 8 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sha256sum backup-file</code> | Calculates or checks a SHA-256 digest so a download can be verified. |
| 2 | <code>tar -tf archive.tar</code> | Creates, lists, or extracts an archive with the shown compression and path options. |

## 206.3 Notify users

- /etc/issue: local pre-login message
- /etc/issue.net: network pre-login message when supported
- /etc/motd: post-login message
- wall: message to active terminals

~~~bash
echo "Maintenance starts at 22:00 UTC." | sudo wall
sudo shutdown -r +30 "Kernel maintenance; save your work"
sudo systemctl reboot
~~~

<!-- LINE-BY-LINE 9 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>echo "Maintenance starts at 22:00 UTC." \| sudo wall</code> | Writes the shown text; redirection may send it to a device or file. The pipe sends standard output from the command on the left to standard input of the command on the right. |
| 2 | <code>sudo shutdown -r +30 "Kernel maintenance; save your work"</code> | sudo requests administrator privileges for this operation. Schedules a controlled shutdown or reboot and can notify users. |
| 3 | <code>sudo systemctl reboot</code> | sudo requests administrator privileges for this operation. Inspects or changes systemd units, targets, enablement, or system state. |

A notice should state affected service, start, duration, user action, contact, and completion. Do not expose sensitive system details in a public banner.

## Exam checklist

/usr/src, gunzip, gzip, bzip2, xz, tar, configure, make, uname, install, patch, /bin/sh, dd, /dev/st*, /dev/nst*, mt, rsync, /etc/issue, /etc/issue.net, /etc/motd, wall, shutdown, and systemctl.

## Mini lab

Build a small trusted program in /usr/local. Back up a test directory with tar and rsync, verify checksums, restore into a new path, and send a notice to another test session.
