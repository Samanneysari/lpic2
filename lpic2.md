# LPIC-2 Complete Beginner Study Guide

This is the main entrance to the active LPIC-2 guide. It covers the published objective codes for LPIC-2 version 4.5:

- Exam 201-450
- Exam 202-450

The original 1,703-line document is still available unchanged at [legacy/lpic2-original.md](legacy/lpic2-original.md). It was preserved so none of the author's earlier explanations were lost. The active chapters keep the useful ideas, correct technical and security problems, and organize the material by the official exam objectives.

## Is this guide complete?

It covers all 41 objective codes listed in [OBJECTIVES.md](OBJECTIVES.md). Each active topic now starts with the theory a beginner needs before commands appear. Every non-empty command or configuration line shown in the study chapters has an explanation immediately below its code block.

"Complete" has a clear boundary. This guide covers the knowledge areas and practical commands required by objectives 201-450 and 202-450. It cannot document every option of every Linux command, every distribution release, or every production architecture. When the guide shows a command, it explains that command line; use the manual page and the linked official documentation for options beyond the example.

## How every chapter is organized

Read each topic from top to bottom:

1. **What it is:** the service, subsystem, or concept is defined in plain English.
2. **How it works:** the important components and the path followed by data are explained.
3. **Terms and files:** names, ports, configuration files, and processes are introduced.
4. **Safe procedure:** the task is divided into ordered steps.
5. **Command or configuration block:** a working example is shown.
6. **Line-by-line explanation:** every non-empty line in that block is explained directly below it.
7. **Validation:** syntax, service state, logs, and client behavior are checked.
8. **Troubleshooting and security:** common causes and safe operating rules are discussed.
9. **Exam checklist and mini lab:** the official terms are reviewed and the skill is practiced.

Do not skip the explanation tables. Typing a command without understanding its target, privilege, persistence, and validation is not system administration.

## Lab naming and address rules

All service names use realsam.ir or one of its subdomains, such as:

| Purpose | Name |
|---|---|
| DNS | ns1.realsam.ir and ns2.realsam.ir |
| Website | www.realsam.ir |
| Application proxy | app.realsam.ir |
| Mail | mail.realsam.ir |
| LDAP | ldap.realsam.ir |
| File server | files.realsam.ir |
| VPN | vpn.realsam.ir |

Private lab networks use RFC 1918 addresses such as 10.20.0.0/24. Examples that look public use documentation-only ranges such as 192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24, and 2001:db8::/32.

## Exam 201-450: Advanced system administration

| Official objective | What you learn | Chapter |
|---|---|---|
| 200.1-200.2 | Measure current resource use and predict future needs | [Topic 200: Capacity Planning](docs/exam-201/topic-200-capacity-planning.md) |
| 201.1-201.3 | Kernel components, compilation, modules, and runtime management | [Topic 201: Linux Kernel](docs/exam-201/topic-201-linux-kernel.md) |
| 202.1-202.3 | Boot process, recovery, SysV init, and systemd | [Topic 202: System Startup](docs/exam-201/topic-202-system-startup.md) |
| 203.1-203.3 | Filesystems, mounting, options, and maintenance | [Topic 203: Filesystems and Devices](docs/exam-201/topic-203-filesystems.md) |
| 204.1-204.3 | RAID, storage access, LVM, and advanced block storage | [Topic 204: Advanced Storage](docs/exam-201/topic-204-storage.md) |
| 205.1-205.3 | Interfaces, routing, troubleshooting, and virtual networking | [Topic 205: Network Configuration](docs/exam-201/topic-205-networking.md) |
| 206.1-206.3 | Source builds, backup operations, and user notification | [Topic 206: System Maintenance](docs/exam-201/topic-206-maintenance.md) |

## Exam 202-450: Network services

| Official objective | What you learn | Chapter |
|---|---|---|
| 207.1-207.3 | BIND, zones, delegation, transfers, TSIG, and DNSSEC | [Topic 207: DNS](docs/exam-202/topic-207-dns.md) |
| 208.1-208.4 | Apache, TLS, Squid, Nginx, and reverse proxying | [Topic 208: HTTP Services](docs/exam-202/topic-208-http-services.md) |
| 209.1-209.2 | Samba/SMB and NFS server and client administration | [Topic 209: File Sharing](docs/exam-202/topic-209-file-sharing.md) |
| 210.1-210.4 | DHCP, PAM, NSS, LDAP clients, and OpenLDAP | [Topic 210: Network Client Management](docs/exam-202/topic-210-client-management.md) |
| 211.1-211.3 | Postfix, mailbox access, Dovecot, and Sieve | [Topic 211: Email Services](docs/exam-202/topic-211-email.md) |
| 212.1-212.5 | Routing, FTP, SSH, firewalling, scanning, and OpenVPN | [Topic 212: System Security](docs/exam-202/topic-212-security.md) |

## Practical material

- [Hands-on labs](labs/README.md)
- [Practice questions](practice/questions.md)
- [Answer key](practice/answers.md)
- [Glossary](GLOSSARY.md)
- [Distribution differences](docs/distribution-notes.md)
- [Official references](REFERENCES.md)
- [Optional LAMP, LEMP, and WordPress appendix](appendices/web-stacks.md)

## Safety rule

Use a disposable virtual machine or an isolated lab. Storage creation, RAID/LVM changes, bootloader installation, firewall replacement, PAM changes, and directory imports can make a machine unavailable or destroy data. Read the explanation, identify the exact target, keep recovery access, back up the current state, validate the change, and test rollback.

Begin with [Topic 200](docs/exam-201/topic-200-capacity-planning.md), or use [README.md](README.md) for the compact repository overview.
