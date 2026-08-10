# LPIC-2 Complete Study Guide

This repository is a beginner-friendly study guide for the Linux Professional Institute LPIC-2 certification.

It follows LPIC-2 objectives version 4.5:

- Exam 201-450
- Exam 202-450

The official objectives are available at [Linux Professional Institute](https://www.lpi.org/our-certifications/exam-201-202-objectives/).

> This guide explains the exam subjects in simple English. It does not contain real exam questions and it does not replace hands-on practice.

## How to use this guide

1. Read the topics in order.
2. Type every command in a test virtual machine.
3. Complete the labs after each topic.
4. Review the glossary when a term is unclear.
5. Take the practice test.
6. Read the answer key only after completing the test.

Never run storage, firewall, bootloader, or deletion commands on a production server while learning.

## Example environment

Examples use the domain **realsam.ir** and its subdomains:

| Service | Example name |
|---|---|
| Authoritative DNS | ns1.realsam.ir, ns2.realsam.ir |
| Web service | www.realsam.ir |
| Mail service | mail.realsam.ir |
| File service | files.realsam.ir |
| Directory service | ldap.realsam.ir |
| Proxy service | proxy.realsam.ir |
| VPN service | vpn.realsam.ir |
| Back-end web nodes | backend1.realsam.ir, backend2.realsam.ir |

Private labs use addresses such as 10.20.0.0/24. Public examples use the documentation ranges 192.0.2.0/24, 198.51.100.0/24, and 203.0.113.0/24.

## Exam 201-450

| Objectives | Topic | Guide |
|---|---|---|
| 200.1-200.2 | Capacity Planning | [Topic 200](docs/exam-201/topic-200-capacity-planning.md) |
| 201.1-201.3 | Linux Kernel | [Topic 201](docs/exam-201/topic-201-linux-kernel.md) |
| 202.1-202.3 | System Startup | [Topic 202](docs/exam-201/topic-202-system-startup.md) |
| 203.1-203.3 | Filesystems and Devices | [Topic 203](docs/exam-201/topic-203-filesystems.md) |
| 204.1-204.3 | Advanced Storage | [Topic 204](docs/exam-201/topic-204-storage.md) |
| 205.1-205.3 | Network Configuration | [Topic 205](docs/exam-201/topic-205-networking.md) |
| 206.1-206.3 | System Maintenance | [Topic 206](docs/exam-201/topic-206-maintenance.md) |

## Exam 202-450

| Objectives | Topic | Guide |
|---|---|---|
| 207.1-207.3 | DNS | [Topic 207](docs/exam-202/topic-207-dns.md) |
| 208.1-208.4 | HTTP Services | [Topic 208](docs/exam-202/topic-208-http-services.md) |
| 209.1-209.2 | File Sharing | [Topic 209](docs/exam-202/topic-209-file-sharing.md) |
| 210.1-210.4 | Network Client Management | [Topic 210](docs/exam-202/topic-210-client-management.md) |
| 211.1-211.3 | Email Services | [Topic 211](docs/exam-202/topic-211-email.md) |
| 212.1-212.5 | System Security | [Topic 212](docs/exam-202/topic-212-security.md) |

## Complete objective checklist

The [objective coverage checklist](OBJECTIVES.md) maps all 41 objectives and their official weights to this guide.

## Practice material

- [Hands-on labs](labs/README.md)
- [Practice questions](practice/questions.md)
- [Answer key](practice/answers.md)
- [Distribution differences](docs/distribution-notes.md)
- [Glossary](GLOSSARY.md)
- [Official references](REFERENCES.md)
- [Optional LAMP, LEMP, and WordPress appendix](appendices/web-stacks.md)

## Safe command pattern

For every service:

1. Back up the configuration.
2. Make one controlled change.
3. Test syntax.
4. Reload when possible.
5. Check status and logs.
6. Test from a client.
7. Roll back when validation fails.

~~~bash
sudo named-checkconf -z
sudo apachectl configtest
sudo nginx -t
sudo squid -k parse
sudo dhcpd -t -cf /etc/dhcp/dhcpd.conf
~~~

## Repository history

The original notes are preserved at [legacy/lpic2-original.md](legacy/lpic2-original.md). The root [lpic2.md](lpic2.md) is now a compatibility index for the corrected modular guide.
