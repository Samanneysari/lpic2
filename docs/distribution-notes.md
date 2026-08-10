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

Do not edit a generated file until you know which tool owns it.

## Firewall

The objectives name iptables and ip6tables. Modern systems may use nftables underneath.

~~~bash
sudo iptables -L -n -v
sudo ip6tables -L -n -v
sudo nft list ruleset
sudo firewall-cmd --list-all
~~~

Never flush remote firewall rules without console access and a rollback plan.

## SELinux and AppArmor

RHEL-family systems normally use SELinux. Ubuntu normally uses AppArmor. Do not disable either system to solve a configuration problem.

~~~bash
getenforce
sudo ausearch -m AVC -ts recent
sudo aa-status
sudo journalctl -k | grep -i apparmor
~~~

Persistent SELinux labels use semanage and restorecon:

~~~bash
sudo semanage fcontext -a -t httpd_sys_content_t "/srv/www/realsam.ir(/.*)?"
sudo restorecon -Rv /srv/www/realsam.ir
~~~

A direct chcon change can disappear after restorecon or a filesystem relabel.

## Configuration discovery

Use installed documentation instead of guessing paths:

~~~bash
man service-name
systemctl cat service-name
rpm -qc package-name
dpkg-query -L package-name
~~~

## Reload versus restart

After a successful syntax test, prefer reload when the daemon supports it. Reload normally keeps existing connections.

~~~bash
sudo systemctl reload nginx
sudo systemctl reload apache2
sudo systemctl reload httpd
sudo rndc reload
~~~
