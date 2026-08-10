# Topic 205: Network Configuration

Objectives: 205.1, 205.2, and 205.3

<!-- BEGIN BEGINNER FOUNDATION -->
## Learn the idea before running commands

### How Linux networking fits together

A networked Linux host needs a working link, an interface configuration, an IP address and prefix, a route to the destination, and usually DNS resolution. A service also needs a listening socket and a firewall rule that permits the intended traffic.

Troubleshoot from the lowest relevant layer upward:

1. Is the interface present and is the link up?
2. Does it have the correct IPv4 or IPv6 address?
3. Is the connected route present?
4. Is the default or more-specific route correct?
5. Can the next-hop gateway be reached?
6. Does DNS return the expected address?
7. Is the server listening on the correct address and port?
8. Do host and network firewalls allow the traffic?
9. Does packet capture show requests and replies?

### Addresses, prefixes, and routes

The prefix length identifies which address bits describe the local network. Hosts on the same subnet communicate directly after neighbor discovery; traffic for other networks is sent to a router selected by the routing table. The most specific matching route wins, and route metrics break some ties.

IPv6 uses Neighbor Discovery instead of ARP. A link-local IPv6 address is automatically available on an interface and is often required even when global addresses are configured.

### Persistent versus temporary changes

Commands from the ip suite change the running system. Those changes normally disappear after reboot unless they are also written through the distribution network manager, such as NetworkManager or systemd-networkd. Always distinguish a diagnostic temporary change from the persistent configuration.

### Virtual networking

A bond combines interfaces for redundancy or throughput according to its mode. A bridge connects layer-2 segments and is common for virtual machines. A VLAN interface carries traffic tagged for one VLAN. These devices have different purposes, even though they can be combined.

Packet capture can expose credentials and private data. Use a narrow filter, capture only what is required, protect the file, and delete it according to policy.
<!-- END BEGINNER FOUNDATION -->

## 205.1 Basic networking

~~~bash
ip -br link
ip -br address
ip route
ip -6 route
cat /etc/resolv.conf
getent hosts www.realsam.ir
~~~

<!-- LINE-BY-LINE 1 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>ip -br link</code> | Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |
| 2 | <code>ip -br address</code> | Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |
| 3 | <code>ip route</code> | Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |
| 4 | <code>ip -6 route</code> | Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |
| 5 | <code>cat /etc/resolv.conf</code> | Prints or combines files; when redirected it can write the shown data to a file. |
| 6 | <code>getent hosts www.realsam.ir</code> | Queries an NSS database such as hosts, passwd, or group. |

Temporary lab configuration:

~~~bash
sudo ip address add 10.20.0.10/24 dev eth0
sudo ip link set eth0 up
sudo ip route add default via 10.20.0.1
sudo ip -6 address add 2001:db8:20::10/64 dev eth0
~~~

<!-- LINE-BY-LINE 2 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo ip address add 10.20.0.10/24 dev eth0</code> | sudo requests administrator privileges for this operation. Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |
| 2 | <code>sudo ip link set eth0 up</code> | sudo requests administrator privileges for this operation. Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |
| 3 | <code>sudo ip route add default via 10.20.0.1</code> | sudo requests administrator privileges for this operation. Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |
| 4 | <code>sudo ip -6 address add 2001:db8:20::10/64 dev eth0</code> | sudo requests administrator privileges for this operation. Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |

Use the active network manager for persistence. Legacy tools are ifconfig, route, and arp. Modern replacements are ip address, ip route, and ip neigh.

IPv6 link-local addresses normally start with fe80::/10. The documentation prefix is 2001:db8::/32. Neighbor Discovery replaces IPv4 ARP.

Wireless tools include iw, iwconfig, and iwlist:

~~~bash
iw dev
iw dev wlan0 link
iwlist wlan0 scan
~~~

<!-- LINE-BY-LINE 3 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>iw dev</code> | Displays or configures modern Linux wireless interfaces. |
| 2 | <code>iw dev wlan0 link</code> | Displays or configures modern Linux wireless interfaces. |
| 3 | <code>iwlist wlan0 scan</code> | Scans or displays wireless information using the older wireless-tools interface. |

## 205.2 Advanced networking

A multihomed host has several interfaces or networks.

~~~bash
ip route show table all
ip rule
ip route get 203.0.113.20
ip neigh
~~~

<!-- LINE-BY-LINE 4 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>ip route show table all</code> | Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |
| 2 | <code>ip rule</code> | Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |
| 3 | <code>ip route get 203.0.113.20</code> | Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |
| 4 | <code>ip neigh</code> | Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |

Temporary policy routing example:

~~~bash
sudo ip route add default via 10.20.0.1 table 100
sudo ip rule add from 10.20.0.10/32 table 100
~~~

<!-- LINE-BY-LINE 5 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo ip route add default via 10.20.0.1 table 100</code> | sudo requests administrator privileges for this operation. Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |
| 2 | <code>sudo ip rule add from 10.20.0.10/32 table 100</code> | sudo requests administrator privileges for this operation. Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |

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

<!-- LINE-BY-LINE 6 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>ss -lntup</code> | Displays listening or connected sockets and summary counters. |
| 2 | <code>ss -tan state established</code> | Displays listening or connected sockets and summary counters. |
| 3 | <code>lsof -i</code> | Lists open files, devices, and sockets held by processes. |
| 4 | <code>ping -c 4 10.20.0.1</code> | Sends ICMP echo probes to test reachability and round-trip behavior. |
| 5 | <code>ping -6 -c 4 2001:db8:20::1</code> | Sends ICMP echo probes to test reachability and round-trip behavior. |
| 6 | <code>nc -vz www.realsam.ir 443</code> | Opens or listens on a TCP/UDP connection for controlled diagnostics. |
| 7 | <code>sudo tcpdump -ni eth0 port 53</code> | sudo requests administrator privileges for this operation. Captures packets on the selected interface using the shown filter; captures can contain sensitive data. |
| 8 | <code>sudo nmap -sT -p 22,53,80,443 203.0.113.20</code> | sudo requests administrator privileges for this operation. Scans only the authorized target for reachable ports or service information. |

Scan only authorized systems. netstat is a legacy exam command; ss is the common replacement.

## 205.3 Troubleshooting

### Link

~~~bash
ip -s link show eth0
ethtool eth0
dmesg | grep -i eth0
~~~

<!-- LINE-BY-LINE 7 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>ip -s link show eth0</code> | Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |
| 2 | <code>ethtool eth0</code> | Displays or changes Ethernet link, driver, and offload settings. |
| 3 | <code>dmesg \| grep -i eth0</code> | Displays messages from the kernel ring buffer. The pipe sends standard output from the command on the left to standard input of the command on the right. |

### Address and routing

~~~bash
ip address show dev eth0
ip route get 10.20.0.1
ip neigh show dev eth0
traceroute 203.0.113.20
traceroute6 2001:db8::20
mtr -rw 203.0.113.20
~~~

<!-- LINE-BY-LINE 8 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>ip address show dev eth0</code> | Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |
| 2 | <code>ip route get 10.20.0.1</code> | Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |
| 3 | <code>ip neigh show dev eth0</code> | Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |
| 4 | <code>traceroute 203.0.113.20</code> | Shows routed hops that return TTL-expired responses toward a destination. |
| 5 | <code>traceroute6 2001:db8::20</code> | Runs the IPv6 form of traceroute. |
| 6 | <code>mtr -rw 203.0.113.20</code> | Combines repeated route tracing and latency/loss measurement. |

### Name resolution

~~~bash
cat /etc/nsswitch.conf
cat /etc/hosts
cat /etc/resolv.conf
resolvectl status
getent ahosts www.realsam.ir
dig www.realsam.ir
~~~

<!-- LINE-BY-LINE 9 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>cat /etc/nsswitch.conf</code> | Prints or combines files; when redirected it can write the shown data to a file. |
| 2 | <code>cat /etc/hosts</code> | Prints or combines files; when redirected it can write the shown data to a file. |
| 3 | <code>cat /etc/resolv.conf</code> | Prints or combines files; when redirected it can write the shown data to a file. |
| 4 | <code>resolvectl status</code> | Queries systemd-resolved status, per-link DNS settings, or names. |
| 5 | <code>getent ahosts www.realsam.ir</code> | Queries an NSS database such as hosts, passwd, or group. |
| 6 | <code>dig www.realsam.ir</code> | Sends a DNS query and prints the detailed response. |

getent tests the system name-service path. dig tests DNS directly.

### Transport and application

~~~bash
ss -lntup
nc -vz www.realsam.ir 443
curl -vk https://www.realsam.ir/
~~~

<!-- LINE-BY-LINE 10 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>ss -lntup</code> | Displays listening or connected sockets and summary counters. |
| 2 | <code>nc -vz www.realsam.ir 443</code> | Opens or listens on a TCP/UDP connection for controlled diagnostics. |
| 3 | <code>curl -vk https://www.realsam.ir/</code> | Makes an HTTP request; -I requests response headers without downloading the body. |

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

<!-- LINE-BY-LINE 11 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>journalctl -b -u NetworkManager</code> | Reads structured systemd journal records with the shown unit or time filter. |
| 2 | <code>journalctl -b -u systemd-networkd</code> | Reads structured systemd journal records with the shown unit or time filter. |
| 3 | <code>journalctl -k -b</code> | Reads structured systemd journal records with the shown unit or time filter. |
| 4 | <code>nmcli device status</code> | Displays or changes persistent NetworkManager connections. |
| 5 | <code>nmcli connection show</code> | Displays or changes persistent NetworkManager connections. |
| 6 | <code>hostnamectl</code> | Displays or changes the persistent hostname on systemd systems. |

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
