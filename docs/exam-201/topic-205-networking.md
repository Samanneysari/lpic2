# Topic 205: Network Configuration

Objectives: 205.1, 205.2, and 205.3

## 205.1 Basic networking

~~~bash
ip -br link
ip -br address
ip route
ip -6 route
cat /etc/resolv.conf
getent hosts www.realsam.ir
~~~

Temporary lab configuration:

~~~bash
sudo ip address add 10.20.0.10/24 dev eth0
sudo ip link set eth0 up
sudo ip route add default via 10.20.0.1
sudo ip -6 address add 2001:db8:20::10/64 dev eth0
~~~

Use the active network manager for persistence. Legacy tools are ifconfig, route, and arp. Modern replacements are ip address, ip route, and ip neigh.

IPv6 link-local addresses normally start with fe80::/10. The documentation prefix is 2001:db8::/32. Neighbor Discovery replaces IPv4 ARP.

Wireless tools include iw, iwconfig, and iwlist:

~~~bash
iw dev
iw dev wlan0 link
iwlist wlan0 scan
~~~

## 205.2 Advanced networking

A multihomed host has several interfaces or networks.

~~~bash
ip route show table all
ip rule
ip route get 203.0.113.20
ip neigh
~~~

Temporary policy routing example:

~~~bash
sudo ip route add default via 10.20.0.1 table 100
sudo ip rule add from 10.20.0.10/32 table 100
~~~

Plan source selection, asymmetric routing, reverse-path filtering, and firewalls.

~~~bash
ss -lntup
ss -tan state established
lsof -i
ping -c 4 10.20.0.1
ping -6 -c 4 2001:db8:20::1
nc -vz www.realsam.ir 443
sudo tcpdump -ni eth0 port 53
sudo nmap -sT -p 22,53,80,443 203.0.113.20
~~~

Scan only authorized systems. netstat is a legacy exam command; ss is the common replacement.

## 205.3 Troubleshooting

### Link

~~~bash
ip -s link show eth0
ethtool eth0
dmesg | grep -i eth0
~~~

### Address and routing

~~~bash
ip address show dev eth0
ip route get 10.20.0.1
ip neigh show dev eth0
traceroute 203.0.113.20
traceroute6 2001:db8::20
mtr -rw 203.0.113.20
~~~

### Name resolution

~~~bash
cat /etc/nsswitch.conf
cat /etc/hosts
cat /etc/resolv.conf
resolvectl status
getent ahosts www.realsam.ir
dig www.realsam.ir
~~~

getent tests the system name-service path. dig tests DNS directly.

### Transport and application

~~~bash
ss -lntup
nc -vz www.realsam.ir 443
curl -vk https://www.realsam.ir/
~~~

Ping alone does not prove that an application works.

### Logs and ownership

~~~bash
journalctl -b -u NetworkManager
journalctl -b -u systemd-networkd
journalctl -k -b
nmcli device status
nmcli connection show
hostnamectl
~~~

Important paths include /etc/network/, /etc/sysconfig/network-scripts/, /etc/hostname, /etc/HOSTNAME, /etc/hosts, and /etc/resolv.conf. /etc/hosts.allow and /etc/hosts.deny are historical TCP Wrappers exam terms.

## Fault table

| Symptom | Likely cause |
|---|---|
| No carrier | Cable, virtual NIC, switch, driver |
| Local network only | Missing or wrong route |
| IP works, name fails | DNS or NSS |
| One port fails | Service, bind address, firewall, security policy |
| Intermittent loss | Congestion, duplex, MTU, failing link |
| Replies use wrong path | Route or policy rule |
| IPv4 works, IPv6 fails | RA, prefix, route, firewall, AAAA |

## Exam checklist

ip, ifconfig, route, arp, iw, iwconfig, iwlist, ss, netstat, lsof, ping, ping6, nc, tcpdump, nmap, traceroute, traceroute6, mtr, hostname, logs, dmesg, resolv.conf, hosts, hostname files, and TCP Wrappers files.

## Mini lab

Create two lab networks and a multihomed router VM. Configure IPv4 and IPv6, capture DNS, introduce a wrong prefix, and document the evidence used to fix it.
