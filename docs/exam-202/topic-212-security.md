# Topic 212: System Security

Objectives: 212.1, 212.2, 212.3, 212.4, and 212.5

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

~~~bash
sudo sysctl --system
ip route
ip -6 route
~~~

iptables example:

~~~bash
sudo iptables -P FORWARD DROP
sudo iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A FORWARD -i lan0 -o wan0 -s 10.20.0.0/24 -j ACCEPT
sudo iptables -t nat -A POSTROUTING -o wan0 -s 10.20.0.0/24 -j MASQUERADE
~~~

Port forwarding:

~~~bash
sudo iptables -t nat -A PREROUTING -i wan0 -p tcp --dport 443 \
  -j DNAT --to-destination 10.20.0.20:443
sudo iptables -A FORWARD -p tcp -d 10.20.0.20 --dport 443 \
  -m conntrack --ctstate NEW,ESTABLISHED,RELATED -j ACCEPT
~~~

Know ip6tables for IPv6 filtering. Modern systems may use nftables behind or instead of iptables.

Save and restore with distribution tools or:

~~~bash
sudo iptables-save > /root/iptables.rules
sudo iptables-restore < /root/iptables.rules
~~~

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

Do not disable password login until a key login has succeeded in a second session.

~~~bash
sudo sshd -t
sudo systemctl reload sshd
ssh -vv alice@server.realsam.ir
~~~

Key management:

~~~bash
ssh-keygen -t ed25519 -a 64
ssh-copy-id alice@server.realsam.ir
ssh-keygen -lf ~/.ssh/id_ed25519.pub
~~~

Protect private keys. authorized_keys can restrict a key with from=, command=, no-port-forwarding, and other options.

Forwarding:

~~~bash
ssh -L 15432:db.realsam.ir:5432 alice@bastion.realsam.ir
ssh -R 18080:localhost:8080 alice@server.realsam.ir
ssh -D 1080 alice@bastion.realsam.ir
~~~

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

Use nmap only with authorization. telnet is useful for a plain protocol test but not for secure remote login.

### Detection and blocking

- Snort: network intrusion detection and prevention awareness
- OpenVAS or Greenbone: vulnerability scanning awareness
- fail2ban: blocks repeated abusive events using logs and firewall actions

~~~bash
sudo fail2ban-client status
sudo fail2ban-client status sshd
~~~

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

Test routes, DNS, firewall, certificate identity, revocation, and traffic flow. Do not route all client traffic unless that is the intended policy.

~~~bash
sudo openvpn --config client.conf
ip address show dev tun0
ip route
journalctl -u openvpn-server@server
~~~

## Exam checklist

/proc/sys/net/ipv4/, /proc/sys/net/ipv6/, /etc/services, iptables, ip6tables, NAT, forwarding, vsftpd.conf, Pure-FTPd options, ProFTPd, active and passive FTP, ssh, sshd, sshd_config, keys, PermitRootLogin, PubkeyAuthentication, AllowUsers, PasswordAuthentication, telnet, nmap, fail2ban, nc, OpenVAS, Snort, /etc/openvpn/, and openvpn.

## Mini lab

Build a two-interface router VM with forwarding, filtering, NAT, and one port forward. Configure key-only SSH after testing keys, inspect exposed ports, configure a fail2ban jail, compare active and passive FTP, and create an OpenVPN tunnel between two lab hosts.
