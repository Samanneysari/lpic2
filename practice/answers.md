# LPIC-2 Practice Answer Key

## Exam 201-450

1. It suggests tasks blocked in uninterruptible sleep, often waiting for I/O.
2. lsof +L1, or an equivalent lsof search for deleted open files.
3. 30 days, before adding a safety margin.
4. Any two of Icinga 2, Nagios, collectd, MRTG, and Cacti.
5. No. bzImage means big zImage; it does not describe bzip2 compression.
6. /lib/modules/kernel-version/, using the running version from uname -r.
7. It removes old build output and configuration remnants to create a clean source tree.
8. initramfs or initrd.
9. modprobe resolves dependencies and uses module aliases and configuration.
10. /etc/sysctl.conf or a file under /etc/sysctl.d/.
11. systemctl edit UNIT.
12. multi-user.target.
13. The initramfs and its storage, encryption, and LVM components.
14. Repairing metadata while the kernel changes it can cause further corruption.
15. PXELINUX.
16. systemd-boot or GRUB for UEFI; U-Boot for embedded systems.
17. It controls filesystem-check order at boot.
18. swapon --show.
19. No. Standard supported XFS tools can grow but not shrink XFS.
20. It can be lost with the same disk, filesystem, host, compromise, or administrative error.
21. AutoFS, or a systemd automount unit.
22. cryptsetup open DEVICE NAME.
23. RAID 0.
24. /proc/mdstat.
25. It tells supported storage which blocks are no longer in use.
26. Logical Unit Number.
27. PV, then VG, then LV.
28. The snapshot becomes invalid or unusable.
29. No. It is normally a runtime change.
30. IPv6 Neighbor Discovery.
31. ss.
32. Routing tables plus ip rule policy rules.
33. getent follows NSS configuration and may use files, DNS, or other sources; dig queries DNS directly.
34. Link, address, route, DNS, transport, application.
35. It separates locally managed software from distribution-owned files.
36. Source origin, signature or checksum, dependencies, and build instructions.
37. A wrong source, destination, or slash can delete needed destination data.
38. A successful verified restore.
39. wall.
40. /etc/motd.

## Exam 202-450

41. allow-recursion and allow-query-cache, normally using a trusted-client ACL.
42. rndc reload.
43. Secondaries and caches compare it to determine whether zone data changed.
44. 113.0.203.in-addr.arpa.
45. Message authentication and integrity using a shared key; it does not encrypt the transfer.
46. No. DNSSEC authenticates DNS data and detects forged or modified answers.
47. apachectl configtest or the distribution-equivalent apache2ctl configtest.
48. Basic credentials are only encoded and can be read from unencrypted traffic.
49. Subject Alternative Name, or SAN.
50. In the file referenced by SSLCertificateFile, after the server certificate, typically as a full chain.
51. Define Safe_ports and deny !Safe_ports before allow rules.
52. Examples: cache_mem, cache_dir, or maximum_object_size; proxy_auth or an authentication helper.
53. No. default_server on the listen directive selects the default server.
54. Any two of Host, X-Real-IP, X-Forwarded-For, and X-Forwarded-Proto.
55. testparm.
56. Samba authorization cannot override the kernel's Unix ownership, mode, ACL, or security-policy denial.
57. It maps client root to an unprivileged identity on the export.
58. NFSv4.
59. It prevents the dynamic allocator from offering the same address to another client.
60. RA normally supplies the default router and on-link prefix information.
61. sufficient.
62. Root ownership and mode 0600.
63. ldapsearch.
64. LDIF.
65. The dynamic directory-based OpenLDAP configuration tree.
66. The first matching access rule determines the result, so a broad rule can shadow later rules.
67. reject_unauth_destination in smtpd_relay_restrictions or an equivalent safe policy.
68. newaliases.
69. fileinto.
70. An older mail filtering and delivery tool included for awareness.
71. IMAP.
72. doveconf -n.
73. net.ipv4.ip_forward=1.
74. A mistake can terminate access before rules are repaired; use console access, a second session, and rollback.
75. Passive mode.
76. Any two: isolated upload-only path, no execution, malware scanning, quotas, restrictive permissions, no direct web serving, and separate storage.
77. sshd -t.
78. -L creates local forwarding from the client side; -R creates a listening forward on the remote side.
79. No. Scanning requires ownership or explicit authorization.
80. It reacts to repeated log events and adds temporary blocking actions; it does not replace patches, strong authentication, or secure configuration.
81. CA certificate, server certificate, server private key, client certificate and key, CRL, and a tls-crypt key are valid examples; any four core objects earn credit.
82. The expected server identity and purpose, a trusted chain, validity, and revocation status.
