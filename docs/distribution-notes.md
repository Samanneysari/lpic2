# Distribution Differences

LPIC is distribution-neutral. Recognize both Debian-family and Red Hat-family layouts.

## Package and service names

| Task or service | Debian and Ubuntu | RHEL, Rocky, AlmaLinux |
|---|---|---|
| Install a package | apt install package | dnf install package |
| List package files | dpkg -L package | rpm -ql package |
| Find owning package | dpkg -S /path | rpm -qf /path |
| Apache package/service | apache2 | httpd |
| Apache path | /etc/apache2/ | /etc/httpd/ |
| BIND package | bind9 | bind |
| BIND configuration | /etc/bind/named.conf* | /etc/named.conf |
| BIND zone directory | /var/lib/bind or /etc/bind | /var/named |
| DHCP package | isc-dhcp-server | dhcp-server |
| NFS service | nfs-kernel-server | nfs-server |
| Main system log | /var/log/syslog | /var/log/messages |

## Network configuration

A system may use NetworkManager, systemd-networkd, ifupdown, Netplan, or older network-scripts. First identify the active manager:

~~~bash
systemctl is-active NetworkManager
networkctl status
nmcli device status
ip -br address
ip route
resolvectl status
~~~

<!-- LINE-BY-LINE 1 -->
**Line-by-line explanation**

| Line | Command | What it does |
|---:|---|---|
| 1 | <code>systemctl is-active NetworkManager</code> | Checks whether NetworkManager is currently active under systemd. |
| 2 | <code>networkctl status</code> | Shows the state of links managed or observed by systemd-networkd. |
| 3 | <code>nmcli device status</code> | Lists NetworkManager devices, their type, and connection state. |
| 4 | <code>ip -br address</code> | Shows a brief list of interfaces and assigned addresses. |
| 5 | <code>ip route</code> | Displays the running IPv4 and IPv6 routing tables. |
| 6 | <code>resolvectl status</code> | Shows systemd-resolved global and per-link DNS configuration. |

Do not edit a generated file until you know which tool owns it.

## Firewall

The objectives name iptables and ip6tables. Modern systems may use nftables underneath.

~~~bash
sudo iptables -L -n -v
sudo ip6tables -L -n -v
sudo nft list ruleset
sudo firewall-cmd --list-all
~~~

<!-- LINE-BY-LINE 2 -->
**Line-by-line explanation**

| Line | Command | What it does |
|---:|---|---|
| 1 | <code>sudo iptables -L -n -v</code> | Lists legacy IPv4 firewall rules with numeric addresses, packet counters, and byte counters; sudo requests administrator access. |
| 2 | <code>sudo ip6tables -L -n -v</code> | Lists legacy IPv6 firewall rules with numeric addresses, packet counters, and byte counters; sudo requests administrator access. |
| 3 | <code>sudo nft list ruleset</code> | Prints the complete nftables ruleset; sudo requests administrator access. |
| 4 | <code>sudo firewall-cmd --list-all</code> | Shows the effective firewalld policy for the current zone; sudo requests administrator access. |

Never flush remote firewall rules without console access and a rollback plan.

## SELinux and AppArmor

RHEL-family systems normally use SELinux. Ubuntu normally uses AppArmor. Do not disable either system to solve a configuration problem.

~~~bash
getenforce
sudo ausearch -m AVC -ts recent
sudo aa-status
sudo journalctl -k | grep -i apparmor
~~~

<!-- LINE-BY-LINE 3 -->
**Line-by-line explanation**

| Line | Command | What it does |
|---:|---|---|
| 1 | <code>getenforce</code> | Reports whether SELinux is enforcing, permissive, or disabled. |
| 2 | <code>sudo ausearch -m AVC -ts recent</code> | Searches recent Linux audit records for SELinux AVC denials; sudo requests administrator access. |
| 3 | <code>sudo aa-status</code> | Shows loaded AppArmor profiles and enforcement state; sudo requests administrator access. |
| 4 | <code>sudo journalctl -k \| grep -i apparmor</code> | Reads kernel journal messages and keeps lines mentioning AppArmor; the pipe passes journal output to grep. |

Persistent SELinux labels use semanage and restorecon:

~~~bash
sudo semanage fcontext -a -t httpd_sys_content_t "/srv/www/realsam.ir(/.*)?"
sudo restorecon -Rv /srv/www/realsam.ir
~~~

<!-- LINE-BY-LINE 4 -->
**Line-by-line explanation**

| Line | Command | What it does |
|---:|---|---|
| 1 | <code>sudo semanage fcontext -a -t httpd_sys_content_t "/srv/www/realsam.ir(/.*)?"</code> | Adds a persistent SELinux file-context rule for the realsam.ir document tree; sudo requests administrator access. |
| 2 | <code>sudo restorecon -Rv /srv/www/realsam.ir</code> | Recursively applies the persistent SELinux context policy to that document tree; sudo requests administrator access. |

A direct chcon change can disappear after restorecon or a filesystem relabel.

## Configuration discovery

Use installed documentation instead of guessing paths:

~~~bash
man service-name
systemctl cat service-name
rpm -qc package-name
dpkg-query -L package-name
~~~

<!-- LINE-BY-LINE 5 -->
**Line-by-line explanation**

| Line | Command | What it does |
|---:|---|---|
| 1 | <code>man service-name</code> | Opens the manual page for the service; replace service-name with the real service name. |
| 2 | <code>systemctl cat service-name</code> | Prints the packaged systemd unit and all drop-in overrides for the service. |
| 3 | <code>rpm -qc package-name</code> | Lists configuration files installed by an RPM package. |
| 4 | <code>dpkg-query -L package-name</code> | Lists every file installed by a Debian package. |

## Reload versus restart

After a successful syntax test, prefer reload when the daemon supports it. Reload normally keeps existing connections.

~~~bash
sudo systemctl reload nginx
sudo systemctl reload apache2
sudo systemctl reload httpd
sudo rndc reload
~~~

<!-- LINE-BY-LINE 6 -->
**Line-by-line explanation**

| Line | Command | What it does |
|---:|---|---|
| 1 | <code>sudo systemctl reload nginx</code> | Reloads Nginx through systemd without an unnecessary full restart; sudo requests administrator access. |
| 2 | <code>sudo systemctl reload apache2</code> | Reloads Debian-family Apache through systemd; sudo requests administrator access. |
| 3 | <code>sudo systemctl reload httpd</code> | Reloads RHEL-family Apache through systemd; sudo requests administrator access. |
| 4 | <code>sudo rndc reload</code> | Sends an authenticated reload command to BIND; sudo requests administrator access. |
