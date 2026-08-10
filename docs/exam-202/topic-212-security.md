# Topic 212: System Security

Objectives: 212.1, 212.2, 212.3, 212.4, and 212.5

<!-- BEGIN BEGINNER FOUNDATION -->
## Learn the idea before running commands

### Security is a set of boundaries

System security is not one command. It combines least privilege, patched software, network filtering, strong authentication, encryption, logging, backups, and tested recovery. Start by defining which users, hosts, ports, and services are allowed. Deny or remove what is unnecessary.

### Routing and packet filtering

A router forwards packets between networks when kernel forwarding is enabled and routes exist. A firewall then accepts, rejects, or drops traffic according to ordered rules. Stateful filtering tracks connections so return traffic can be treated differently from new unsolicited traffic.

NAT changes address or port information. Source NAT is commonly used for outbound private networks; destination NAT forwards traffic to an internal service. NAT is not an access-control policy by itself.

The exam includes iptables, ip6tables, ebtables, and knowledge of modern nftables. Do not mix management layers without understanding which service owns the live ruleset. Apply remote firewall changes with console access or an automatic rollback.

### FTP and SSH

FTP uses separate control and data connections. Active and passive modes open those connections differently, which affects firewalls. Plain FTP exposes credentials and data; prefer SFTP or another encrypted method unless compatibility requires FTP.

OpenSSH provides encrypted remote login, commands, file transfer, and tunneling. Public-key authentication proves possession of a private key. The private key stays on the client; the public key is placed in authorized_keys on the server. File permissions, host-key verification, and a safe test session are essential.

### Scanning and incident evidence

A port scanner shows what is reachable, not whether a service is secure. Scan only systems you own or are authorized to test. Compare listening sockets on the host with remotely reachable ports and explain every difference.

### VPN concepts

OpenVPN creates an encrypted tunnel using certificates or shared credentials. Routing decides which traffic enters the tunnel. Firewall rules control traffic at tunnel boundaries. Certificate validation, unique client credentials, revocation, and protected private keys are required.

### Safe change sequence

1. Keep a working console or second SSH session.
2. Back up the exact configuration.
3. Validate syntax where a validation command exists.
4. Add the narrow allow rule before removing an old access path.
5. Reload.
6. Test a new connection.
7. Inspect logs and listening ports.
8. Close the old session only after success.
<!-- END BEGINNER FOUNDATION -->

## 212.1 Configure a router

Linux routing requires forwarding, routes, and firewall policy.

Private IPv4 ranges:

- 10.0.0.0/8
- 172.16.0.0/12
- 192.168.0.0/16

IPv6 Unique Local Addresses use fc00::/7. IPv6 link-local addresses use fe80::/10.

Enable forwarding persistently only on an intended router:

~~~text
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
~~~

<!-- LINE-BY-LINE 1 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>net.ipv4.ip_forward = 1</code> | Persistently enables IPv4 packet forwarding when loaded through sysctl. |
| 2 | <code>net.ipv6.conf.all.forwarding = 1</code> | Persistently enables IPv6 forwarding and router behavior when loaded through sysctl. |

~~~bash
sudo sysctl --system
ip route
ip -6 route
~~~

<!-- LINE-BY-LINE 2 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo sysctl --system</code> | sudo requests administrator privileges for this operation. Reads or changes a live kernel parameter under /proc/sys. |
| 2 | <code>ip route</code> | Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |
| 3 | <code>ip -6 route</code> | Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |

iptables example:

~~~bash
sudo iptables -P FORWARD DROP
sudo iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A FORWARD -i lan0 -o wan0 -s 10.20.0.0/24 -j ACCEPT
sudo iptables -t nat -A POSTROUTING -o wan0 -s 10.20.0.0/24 -j MASQUERADE
~~~

<!-- LINE-BY-LINE 3 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo iptables -P FORWARD DROP</code> | sudo requests administrator privileges for this operation. Inspects or changes the legacy IPv4 netfilter rules. |
| 2 | <code>sudo iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT</code> | sudo requests administrator privileges for this operation. Inspects or changes the legacy IPv4 netfilter rules. |
| 3 | <code>sudo iptables -A FORWARD -i lan0 -o wan0 -s 10.20.0.0/24 -j ACCEPT</code> | sudo requests administrator privileges for this operation. Inspects or changes the legacy IPv4 netfilter rules. |
| 4 | <code>sudo iptables -t nat -A POSTROUTING -o wan0 -s 10.20.0.0/24 -j MASQUERADE</code> | sudo requests administrator privileges for this operation. Inspects or changes the legacy IPv4 netfilter rules. |

Port forwarding:

~~~bash
sudo iptables -t nat -A PREROUTING -i wan0 -p tcp --dport 443 \
  -j DNAT --to-destination 10.20.0.20:443
sudo iptables -A FORWARD -p tcp -d 10.20.0.20 --dport 443 \
  -m conntrack --ctstate NEW,ESTABLISHED,RELATED -j ACCEPT
~~~

<!-- LINE-BY-LINE 4 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo iptables -t nat -A PREROUTING -i wan0 -p tcp --dport 443 \</code> | sudo requests administrator privileges for this operation. Inspects or changes the legacy IPv4 netfilter rules. The final backslash continues this logical command on the next physical line. |
| 2 | <code>-j DNAT --to-destination 10.20.0.20:443</code> | This physical line adds the shown option or argument to the command started on the previous line. |
| 3 | <code>sudo iptables -A FORWARD -p tcp -d 10.20.0.20 --dport 443 \</code> | sudo requests administrator privileges for this operation. Inspects or changes the legacy IPv4 netfilter rules. The final backslash continues this logical command on the next physical line. |
| 4 | <code>-m conntrack --ctstate NEW,ESTABLISHED,RELATED -j ACCEPT</code> | This physical line adds the shown option or argument to the command started on the previous line. |

Know ip6tables for IPv6 filtering. Modern systems may use nftables behind or instead of iptables.

Save and restore with distribution tools or:

~~~bash
sudo iptables-save > /root/iptables.rules
sudo iptables-restore < /root/iptables.rules
~~~

<!-- LINE-BY-LINE 5 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo iptables-save > /root/iptables.rules</code> | sudo requests administrator privileges for this operation. Serializes the current iptables rules to standard output. Shell redirection writes standard output to the named file instead of the terminal. |
| 2 | <code>sudo iptables-restore < /root/iptables.rules</code> | sudo requests administrator privileges for this operation. Loads an iptables ruleset from standard input. |

Never change default policy or flush rules over SSH without console access, a second session, and timed rollback.

Basic protection includes default deny, state tracking, source validation, rate limiting where appropriate, logging without log floods, and patching.

## 212.2 FTP servers

FTP has separate control and data connections.

- active mode: server connects back to the client
- passive mode: client connects to a server-selected data port
- FTPS: FTP protected with TLS
- SFTP: SSH File Transfer Protocol; it is not FTP

vsftpd example ideas:

~~~ini
anonymous_enable=NO
local_enable=YES
write_enable=YES
chroot_local_user=YES
pasv_min_port=30000
pasv_max_port=30100
ssl_enable=YES
~~~

<!-- LINE-BY-LINE 6 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>anonymous_enable=NO</code> | Disables anonymous FTP logins. |
| 2 | <code>local_enable=YES</code> | Allows authenticated local accounts to use FTP. |
| 3 | <code>write_enable=YES</code> | Allows FTP commands that modify data when filesystem permissions also permit them. |
| 4 | <code>chroot_local_user=YES</code> | Confines local FTP users to their selected directory tree, subject to safe writable-root rules. |
| 5 | <code>pasv_min_port=30000</code> | Sets the first TCP port in the passive FTP data-connection range. |
| 6 | <code>pasv_max_port=30100</code> | Sets the last TCP port in the passive FTP data-connection range. |
| 7 | <code>ssl_enable=YES</code> | Enables TLS support for FTP sessions; certificate directives are also required. |

Validate package documentation, certificate paths, filesystem permissions, firewall ports, and chroot behavior.

Anonymous uploads are high risk. If required, isolate the upload-only directory, prevent download or execution, scan content, set quotas, use noexec storage where possible, and never expose uploaded files directly to a web application.

Know vsftpd.conf, Pure-FTPd command-line options, and ProFTPd awareness.

## 212.3 Secure Shell

Server configuration is normally /etc/ssh/sshd_config.

Secure baseline ideas:

~~~sshconfig
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no
AllowGroups ssh-users
X11Forwarding no
~~~

<!-- LINE-BY-LINE 7 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>PermitRootLogin no</code> | Prevents direct SSH login as root. |
| 2 | <code>PubkeyAuthentication yes</code> | Allows SSH public-key authentication. |
| 3 | <code>PasswordAuthentication no</code> | Disables SSH password authentication after key access has been tested. |
| 4 | <code>AllowGroups ssh-users</code> | Limits SSH login to members of the named Unix group. |
| 5 | <code>X11Forwarding no</code> | Disables SSH X11 forwarding to reduce unused attack surface. |

Do not disable password login until a key login has succeeded in a second session.

~~~bash
sudo sshd -t
sudo systemctl reload sshd
ssh -vv alice@server.realsam.ir
~~~

<!-- LINE-BY-LINE 8 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo sshd -t</code> | sudo requests administrator privileges for this operation. Runs or validates the OpenSSH server configuration; -t performs a syntax check. |
| 2 | <code>sudo systemctl reload sshd</code> | sudo requests administrator privileges for this operation. Inspects or changes systemd units, targets, enablement, or system state. |
| 3 | <code>ssh -vv alice@server.realsam.ir</code> | Opens an encrypted remote session or tunnel using the selected identity and options. |

Key management:

~~~bash
ssh-keygen -t ed25519 -a 64
ssh-copy-id alice@server.realsam.ir
ssh-keygen -lf ~/.ssh/id_ed25519.pub
~~~

<!-- LINE-BY-LINE 9 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>ssh-keygen -t ed25519 -a 64</code> | Creates, inspects, or manages SSH key material. |
| 2 | <code>ssh-copy-id alice@server.realsam.ir</code> | Appends the selected public key to the remote account's authorized_keys file. |
| 3 | <code>ssh-keygen -lf ~/.ssh/id_ed25519.pub</code> | Creates, inspects, or manages SSH key material. |

Protect private keys. authorized_keys can restrict a key with from=, command=, no-port-forwarding, and other options.

Forwarding:

~~~bash
ssh -L 15432:db.realsam.ir:5432 alice@bastion.realsam.ir
ssh -R 18080:localhost:8080 alice@server.realsam.ir
ssh -D 1080 alice@bastion.realsam.ir
~~~

<!-- LINE-BY-LINE 10 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>ssh -L 15432:db.realsam.ir:5432 alice@bastion.realsam.ir</code> | Opens an encrypted remote session or tunnel using the selected identity and options. |
| 2 | <code>ssh -R 18080:localhost:8080 alice@server.realsam.ir</code> | Opens an encrypted remote session or tunnel using the selected identity and options. |
| 3 | <code>ssh -D 1080 alice@bastion.realsam.ir</code> | Opens an encrypted remote session or tunnel using the selected identity and options. |

Local, remote, and dynamic forwarding carry application traffic inside SSH. Restrict forwarding on servers that do not require it.

Keep multiple authorized sessions open while testing remote SSH changes so one failed configuration does not remove all access.

## 212.4 Security tasks

### Patch and alerts

Use distribution security advisories, CERT organizations, CISA, and vendor announcements. Apply security updates with change control and reboot when a replaced kernel or critical library requires it.

### Inspect ports

~~~bash
ss -lntup
sudo nmap -sT -sV -p- 203.0.113.20
nc -vz 203.0.113.20 22
telnet 203.0.113.20 25
~~~

<!-- LINE-BY-LINE 11 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>ss -lntup</code> | Displays listening or connected sockets and summary counters. |
| 2 | <code>sudo nmap -sT -sV -p- 203.0.113.20</code> | sudo requests administrator privileges for this operation. Scans only the authorized target for reachable ports or service information. |
| 3 | <code>nc -vz 203.0.113.20 22</code> | Opens or listens on a TCP/UDP connection for controlled diagnostics. |
| 4 | <code>telnet 203.0.113.20 25</code> | Opens a plaintext TCP session; here it is only a protocol diagnostic, not a secure login. |

Use nmap only with authorization. telnet is useful for a plain protocol test but not for secure remote login.

### Detection and blocking

- Snort: network intrusion detection and prevention awareness
- OpenVAS or Greenbone: vulnerability scanning awareness
- fail2ban: blocks repeated abusive events using logs and firewall actions

~~~bash
sudo fail2ban-client status
sudo fail2ban-client status sshd
~~~

<!-- LINE-BY-LINE 12 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo fail2ban-client status</code> | sudo requests administrator privileges for this operation. Queries or controls Fail2ban jails and state. |
| 2 | <code>sudo fail2ban-client status sshd</code> | sudo requests administrator privileges for this operation. Queries or controls Fail2ban jails and state. |

Do not use fail2ban as a replacement for secure authentication and patching.

Review logs, establish time synchronization, centralize important events, limit log access, and test alert delivery.

## 212.5 OpenVPN

OpenVPN creates routed or bridged encrypted tunnels. Common designs are remote access and site-to-site.

A PKI design uses:

- CA certificate
- server certificate and private key
- client certificates and private keys
- revocation list
- TLS control-channel protection
- routes and firewall policy

Server configuration ideas:

~~~openvpn
port 1194
proto udp
dev tun
server 10.30.0.0 255.255.255.0
topology subnet
ca ca.crt
cert vpn.realsam.ir.crt
key vpn.realsam.ir.key
crl-verify crl.pem
tls-crypt ta.key
keepalive 10 120
persist-key
persist-tun
user nobody
group nogroup
verb 3
~~~

<!-- LINE-BY-LINE 13 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>port 1194</code> | Makes OpenVPN use UDP/TCP port 1194 as selected by the protocol line. |
| 2 | <code>proto udp</code> | Uses UDP as the OpenVPN transport. |
| 3 | <code>dev tun</code> | Creates a routed layer-3 tunnel interface. |
| 4 | <code>server 10.30.0.0 255.255.255.0</code> | Allocates client tunnel addresses from the 10.30.0.0/24 VPN network. |
| 5 | <code>topology subnet</code> | Uses subnet-style tunnel addressing so clients receive addresses from one virtual subnet. |
| 6 | <code>ca ca.crt</code> | Loads the certificate authority used to verify peer certificates. |
| 7 | <code>cert vpn.realsam.ir.crt</code> | Loads this peer's public certificate. |
| 8 | <code>key vpn.realsam.ir.key</code> | Loads the VPN server's private key; protect this file. |
| 9 | <code>crl-verify crl.pem</code> | Rejects certificates listed in the supplied certificate revocation list. |
| 10 | <code>tls-crypt ta.key</code> | Protects and authenticates the TLS control channel with the shared tls-crypt key. |
| 11 | <code>keepalive 10 120</code> | Keeps the shown number of idle upstream connections available per worker. |
| 12 | <code>persist-key</code> | Keeps key material available across privilege or restart-related transitions. |
| 13 | <code>persist-tun</code> | Keeps the tunnel device open across selected restarts. |
| 14 | <code>user nobody</code> | Drops the OpenVPN process to an unprivileged user after initialization. |
| 15 | <code>group nogroup</code> | Drops the OpenVPN process to an unprivileged group after initialization. |
| 16 | <code>verb 3</code> | Sets normal operational logging verbosity. |

Account names differ by distribution. Protect every private key. Use supported ciphers and settings from the installed OpenVPN documentation.

Client ideas:

~~~openvpn
client
dev tun
proto udp
remote vpn.realsam.ir 1194
nobind
remote-cert-tls server
persist-key
persist-tun
verb 3
~~~

<!-- LINE-BY-LINE 14 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>client</code> | Selects OpenVPN client mode and applies client-oriented defaults. |
| 2 | <code>dev tun</code> | Creates a routed layer-3 tunnel interface. |
| 3 | <code>proto udp</code> | Uses UDP as the OpenVPN transport. |
| 4 | <code>remote vpn.realsam.ir 1194</code> | Connects to vpn.realsam.ir on port 1194. |
| 5 | <code>nobind</code> | Lets the client use an automatically selected local source port. |
| 6 | <code>remote-cert-tls server</code> | Requires the remote certificate to be valid for a TLS server role. |
| 7 | <code>persist-key</code> | Keeps key material available across privilege or restart-related transitions. |
| 8 | <code>persist-tun</code> | Keeps the tunnel device open across selected restarts. |
| 9 | <code>verb 3</code> | Sets normal operational logging verbosity. |

Test routes, DNS, firewall, certificate identity, revocation, and traffic flow. Do not route all client traffic unless that is the intended policy.

~~~bash
sudo openvpn --config client.conf
ip address show dev tun0
ip route
journalctl -u openvpn-server@server
~~~

<!-- LINE-BY-LINE 15 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo openvpn --config client.conf</code> | sudo requests administrator privileges for this operation. Runs OpenVPN or parses the selected tunnel configuration. |
| 2 | <code>ip address show dev tun0</code> | Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |
| 3 | <code>ip route</code> | Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |
| 4 | <code>journalctl -u openvpn-server@server</code> | Reads structured systemd journal records with the shown unit or time filter. |

## Exam checklist

/proc/sys/net/ipv4/, /proc/sys/net/ipv6/, /etc/services, iptables, ip6tables, NAT, forwarding, vsftpd.conf, Pure-FTPd options, ProFTPd, active and passive FTP, ssh, sshd, sshd_config, keys, PermitRootLogin, PubkeyAuthentication, AllowUsers, PasswordAuthentication, telnet, nmap, fail2ban, nc, OpenVAS, Snort, /etc/openvpn/, and openvpn.

## Mini lab

Build a two-interface router VM with forwarding, filtering, NAT, and one port forward. Configure key-only SSH after testing keys, inspect exposed ports, configure a fail2ban jail, compare active and passive FTP, and create an OpenVPN tunnel between two lab hosts.
