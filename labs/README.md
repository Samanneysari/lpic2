# LPIC-2 Hands-on Labs

Use disposable virtual machines. Take snapshots. Never use production disks, DNS zones, mail domains, firewall gateways, or credentials.

## Suggested lab network

| Host | Address | Name |
|---|---|---|
| Router | 10.20.0.1 | router.realsam.ir |
| DNS and DHCP | 10.20.0.53 | ns1.realsam.ir |
| Web and proxy | 10.20.0.20 | www.realsam.ir |
| File server | 10.20.0.40 | files.realsam.ir |
| LDAP | 10.20.0.50 | ldap.realsam.ir |
| Mail | 10.20.0.25 | mail.realsam.ir |
| VPN | 10.20.0.60 | vpn.realsam.ir |
| Client | DHCP | client1.realsam.ir |

This is a private lab. Public DNS examples in the guide use documentation addresses and are not expected to route.

## Lab report template

For every lab record:

1. objective codes
2. topology and versions
3. starting state
4. commands and configuration
5. syntax-test results
6. verification from a client
7. one induced failure
8. evidence used to diagnose it
9. rollback or cleanup
10. what you learned

## Lab 200: Find a bottleneck

Objectives: 200.1 and 200.2

1. Record uptime, memory, disk, inode, and network baselines.
2. Create controlled CPU, memory, and I/O pressure one at a time.
3. Observe top, vmstat, iostat, iotop, sar, ss, and lsof.
4. Identify the process responsible.
5. Save ten samples and graph one metric.
6. Estimate when a test filesystem would fill at the measured growth rate.

Success: the report distinguishes CPU pressure, I/O wait, memory pressure, and disk-full conditions.

## Lab 201: Kernel and udev

Objectives: 201.1-201.3

1. Record kernel version, /boot contents, and module directory.
2. Load the dummy module with modprobe.
3. Inspect it with lsmod and modinfo.
4. Create a modprobe alias under /etc/modprobe.d/.
5. Monitor a safe udev event.
6. Add a harmless sysctl file and apply it.
7. Remove the module and setting.
8. In a snapshot VM, review kernel build targets without replacing the working kernel.

Success: you can explain modules, dependencies, initramfs, DKMS, sysctl, and udev.

## Lab 202: Boot and recovery

Objectives: 202.1-202.3

1. Draw the firmware-to-systemd boot chain.
2. Inspect default target and dependencies.
3. Create a service override and view it with systemd-delta.
4. Boot once into rescue.target.
5. Inspect the ESP or BIOS boot layout.
6. List GRUB files and current kernel command line.
7. Introduce a harmless failed mount with nofail, diagnose it, and remove it.
8. Identify files used by PXELINUX and UEFI network boot.

Success: normal boot is restored and the previous boot journal explains the failure.

## Lab 203: Filesystems

Objectives: 203.1-203.3

1. Attach two empty virtual disks.
2. Create ext4 on one and mount it by UUID.
3. Add and verify fstab.
4. Create and remove a swap file.
5. Create a Btrfs subvolume and read-only snapshot if Btrfs is available.
6. Run non-destructive filesystem and SMART checks.
7. Configure an AutoFS map for an NFS test export.
8. Use the second empty disk for LUKS, then close and remove the lab mapping.

Success: all persistent mounts validate and no production device is touched.

## Lab 204: RAID and LVM

Objectives: 204.1-204.3

1. Attach three empty virtual disks.
2. Build RAID 1 with two devices.
3. Create an LVM PV, VG, LV, and filesystem on the array.
4. Extend the LV and filesystem.
5. Create an LVM snapshot.
6. Fail and replace one RAID member.
7. Inspect /proc/mdstat, mdadm detail, pvs, vgs, and lvs.
8. Remove the lab in reverse dependency order.

Success: the array returns to clean state and the filesystem remains readable.

## Lab 205: Network troubleshooting

Objectives: 205.1-205.3

1. Give a router VM two isolated interfaces.
2. Configure IPv4 and IPv6 addresses and routes.
3. Test link, neighbor, route, DNS, TCP, and application layers.
4. Capture DNS packets.
5. Introduce one wrong prefix, route, and resolver address at different times.
6. Diagnose each failure without immediately reading the answer.
7. Compare legacy and modern command names.

Success: each conclusion cites command output, not a guess.

## Lab 206: Maintenance

Objectives: 206.1-206.3

1. Download a small trusted source package and verify its checksum.
2. Build it under /usr/local and record installed files.
3. Back up a test directory with tar and rsync.
4. Preview a delete operation with rsync dry run.
5. Verify checksums and restore to a different path.
6. Send a maintenance message to another session.
7. Remove the locally built program cleanly.

Success: the restored data matches and the build can be inventoried.

## Lab 207: DNS

Objectives: 207.1-207.3

1. Draw the root, <code>ir</code>, <code>realsam.ir</code>, host, and delegated child-zone hierarchy.
2. Build separate recursive and authoritative servers.
3. Create a forward zone and identify owner, TTL, class, type, and RDATA in every record.
4. Query and explain SOA, NS, A, AAAA, CNAME, MX, PTR, TXT, SRV, and CAA.
5. Create a reverse declaration and zone for the isolated 203.0.113.0/24 network.
6. Configure consistent A and PTR data for <code>mail.realsam.ir</code> and demonstrate FCrDNS.
7. Explain why a real public PTR must be set or delegated by the IP-address provider.
8. Convert one IPv4 and one IPv6 address to their full reverse query owners.
9. Add a secondary server and compare SOA serials.
10. Protect transfer with TSIG.
11. Validate with <code>named-checkconf -z</code> and <code>named-checkzone</code>.
12. Confirm recursion is denied to an untrusted client.
13. Confirm unauthorized AXFR fails.
14. Create one delegated lab subdomain and identify required glue.
15. Trace a web request from the stub resolver through root, TLD, authoritative answer, routing, TLS, HTTP, and rendering.
16. Produce and diagnose NXDOMAIN, NODATA, REFUSED, and SERVFAIL in the isolated lab.
17. Explain RFC 2317 classless reverse delegation and the DNSSEC signing and parent DS process.

Success: forward and reverse authority, record meanings, resolution flow, recursion policy, transfer policy, and public rDNS ownership can all be explained and demonstrated.

## Lab 208: HTTP services

Objectives: 208.1-208.4

1. Publish www.realsam.ir with Apache.
2. Add logs, a protected directory, and redirect.
3. Create a self-signed test certificate with SAN and configure HTTPS.
4. Test SNI with openssl s_client.
5. Configure Squid with Safe_ports, one client subnet, and authentication.
6. Configure Nginx as a static server.
7. Configure Nginx as reverse proxy for two back ends.
8. Induce one syntax error in each service and prove the validator catches it.
9. Remove the errors and reload without unnecessary restart.

After this exam-focused lab, complete the [40 scenario-driven Topic 208 web-server labs](../docs/exam-202/topic-208/labs.md). They add Nginx and Apache request selection, Squid forward-proxy policy, reverse-proxy header trust, load balancing, PHP-FPM, certificate renewal, SELinux, monitoring, performance, recovery, and a full capstone.

Success: every service is validated and tested from a client.

## Lab 209: File sharing

Objectives: 209.1 and 209.2

1. Create a Samba group share.
2. Add a Samba user and test with smbclient.
3. Mount the share with a protected credentials file.
4. Create an NFS export with root_squash.
5. Mount it with NFSv4 and systemd automount.
6. Test an allowed and denied client.
7. Inspect Samba and NFS state and logs.
8. Explain what would change for an AD member server.

Success: Unix permissions and service access rules agree.

## Lab 210: Client management

Objectives: 210.1-210.4

1. Configure DHCP pool, fixed host, BOOTP options, and relay.
2. Capture a lease and DORA exchange.
3. Configure an IPv6 RA in an isolated lab.
4. Inspect one PAM stack and identify control flow.
5. Configure SSSD against the lab LDAP server.
6. Build an LDAP directory for realsam.ir.
7. Add, search, modify, rename, password-change, and delete a user.
8. Back up LDAP data and cn=config.
9. Test an ACL that protects password data.

Success: DHCP and directory clients work without weakening authentication safety.

## Lab 211: Email

Objectives: 211.1-211.3

1. Configure Postfix for realsam.ir with relay protection.
2. Add local aliases and a virtual alias.
3. Submit a message and inspect the queue and logs.
4. Add TLS and test SMTP STARTTLS.
5. Create a Sieve fileinto rule.
6. Configure Dovecot Maildir and IMAPS.
7. Authenticate and list a mailbox with doveadm.
8. Intentionally break an MX record or mailbox permission, diagnose it, and restore service.

Success: mail is not an open relay and TLS names match.

## Lab 212: Security

Objectives: 212.1-212.5

1. Configure IPv4 forwarding, a default-deny forward policy, and NAT.
2. Add one controlled port forward.
3. Save and restore firewall rules.
4. Compare active and passive FTP in packet capture.
5. Configure key-based SSH and disable root login.
6. Test local, remote, and dynamic forwarding.
7. Scan only the lab server and compare nmap with ss.
8. Configure a fail2ban test jail.
9. Create an OpenVPN tunnel between lab hosts.
10. Test route, DNS, certificate identity, and revocation behavior.

Success: a second SSH session remains available, firewall rollback works, and the VPN uses unique protected keys.

## Final capstone

Build a small realsam.ir environment with DNS, DHCP, web, file, LDAP, mail, routing, SSH, monitoring, backups, and VPN. Produce:

- network and service diagram
- address and DNS plan
- configuration inventory
- validation commands
- firewall matrix
- backup and restore evidence
- monitoring baseline
- incident and recovery record
- list of remaining risks

The capstone is complete only when another learner can reproduce it from the report.
