# Topic 208 Deep Learning Path: Web Servers and Proxies

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

This is the detailed, production-oriented companion to [Topic 208: HTTP Services](../topic-208-http-services.md). It starts with HTTP fundamentals and continues through Nginx, Apache HTTP Server, TLS, Squid, reverse proxies, load balancing, PHP-FPM, logging, security, performance, troubleshooting, and recovery on Linux.

The parent Topic 208 chapter remains the exam-focused reference. This path adds the deeper explanation and operational scenarios needed to administer real services.

The primary lab platform is Rocky Linux or AlmaLinux 9. Ubuntu Server differences are called out where package names, service units, paths, or defaults differ.

> [!CAUTION]
> A web-server, DNS, TLS, routing, or firewall change can make every site unavailable. Keep console access and an existing administrative session, validate configuration before reload, define rollback, and test from an independent client.

## LPIC-2 objective map

| Objective | Official core | Chapters |
| --- | --- | --- |
| 208.1 | Apache configuration, logs, access control, authentication, scripting, resource limits, virtual hosts, and redirects | [HTTP](chapters/01-http.md), [Apache](chapters/03-apache.md), [application gateways](chapters/06-application-gateways.md), [performance](chapters/08-performance.md), [observability](chapters/09-observability.md) |
| 208.2 | Apache HTTPS, keys, CSRs, certificates, chains, SNI, protocols, ciphers, and TLS security | [TLS and ACME](chapters/04-tls-acme.md), [Apache](chapters/03-apache.md), [TLS checklist](checklists/tls.md) |
| 208.3 | Squid configuration, ACLs, access policy, authentication, and resource use | The exam-focused [208.3 section](../topic-208-http-services.md#2083-squid-caching-proxy) plus the forward-proxy scenarios in [labs.md](labs.md) and [practice questions](practice-questions.md) |
| 208.4 | Nginx as a basic web server and reverse proxy | [Nginx](chapters/02-nginx.md), [reverse proxy and load balancing](chapters/05-proxy-load-balancing.md), [troubleshooting](chapters/11-troubleshooting.md) |

HAProxy, ACME automation, PHP-FPM, CDN design, advanced hardening, capacity engineering, and production operations are clearly useful extensions, but they go beyond the minimum LPIC-2 4.5 objective wording.

## Learning path

| Chapter | Outcome |
| --- | --- |
| [00 — Lab and operating model](chapters/00-lab.md) | Build a safe two-server lab and deploy the first site. |
| [01 — HTTP from request to response](chapters/01-http.md) | Understand URLs, methods, headers, status, connections, proxies, and caching. |
| [02 — Nginx administration](chapters/02-nginx.md) | Operate server blocks, locations, files, modules, reloads, and logs. |
| [03 — Apache administration](chapters/03-apache.md) | Operate virtual hosts, modules, directory policy, MPMs, and overrides. |
| [04 — TLS and ACME](chapters/04-tls-acme.md) | Build, validate, renew, and troubleshoot certificate deployments. |
| [05 — Reverse proxy and load balancing](chapters/05-proxy-load-balancing.md) | Preserve client identity, define health, balance safely, and drain backends. |
| [06 — Application gateways and PHP-FPM](chapters/06-application-gateways.md) | Connect web front ends to Unix/TCP application workers securely. |
| [07 — Web-server security](chapters/07-security.md) | Reduce exposure without breaking intended behavior. |
| [08 — Performance and capacity](chapters/08-performance.md) | Locate network, TLS, worker, upstream, storage, and application bottlenecks. |
| [09 — Logging and monitoring](chapters/09-observability.md) | Build correlated logs, metrics, synthetic checks, and actionable alerts. |
| [10 — DNS, CDN, and client IP](chapters/10-dns-cdn.md) | Operate authoritative records, reverse proxies, trusted headers, and origin protection. |
| [11 — Troubleshooting and recovery](chapters/11-troubleshooting.md) | Resolve multi-layer incidents with evidence and rollback. |
| [12 — Production operations](chapters/12-production-operations.md) | Deploy, patch, renew, back up, restore, and decommission safely. |

Practice:

- [40 hands-on labs](labs.md)
- [90 exercises](practice-questions.md) and [answer key](practice-answers.md)
- [Deployment](checklists/deployment.md), [TLS](checklists/tls.md), and [incident](checklists/incident.md) checklists
- [Official references](references.md)

## Chapter pattern

Every chapter follows: mental model → production scenario → read-only evidence → safe configuration → line-by-line explanation → validation → rollback → lab → review.

## Conventions

- `$` is an unprivileged shell and `#` is a root prompt; do not type the prompt.
- Examples use `app.realsam.ir` and documentation networks such as `192.0.2.0/24`.
- Replace `<placeholders>` before use.
- Commands and directives vary by installed release; local manuals and native validators are authoritative.
- Never place real credentials, cookies, private keys, tokens, or production logs in this repository.

Return to the [LPIC-2 guide](../../../README.md), use the [Topic 208 safety rules](safety.md), and complete the exam-focused chapter before treating these production extensions as required exam material.
