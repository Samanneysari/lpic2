# Topic 209: File Sharing

Objectives: 209.1 and 209.2

<!-- BEGIN BEGINNER FOUNDATION -->
## Learn the idea before running commands

### What network file sharing means

Network file sharing lets a client access data stored on another host. The two major technologies in this objective are SMB/CIFS through Samba and NFS. Both expose files, but their identity models, discovery methods, configuration, and security controls differ.

Samba implements SMB services used by Windows, Linux, and other clients. smbd serves files and printers. Depending on the version and role, other components provide name discovery or domain services. Samba can use a local user database, integrate with an existing domain, or act in selected domain roles.

NFS exports parts of a server filesystem to trusted clients. NFSv4 uses a stateful protocol and a unified namespace; older versions also rely on RPC services and separate ports. Client access is affected by server export options, network controls, and local filesystem permissions.

### Identity is the central concept

A network share does not replace local permissions. Samba maps authenticated SMB identities to Unix users and groups. NFS normally trusts numeric user and group IDs unless an identity-mapping design is in place. If IDs differ between client and server, ownership may appear wrong.

root_squash is an important NFS protection: client root is mapped to an unprivileged identity. Avoid no_root_squash except for a narrowly justified design.

### From a client request to a file

For a Samba access:

1. The client resolves the server name and connects to the SMB service.
2. Protocol negotiation selects supported SMB capabilities.
3. The server authenticates the user against its configured identity source.
4. Samba maps that identity to a Unix account or security token.
5. Share rules decide whether the requested share and operation are allowed.
6. The kernel then checks Unix ownership, mode bits, ACLs, mount state, and SELinux/AppArmor policy.
7. Only when both Samba policy and local filesystem policy allow the operation does data reach the client.

For an NFS access:

1. The client resolves the server and contacts the NFS/RPC services required by the chosen version.
2. The server matches the client against an export and its options.
3. NFS presents a numeric UID/GID or a mapped identity.
4. Options such as <code>root_squash</code>, read-only mode, and subtree policy transform or restrict the request.
5. The local filesystem and security policy make the final access decision.
6. Client mount options influence behavior but cannot grant permission denied by the server.

This is why changing a share to world-writable is not a valid troubleshooting method. Identify the exact layer that denied the operation.

### Safe implementation sequence

1. Decide who should access the data and whether they need read or write permission.
2. Create the local directory, owner, group, and permissions first.
3. Limit service exposure to the intended lab network.
4. Write one minimal share or export.
5. Validate configuration.
6. Reload the service.
7. Test as an authorized user and an unauthorized user.
8. Inspect logs and effective permissions.
9. Make the mount persistent only after the manual test succeeds.

Do not solve permission errors with world-writable directories. Trace the authenticated identity, group membership, share policy, mount options, SELinux/AppArmor policy, and local filesystem permissions.
<!-- END BEGINNER FOUNDATION -->

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

<!-- LINE-BY-LINE 1 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>[global]</code> | Opens the named INI-style configuration section. |
| 2 | <code>workgroup = REALSAM</code> | Sets the SMB workgroup name advertised by this standalone Samba server. |
| 3 | <code>security = user</code> | Requires user-level Samba authentication. |
| 4 | <code>server role = standalone server</code> | Configures Samba as a standalone server instead of a domain controller or member. |
| 5 | <code>map to guest = Never</code> | Prevents failed or unknown logins from being silently mapped to the guest account. |
| 6 | <code>logging = file</code> | Selects file-based Samba logging. |
| 7 | <code>log file = /var/log/samba/%m.log</code> | Writes a separate Samba log whose %m placeholder is replaced by the client machine name. |
| 9 | <code>[team]</code> | Opens the named INI-style configuration section. |
| 10 | <code>path = /srv/samba/team</code> | Sets the local directory exported by this Samba share. |
| 11 | <code>browseable = yes</code> | Makes the share visible in normal SMB browse listings. |
| 12 | <code>read only = no</code> | Allows writes at the share layer; filesystem permissions must also allow them. |
| 13 | <code>valid users = @realsam-team</code> | Limits the share to members of the named Unix group; @ means a group. |
| 14 | <code>create mask = 0660</code> | Limits permission bits Samba may apply to newly created files. |
| 15 | <code>directory mask = 0770</code> | Limits permission bits Samba may apply to newly created directories. |

Prepare users and filesystem permissions:

~~~bash
sudo groupadd realsam-team
sudo usermod -aG realsam-team alice
sudo install -d -o root -g realsam-team -m 2770 /srv/samba/team
sudo smbpasswd -a alice
sudo testparm -s
sudo systemctl reload smb
~~~

<!-- LINE-BY-LINE 2 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo groupadd realsam-team</code> | sudo requests administrator privileges for this operation. Creates the named local group. |
| 2 | <code>sudo usermod -aG realsam-team alice</code> | sudo requests administrator privileges for this operation. Changes local user membership or account attributes. |
| 3 | <code>sudo install -d -o root -g realsam-team -m 2770 /srv/samba/team</code> | sudo requests administrator privileges for this operation. Creates a file or directory with explicit owner, group, and permission mode. |
| 4 | <code>sudo smbpasswd -a alice</code> | sudo requests administrator privileges for this operation. Adds or changes a Samba password for an existing mapped user. |
| 5 | <code>sudo testparm -s</code> | sudo requests administrator privileges for this operation. Parses Samba configuration and prints the effective settings. |
| 6 | <code>sudo systemctl reload smb</code> | sudo requests administrator privileges for this operation. Inspects or changes systemd units, targets, enablement, or system state. |

The setgid directory bit keeps the group on new files. Samba permissions do not override restrictive Unix permissions.

Client tests:

~~~bash
smbclient -L //files.realsam.ir -U alice
smbclient //files.realsam.ir/team -U alice
mount -t cifs //files.realsam.ir/team /mnt/team \
  -o credentials=/root/.smb-credentials,vers=3.1.1
~~~

<!-- LINE-BY-LINE 3 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>smbclient -L //files.realsam.ir -U alice</code> | Lists or accesses SMB shares from the command line. |
| 2 | <code>smbclient //files.realsam.ir/team -U alice</code> | Lists or accesses SMB shares from the command line. |
| 3 | <code>mount -t cifs //files.realsam.ir/team /mnt/team \</code> | Attaches a filesystem to the directory tree, remounts it, or displays mount data. The final backslash continues this logical command on the next physical line. |
| 4 | <code>-o credentials=/root/.smb-credentials,vers=3.1.1</code> | This physical line adds the shown option or argument to the command started on the previous line. |

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

<!-- LINE-BY-LINE 4 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>smbstatus</code> | Shows active Samba sessions, files, and locks. |
| 2 | <code>smbcontrol all reload-config</code> | Sends a control message to running Samba processes. |
| 3 | <code>nmblookup -A 10.20.0.40</code> | Queries NetBIOS name service for legacy discovery diagnostics. |
| 4 | <code>net ads testjoin</code> | Runs the selected Samba administration operation. |
| 5 | <code>samba-tool --help</code> | Runs Samba Active Directory and domain administration operations. |
| 6 | <code>journalctl -u smb -u nmb -u winbind</code> | Reads structured systemd journal records with the shown unit or time filter. |

Know user-level and historical share-level security. Current secure deployments normally use user or AD security. Active Directory membership requires DNS, time synchronization, Kerberos, machine credentials, identity mapping, and winbind or another supported identity service.

Samba can expose printer shares. Understand the [printers] share, spool directory, and client drivers at an awareness level.

## 209.2 NFS

NFS exports directories to Unix-like clients. NFSv3 uses rpcbind and several RPC services. NFSv4 uses a unified namespace and normally TCP port 2049.

Server /etc/exports:

~~~exports
/srv/nfs/team 10.20.0.0/24(rw,sync,root_squash,no_subtree_check)
~~~

<!-- LINE-BY-LINE 5 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>/srv/nfs/team 10.20.0.0/24(rw,sync,root_squash,no_subtree_check)</code> | Exports the leading directory to the listed client network with the options in parentheses. |

Apply and inspect:

~~~bash
sudo exportfs -rav
sudo exportfs -v
showmount -e files.realsam.ir
rpcinfo -p files.realsam.ir
nfsstat -s
~~~

<!-- LINE-BY-LINE 6 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo exportfs -rav</code> | sudo requests administrator privileges for this operation. Displays or rebuilds the live NFS export table. |
| 2 | <code>sudo exportfs -v</code> | sudo requests administrator privileges for this operation. Displays or rebuilds the live NFS export table. |
| 3 | <code>showmount -e files.realsam.ir</code> | Queries an NFS server for exports where the NFS/RPC version supports it. |
| 4 | <code>rpcinfo -p files.realsam.ir</code> | Queries RPC programs registered on a host. |
| 5 | <code>nfsstat -s</code> | Displays NFS client or server RPC and operation counters. |

root_squash maps client root to an unprivileged identity. no_root_squash is dangerous and should be used only with a specific justified design. Restrict exports to exact hosts or subnets.

Client:

~~~bash
sudo mount -t nfs4 files.realsam.ir:/team /mnt/team
findmnt /mnt/team
nfsstat -c
~~~

<!-- LINE-BY-LINE 7 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo mount -t nfs4 files.realsam.ir:/team /mnt/team</code> | sudo requests administrator privileges for this operation. Attaches a filesystem to the directory tree, remounts it, or displays mount data. |
| 2 | <code>findmnt /mnt/team</code> | Displays mounts or validates fstab and mount relationships. |
| 3 | <code>nfsstat -c</code> | Displays NFS client or server RPC and operation counters. |

fstab:

~~~fstab
files.realsam.ir:/team /mnt/team nfs4 rw,_netdev,x-systemd.automount 0 0
~~~

<!-- LINE-BY-LINE 8 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>files.realsam.ir:/team /mnt/team nfs4 rw,_netdev,x-systemd.automount 0 0</code> | Defines one fstab entry: source, mount point, filesystem type, options, dump flag, and filesystem-check order. |

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
