# Topic 206: System Maintenance

Objectives: 206.1, 206.2, and 206.3

## 206.1 Build from source

Prefer trusted packages when possible. Read README and INSTALL first.

~~~bash
tar -xf source.tar
tar -xzf source.tar.gz
tar -xjf source.tar.bz2
tar -xJf source.tar.xz
gunzip file.gz
~~~

Traditional build:

~~~bash
tar -xJf program-1.0.tar.xz
cd program-1.0
./configure --prefix=/usr/local
make
make check
sudo make install
~~~

/usr/src is a traditional source location. /usr/local keeps local software separate from distribution files.

~~~bash
uname -m
./configure --help
make -j"$(nproc)"
sudo install -m 0755 program /usr/local/bin/program
patch -p1 < fix.patch
~~~

Verify upstream signatures or checksums. Record version, URL, options, installed files, and uninstall steps.

## 206.2 Backups

A plan defines scope, frequency, retention, encryption, off-site copies, integrity, and restoration. Protect /etc, application and user data, databases, keys, automation, and package lists. Exclude pseudo-filesystems such as /proc, /sys, /run, and /dev from ordinary file backup.

### tar

~~~bash
sudo tar --one-file-system -czpf etc-backup.tar.gz /etc
tar -tzf etc-backup.tar.gz
sudo tar -xzpf etc-backup.tar.gz -C /restore
~~~

### rsync

~~~bash
sudo rsync -aHAX --numeric-ids /srv/data/ /backup/data/
sudo rsync -aHAXn --delete /srv/data/ /backup/data/
~~~

The trailing slash matters. Preview destructive options with -n.

### dd

~~~bash
sudo dd if=/dev/DEVICE of=/backup/device.img bs=4M status=progress conv=fsync
sha256sum /backup/device.img
~~~

Reversing if and of destroys the source.

Tape devices include /dev/st* and /dev/nst*. mt controls tape position:

~~~bash
mt -f /dev/nst0 status
~~~

Network backup products named by the objectives include Amanda, Bacula, Bareos, and BackupPC.

A live database needs an application-consistent dump, snapshot, or backup API. A backup is not proven until a restore succeeds.

~~~bash
sha256sum backup-file
tar -tf archive.tar
~~~

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

A notice should state affected service, start, duration, user action, contact, and completion. Do not expose sensitive system details in a public banner.

## Exam checklist

/usr/src, gunzip, gzip, bzip2, xz, tar, configure, make, uname, install, patch, /bin/sh, dd, /dev/st*, /dev/nst*, mt, rsync, /etc/issue, /etc/issue.net, /etc/motd, wall, shutdown, and systemctl.

## Mini lab

Build a small trusted program in /usr/local. Back up a test directory with tar and rsync, verify checksums, restore into a new path, and send a notice to another test session.
