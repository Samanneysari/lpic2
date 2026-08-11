# Safety and Change Control

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

## Before every change

1. Confirm host, environment, package version, active configuration, and current time.
2. Keep console/out-of-band access and one existing SSH session.
3. Capture the effective configuration and exact files that will change.
4. Define a native syntax test, remote service test, rollback trigger, and rollback command.
5. Change one layer at a time. A DNS, firewall, TLS, proxy, and application change in one window destroys causality.

Baseline:

```bash
date --iso-8601=seconds
hostnamectl
sudo ss -lntp
sudo firewall-cmd --get-active-zones
sudo nginx -T >nginx.before.txt 2>&1
sudo apachectl -S >apache-vhosts.before.txt 2>&1
```

<!-- LINE-BY-LINE AUTO-SAFETY-01 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>date --iso-8601=seconds</code> | Prints the selected UTC or local date/time representation. |
| 2 | <code>hostnamectl</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |
| 3 | <code>sudo ss -lntp</code> | Displays listening or connected sockets with the requested protocol and process details. |
| 4 | <code>sudo firewall-cmd --get-active-zones</code> | Inspects or changes firewalld policy using the stated runtime or permanent option. |
| 5 | <code>sudo nginx -T &gt;nginx.before.txt 2&gt;&amp;1</code> | Invokes Nginx with the shown validation, build-information, or configuration-dump option. |
| 6 | <code>sudo apachectl -S &gt;apache-vhosts.before.txt 2&gt;&amp;1</code> | Validates, inspects, or controls Apache through its administration wrapper. |

The configuration captures can contain internal names and paths; protect them.

## Native validation gates

| Component | Validation before reload |
| --- | --- |
| Nginx | `sudo nginx -t` |
| Apache | `sudo apachectl configtest` |
| HAProxy | `sudo haproxy -c -f /etc/haproxy/haproxy.cfg` |
| PHP-FPM | distribution/version-specific `php-fpm --test` command |
| Certificate | `openssl x509` inspection plus live SNI test |
| SELinux label | `matchpathcon` and `restorecon -n` preview where applicable |

A syntax pass does not prove DNS, certificate chain, filesystem access, upstream health, or application correctness.

## Prohibited shortcuts

- Do not disable TLS verification to make an upstream green.
- Do not set web content or sockets to mode `777`.
- Do not disable SELinux to silence an AVC.
- Do not trust client-supplied `X-Forwarded-For` from the public Internet.
- Do not expose status, metrics, admin, or PHP-FPM endpoints publicly.
- Do not reload both proxy and application before collecting evidence.
- Do not delete logs during an incident merely to free space.
- Do not store private keys in Git.

## Minimal rollback record

```text
Change ID and owner:
Host/site and impact:
Versions and current state:
Files/directives changed:
Validation commands:
Rollback trigger:
Rollback files/commands:
UTC start/end and result:
```

<!-- LINE-BY-LINE AUTO-SAFETY-02 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>Change ID and owner:</code> | Sets or records the `Change ID and owner` field in this protocol or report example. |
| 2 | <code>Host/site and impact:</code> | Sets or records the `Host/site and impact` field in this protocol or report example. |
| 3 | <code>Versions and current state:</code> | Sets or records the `Versions and current state` field in this protocol or report example. |
| 4 | <code>Files/directives changed:</code> | Sets or records the `Files/directives changed` field in this protocol or report example. |
| 5 | <code>Validation commands:</code> | Sets or records the `Validation commands` field in this protocol or report example. |
| 6 | <code>Rollback trigger:</code> | Sets or records the `Rollback trigger` field in this protocol or report example. |
| 7 | <code>Rollback files/commands:</code> | Sets or records the `Rollback files/commands` field in this protocol or report example. |
| 8 | <code>UTC start/end and result:</code> | Sets or records the `UTC start/end and result` field in this protocol or report example. |
