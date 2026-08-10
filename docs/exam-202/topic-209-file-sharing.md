# Topic 209: File Sharing

Objectives: 209.1 and 209.2

## 209.1 Samba

Samba provides SMB/CIFS file and printer services for Windows, Linux, and other clients. It can run as a standalone server or join Active Directory.

Important paths and daemons:

- /etc/samba/smb.conf
- /var/log/samba/
- smbd: file and print service
- nmbd: older NetBIOS name service
- winbindd: identity integration

### Standalone share

~~~ini
[global]
    workgroup = REALSAM
    security = user
    server role = standalone server
    map to guest = Never
    logging = file
    log file = /var/log/samba/%m.log

[team]
    path = /srv/samba/team
    browseable = yes
    read only = no
    valid users = @realsam-team
    create mask = 0660
    directory mask = 0770
~~~

Prepare users and filesystem permissions:

~~~bash
sudo groupadd realsam-team
sudo usermod -aG realsam-team alice
sudo install -d -o root -g realsam-team -m 2770 /srv/samba/team
sudo smbpasswd -a alice
sudo testparm -s
sudo systemctl reload smb
~~~

The setgid directory bit keeps the group on new files. Samba permissions do not override restrictive Unix permissions.

Client tests:

~~~bash
smbclient -L //files.realsam.ir -U alice
smbclient //files.realsam.ir/team -U alice
mount -t cifs //files.realsam.ir/team /mnt/team \
  -o credentials=/root/.smb-credentials,vers=3.1.1
~~~

Protect the credentials file with mode 0600. An fstab CIFS entry can use credentials=, uid, gid, file_mode, directory_mode, and _netdev.

### Administration and troubleshooting

~~~bash
smbstatus
smbcontrol all reload-config
nmblookup -A 10.20.0.40
net ads testjoin
samba-tool --help
journalctl -u smb -u nmb -u winbind
~~~

Know user-level and historical share-level security. Current secure deployments normally use user or AD security. Active Directory membership requires DNS, time synchronization, Kerberos, machine credentials, identity mapping, and winbind or another supported identity service.

Samba can expose printer shares. Understand the [printers] share, spool directory, and client drivers at an awareness level.

## 209.2 NFS

NFS exports directories to Unix-like clients. NFSv3 uses rpcbind and several RPC services. NFSv4 uses a unified namespace and normally TCP port 2049.

Server /etc/exports:

~~~exports
/srv/nfs/team 10.20.0.0/24(rw,sync,root_squash,no_subtree_check)
~~~

Apply and inspect:

~~~bash
sudo exportfs -rav
sudo exportfs -v
showmount -e files.realsam.ir
rpcinfo -p files.realsam.ir
nfsstat -s
~~~

root_squash maps client root to an unprivileged identity. no_root_squash is dangerous and should be used only with a specific justified design. Restrict exports to exact hosts or subnets.

Client:

~~~bash
sudo mount -t nfs4 files.realsam.ir:/team /mnt/team
findmnt /mnt/team
nfsstat -c
~~~

fstab:

~~~fstab
files.realsam.ir:/team /mnt/team nfs4 rw,_netdev,x-systemd.automount 0 0
~~~

Important terms include /proc/mounts, /etc/fstab, exportfs, showmount, nfsstat, rpcinfo, mountd, and portmapper. TCP Wrappers are an older objective term and are not supported by every current service.

### NFS safety

- use least-privilege export options
- align user and group IDs or use a directory identity design
- use Kerberos security modes when required
- protect the network with firewall rules
- avoid exporting filesystems to everyone
- understand hard versus soft retry behavior
- test server failure behavior before production

## Exam checklist

smbd, nmbd, winbindd, smbcontrol, smbstatus, testparm, smbpasswd, nmblookup, samba-tool, net, smbclient, mount.cifs, /etc/samba/, /var/log/samba/, /etc/exports, exportfs, showmount, nfsstat, /proc/mounts, /etc/fstab, rpcinfo, mountd, portmapper, NFSv3, and NFSv4.

## Mini lab

Create a Samba user share and an NFS export for 10.20.0.0/24. Mount both from a client, prove write permissions, verify an unauthorized user is denied, and collect server and client troubleshooting output.
