# LPIC-2 Practice Questions

These are original study questions, not real LPI exam questions. Answer them without opening the guide.

## Exam 201-450

### Objective 200.1

1. In vmstat output, what does a consistently high b value usually suggest?
2. A filesystem is full, but du shows much less usage than df. Which command helps find deleted files that are still open?

### Objective 200.2

3. A filesystem has 120 GB free and grows by 4 GB per day. What is its simple capacity breakpoint?
4. Name two monitoring systems listed in the LPIC-2 objectives.

### Objective 201.1

5. Does bzImage mean that a kernel image is compressed with bzip2? Explain.
6. Where are modules for the running kernel normally stored?

### Objective 201.2

7. What is the purpose of make mrproper before a clean kernel configuration?
8. After installing modules for a new kernel, which early-boot image may need to be created or updated?

### Objective 201.3

9. What important behavior does modprobe provide that insmod does not normally provide?
10. Where should an administrator place persistent sysctl settings?

### Objective 202.1

11. What command creates a systemd override without editing the vendor unit?
12. Which systemd target normally represents a non-graphical multi-user system?

### Objective 202.2

13. A kernel starts but cannot find the encrypted LVM root filesystem. Which early-boot component should be checked first?
14. Why should fsck not normally run against a mounted writable filesystem?

### Objective 202.3

15. Which loader is associated with BIOS network boot: ISOLINUX or PXELINUX?
16. Name one boot manager commonly used on UEFI systems and one loader common on embedded systems.

### Objective 203.1

17. What is the sixth field in an /etc/fstab entry used for?
18. Which command displays currently active swap devices?

### Objective 203.2

19. Can an XFS filesystem be shrunk using standard supported tools?
20. Why is a Btrfs snapshot on the same disk not a complete backup?

### Objective 203.3

21. Which service mounts a filesystem when its configured path is accessed?
22. Which command opens a LUKS device and creates a device-mapper name?

### Objective 204.1

23. Which RAID level in the objectives offers striping with no redundancy?
24. Which virtual file shows Linux software RAID synchronization state?

### Objective 204.2

25. What is the main purpose of fstrim?
26. In a SAN, what does LUN mean?

### Objective 204.3

27. Put these LVM objects in construction order: LV, PV, VG.
28. What happens to a classic LVM snapshot when its allocated copy-on-write space fills?

### Objective 205.1

29. Does ip address add normally create persistent configuration after reboot?
30. What IPv6 mechanism replaces IPv4 ARP?

### Objective 205.2

31. Which command is normally preferred over netstat for current socket information?
32. What combination of iproute2 features supports policy-based routing?

### Objective 205.3

33. Why can getent hosts and dig return different results?
34. Put these checks in a useful order: application, link, DNS, address, route, transport.

### Objective 206.1

35. Why is /usr/local a useful prefix for software built by an administrator?
36. What should be verified before building downloaded source code?

### Objective 206.2

37. Why should rsync --delete normally be tested with a dry run first?
38. What action proves that a backup is usable?

### Objective 206.3

39. Which command sends a message to currently logged-in terminal users?
40. Which file normally contains a post-login message: /etc/issue or /etc/motd?

## Exam 202-450

### Objective 207.1

41. Which BIND directives should restrict recursive service to trusted clients?
42. Which command asks a running BIND server to reload through its control channel?

### Objective 207.2

43. Why must an SOA serial increase after a zone change?
44. What is the reverse IPv4 zone name for 203.0.113.0/24?

### Objective 207.3

45. What does TSIG provide for a DNS zone transfer?
46. Does DNSSEC encrypt DNS answers? What problem does it solve?

### DNS architecture and rDNS deep dive

- **DNS-1:** Starting with an empty recursive cache, list the authorities contacted to resolve <code>www.realsam.ir</code>.
- **DNS-2:** What is the difference between a stub resolver, recursive resolver, and authoritative server?
- **DNS-3:** Name the five logical fields of a resource record and explain what an RRset is.
- **DNS-4:** Explain the purpose and one important rule for SOA, NS, A, AAAA, CNAME, MX, PTR, TXT, and SRV.
- **DNS-5:** What exact PTR owner name is queried for IPv4 address 203.0.113.25?
- **DNS-6:** Why can the owner of <code>realsam.ir</code> usually not set public rDNS only through the domain registrar?
- **DNS-7:** What two lookups demonstrate forward-confirmed reverse DNS?
- **DNS-8:** How do NXDOMAIN and a NOERROR response with no requested-type answer differ?
- **DNS-9:** After DNS returns an address, name four layers that must still work before a user sees an HTTPS page.
- **DNS-10:** Why is a matching mail-server PTR useful but insufficient as proof that a message is legitimate?

### Objective 208.1

47. Which command should be run before reloading Apache configuration?
48. Why should Basic Authentication not be used over plain HTTP?

### Objective 208.2

49. What certificate field allows www.realsam.ir and realsam.ir to appear in one certificate?
50. On current Apache 2.4, where should intermediate certificates normally be placed?

### Objective 208.3

51. Which Squid ACL pattern prevents requests to unexpected destination ports?
52. Name one Squid resource control and one authentication concept required by the objective.

### Objective 208.4

53. Does server_name _ alone make an Nginx virtual server the default?
54. Name two headers commonly passed from Nginx to an HTTP back end.

### Objective 209.1

55. Which command validates smb.conf?
56. Why can a Samba allow rule still fail when Unix filesystem permissions are restrictive?

### Objective 209.2

57. What security effect does root_squash have?
58. Which NFS version normally uses a unified namespace and TCP port 2049?

### Objective 210.1

59. Why should a fixed DHCP address be outside the dynamic range?
60. Why is Router Advertisement still important when DHCPv6 is used?

### Objective 210.2

61. Which PAM control flag can allow success to complete a stack when no previous required module failed?
62. What permissions should protect /etc/sssd/sssd.conf?

### Objective 210.3

63. Which command performs an LDAP search?
64. What format represents LDAP entries and changes as text?

### Objective 210.4

65. What is cn=config?
66. Why does the order of OpenLDAP access rules matter?

### Objective 211.1

67. Which Postfix restriction is central to rejecting unauthorized relay destinations?
68. Which command rebuilds the local aliases database?

### Objective 211.2

69. Which Sieve action delivers a message into a named mailbox?
70. What is procmail in the context of the objective?

### Objective 211.3

71. Which protocol normally keeps server-side folders synchronized: IMAP or POP3?
72. Which Dovecot command displays the effective non-default configuration?

### Objective 212.1

73. Which kernel setting enables IPv4 packet forwarding?
74. Why is flushing firewall rules over the only SSH session unsafe?

### Objective 212.2

75. In which FTP mode does the client create the data connection to a server-selected port?
76. Give two protections for an anonymous upload directory.

### Objective 212.3

77. Which command validates sshd_config before reload?
78. What is the difference between ssh -L and ssh -R?

### Objective 212.4

79. May you scan any public server with nmap simply because the tool is installed?
80. What does fail2ban do, and what security task does it not replace?

### Objective 212.5

81. Name four PKI files or objects needed by a certificate-based OpenVPN deployment.
82. What should a client verify about the VPN server certificate?
