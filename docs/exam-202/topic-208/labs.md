# Hands-On Labs

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

Run only on disposable VMs. Use `web1` and `client1`; preserve a working admin session and snapshot. Each report needs impact, UTC timeline, evidence, hypothesis, safe change, rollback, local/remote validation, root cause, and prevention.

| ID | Lab | Required result |
| --- | --- | --- |
| W01 | Deploy a static Nginx virtual host | Host-based remote response and per-site logs |
| W02 | Deploy equivalent Apache virtual host | `apachectl -S`, correct filesystem policy |
| W03 | Wrong default host | Prove address/SNI/Host selection |
| W04 | Nginx `root` versus `alias` | Predict and verify mapped paths |
| W05 | Apache section merging | Explain final access decision |
| W06 | Missing parent traversal | Find denial with `namei` |
| W07 | Wrong SELinux content label | AVC plus persistent repair |
| W08 | Graceful reload | Observe worker/process generation |
| W09 | Rejected reload | Old service remains; repair without restart |
| W10 | Reverse proxy to loopback app | Preserve Host/scheme/request ID |
| W11 | `proxy_pass` slash behavior | Build route test matrix |
| W12 | Unix-socket gateway | Correct owner/mode/label/namespace |
| W13 | PHP-FPM pool saturation | Queue/latency evidence before sizing |
| W14 | Intermittent 502 | Correlate proxy and backend evidence |
| W15 | Upstream 504 | Bound deadline versus application time |
| W16 | HAProxy two-backend pool | Health checks and one-node drain |
| W17 | Unsafe health endpoint | Replace shallow/expensive check |
| W18 | Retry of non-idempotent request | Demonstrate risk in a harmless lab app |
| W19 | Self-signed lab CA | Correct trust without `--insecure` |
| W20 | SNI certificate selection | Same address, two names/certificates |
| W21 | Incomplete certificate chain | Detect with live verification |
| W22 | Certbot renewal dry run | Verify timer/hook and live reload plan |
| W23 | HTTPS redirect loop | Correct trusted original-scheme handling |
| W24 | Conservative HSTS | Short policy, rollback implications |
| W25 | DNS migration | TTL timeline and multi-resolver validation |
| W26 | CDN-style proxy | Trusted client-IP header only from proxy |
| W27 | Origin bypass | Firewall/private-path mitigation |
| W28 | Cache-key mistake | Prevent harmless simulated user mixing |
| W29 | Large upload failure | Identify exact rejecting layer |
| W30 | Disk bytes full | Safe relief and retention correction |
| W31 | Inodes full | Separate inode from byte evidence |
| W32 | Deleted-open access log | Reopen and verify freed space |
| W33 | Load-test static and dynamic paths | Bounded ramp and dependency observation |
| W34 | Hourly latency spike | Correlate timer/logrotate/batch evidence |
| W35 | External synthetic check | DNS, TLS, HTTP, content, timing |
| W36 | Full capstone | Two backends, TLS, logs, security, restore, six seeded faults |
| W37 | Safe Squid forward proxy | Only the approved lab subnet and safe destination ports can use it |
| W38 | Squid authentication | Valid users pass; missing or invalid credentials are rejected and logged |
| W39 | Squid ACL ordering failure | Demonstrate first-match behavior, repair the rule order, and prove deny-all fallback |
| W40 | Squid cache and resource limits | Observe access/cache logs and enforce bounded memory and object-size policy |

## Safe backend for proxy labs

On a lab-only host, Python's simple HTTP server can demonstrate transport, not production behavior:

```bash
python3 -m http.server 8080 --bind 127.0.0.1 --directory /srv/lab-backend
```

<!-- LINE-BY-LINE AUTO-LABS-01 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>python3 -m http.server 8080 --bind 127.0.0.1 --directory /srv/lab-backend</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |

It lacks production security, lifecycle, dynamic health, and performance controls. Run it as an unprivileged user under a temporary systemd unit or foreground terminal, never on a public interface.

## Report template

```text
Lab ID / operator:
UTC start/end:
User-visible impact:
Versions/config paths:
Safety and rollback:
Evidence and predictions:
Change:
Native validator:
Local/app/proxy/public validation:
Root cause and contributors:
Prevention/monitoring:
```

<!-- LINE-BY-LINE AUTO-LABS-02 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>Lab ID / operator:</code> | Sets or records the `Lab ID / operator` field in this protocol or report example. |
| 2 | <code>UTC start/end:</code> | Sets or records the `UTC start/end` field in this protocol or report example. |
| 3 | <code>User-visible impact:</code> | Sets or records the `User-visible impact` field in this protocol or report example. |
| 4 | <code>Versions/config paths:</code> | Sets or records the `Versions/config paths` field in this protocol or report example. |
| 5 | <code>Safety and rollback:</code> | Sets or records the `Safety and rollback` field in this protocol or report example. |
| 6 | <code>Evidence and predictions:</code> | Sets or records the `Evidence and predictions` field in this protocol or report example. |
| 7 | <code>Change:</code> | Sets or records the `Change` field in this protocol or report example. |
| 8 | <code>Native validator:</code> | Sets or records the `Native validator` field in this protocol or report example. |
| 9 | <code>Local/app/proxy/public validation:</code> | Sets or records the `Local/app/proxy/public validation` field in this protocol or report example. |
| 10 | <code>Root cause and contributors:</code> | Sets or records the `Root cause and contributors` field in this protocol or report example. |
| 11 | <code>Prevention/monitoring:</code> | Sets or records the `Prevention/monitoring` field in this protocol or report example. |
