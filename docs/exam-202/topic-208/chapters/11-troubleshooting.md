# 11 — Web Incident Troubleshooting and Recovery

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

## Outcome

Bound failures across name, route, transport, TLS, virtual host, proxy, application, dependency, and storage before making changes.

## The first ten minutes

```bash
date --iso-8601=seconds
hostnamectl
systemctl --failed
sudo ss -lntp
df -hT
df -ih
sudo journalctl -p warning..alert --since '-15 minutes'
```

<!-- LINE-BY-LINE AUTO-11_TROUBLESHOOTING-01 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>date --iso-8601=seconds</code> | Prints the selected UTC or local date/time representation. |
| 2 | <code>hostnamectl</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |
| 3 | <code>systemctl --failed</code> | Inspects or changes the named systemd unit; reload is used only after validation. |
| 4 | <code>sudo ss -lntp</code> | Displays listening or connected sockets with the requested protocol and process details. |
| 5 | <code>df -hT</code> | Reports filesystem byte or inode capacity and usage. |
| 6 | <code>df -ih</code> | Reports filesystem byte or inode capacity and usage. |
| 7 | <code>sudo journalctl -p warning..alert --since '-15 minutes'</code> | Reads systemd journal records using the shown unit, priority, boot, or time filter. |

From an external client:

```bash
getent ahosts app.realsam.ir
curl -v --connect-timeout 3 --max-time 10 https://app.realsam.ir/health
```

<!-- LINE-BY-LINE AUTO-11_TROUBLESHOOTING-02 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>getent ahosts app.realsam.ir</code> | Uses the system NSS configuration to resolve the selected host or database entry. |
| 2 | <code>curl -v --connect-timeout 3 --max-time 10 https://app.realsam.ir/health</code> | Makes a bounded HTTP request with the shown name-resolution, header, output, or failure options. |

Capture exact error, address, negotiated protocol, certificate subject/SAN, status, responding headers, and timing.

## Layer table

| Observation | Next boundary |
| --- | --- |
| name fails | NSS, resolver, authoritative delegation/record/cache |
| no TCP connection | route, address, listener, firewall, load balancer |
| TCP reset | reject/no listener/process crash |
| TLS alert | SNI, certificate, protocol, trust, clock |
| wrong site | DNS/address, SNI, Host, default virtual host |
| 403 | authz, filesystem, ACL, SELinux, WAF/application |
| 404 | responding layer, root/alias/path rewrite/application route |
| 502 | proxy-to-upstream connection/protocol/response |
| 503 | deliberate unavailable/no healthy capacity/readiness |
| 504 | upstream exceeded proxy deadline |

These are directions, not absolute proofs.

## Compare direct paths

1. Application loopback/private port.
2. Local web server with `--resolve`.
3. Remote origin with `--resolve`.
4. Public DNS/edge path.

The first transition from success to failure identifies a boundary. Ensure each request uses the same method/path/headers and does not alter state.

## Packet evidence

```bash
sudo tcpdump -ni any -c 100 \
  'host 192.0.2.20 and (tcp port 80 or tcp port 443)'
```

<!-- LINE-BY-LINE AUTO-11_TROUBLESHOOTING-03 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo tcpdump -ni any -c 100 \</code> | Captures or displays packets matching the stated interface and filter. |
| 2 | <code>'host 192.0.2.20 and (tcp port 80 or tcp port 443)'</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |

Capture only with authorization; packets can contain credentials or personal data. Use a count/time boundary and protected storage.

## Common incidents

### Disk full

Check bytes, inodes, deleted-open files, logs/temp/cache/uploads, and growth. Do not delete unknown files. Restore capacity, fix writer/rotation/retention, then validate logging and requests.

### Configuration reload failed

The old process may keep serving. Read validator and journal, preserve the rejected config, fix one syntax/resource error, validate, reload, compare process generations, and run remote checks.

### All requests slow

Separate edge from origin, total from upstream timings, endpoint from global, and current from baseline. Check queue/worker saturation, dependencies, DNS/TLS, network loss, storage, scheduled tasks, and retries.

### One client fails

Compare DNS resolver/cache, IPv4 versus IPv6, path/MTU, proxy/VPN, certificate trust/time, cookies/session, geolocation/CDN POP, and security policy. Do not restart the server because one client reports an error.

### Compromise suspected

Stop cleanup. Preserve volatile state, sessions, processes, sockets, logs, files/timestamps, account/key changes, systemd/cron persistence, and upstream/CDN evidence under the incident plan. A privileged compromise may require trusted rebuild.

## Validation after recovery

- Native configuration valid.
- Unit/process/listener healthy with no loop.
- Correct certificate and DNS at every expected edge.
- Real application transaction succeeds.
- Latency/error and upstream health return to baseline.
- Logs, monitoring, backup, renewal, and security enforcement work.
- Rollback/temporary mitigation owner and expiry recorded.

## Review

1. Why compare four request paths?
2. Why can a failed reload leave service available?
3. What does a 504 imply and not prove?
4. Why avoid restarting for a one-client failure?
5. When should ordinary troubleshooting become security incident response?
