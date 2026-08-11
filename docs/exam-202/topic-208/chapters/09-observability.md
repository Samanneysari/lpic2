# 09 — Logging, Metrics, Monitoring, and Tracing

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

## Outcome

Build evidence that follows one request across edge, proxy, gateway, application, and dependencies without leaking secrets.

## Request ID

At the trusted edge, accept a request ID only if it meets a strict format or generate a new one. Forward the controlled ID to upstreams and return it to the client for support correlation. Do not treat it as authentication.

Nginx concept:

```nginx
proxy_set_header X-Request-ID $request_id;
add_header X-Request-ID $request_id always;
```

<!-- LINE-BY-LINE AUTO-09_OBSERVABILITY-01 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>proxy_set_header X-Request-ID $request_id;</code> | Overwrites the named request header before forwarding it upstream. |
| 2 | <code>add_header X-Request-ID $request_id always;</code> | Adds the named response header under the directive's status and inheritance rules. |

The application must log the same value. If a CDN already supplies one, define ownership and validation.

## Access-log fields

Record timestamp with timezone, virtual host, method, normalized path policy, protocol, status, bytes, total duration, upstream address/status/timings, cache result, and controlled request ID. Client address must represent the trusted proxy chain.

Avoid raw authorization, cookies, tokens, passwords, request bodies, and sensitive query strings. Logs are production data with retention and access controls.

## Error logs and journal

```bash
sudo journalctl -u nginx.service \
  --since '2026-08-11 10:00:00 UTC' \
  --until '2026-08-11 10:10:00 UTC' \
  -o short-iso-precise
sudo tail -n 200 /var/log/nginx/app.error.log
```

<!-- LINE-BY-LINE AUTO-09_OBSERVABILITY-02 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo journalctl -u nginx.service \</code> | Reads systemd journal records using the shown unit, priority, boot, or time filter. |
| 2 | <code>--since '2026-08-11 10:00:00 UTC' \</code> | Adds the shown option or argument to the continued command; the trailing backslash continues it when present. |
| 3 | <code>--until '2026-08-11 10:10:00 UTC' \</code> | Adds the shown option or argument to the continued command; the trailing backslash continues it when present. |
| 4 | <code>-o short-iso-precise</code> | Adds the shown option or argument to the continued command; the trailing backslash continues it when present. |
| 5 | <code>sudo tail -n 200 /var/log/nginx/app.error.log</code> | Displays the requested final lines of a log or file. |

Use a bounded window. Debug logging can expose sensitive data and create load; enable it for the narrowest site/client/time and remove it after capture.

## Metrics

Four golden signals:

- latency;
- traffic;
- errors;
- saturation.

Add certificate days remaining, DNS correctness, backend health, connection states, worker/queue capacity, TLS handshake errors, response classes, upstream latency, cache results, process restarts, file descriptors, disk bytes/inodes, and log pipeline health.

Status endpoints must bind to loopback/management networks with access controls. Metrics often reveal names, routes, versions, and load.

## Synthetic checks

Test from outside the server:

1. normal DNS resolution;
2. TCP/TLS with correct SNI and hostname validation;
3. expected redirect and headers;
4. application transaction and response semantics;
5. optional write/read cleanup in a dedicated test tenant.

An internal localhost check misses DNS, edge/CDN, firewall, certificate name, and external routing.

## Alerts

Alert on sustained user impact or exhaustion with context and runbook. Example: elevated 5xx rate plus request volume and affected host/path. Avoid paging on one transient backend failure when redundancy works.

Every alert should state site, environment, UTC window, current value/baseline, likely layer, dashboard/log query, owner, and immediate safe checks.

## Log rotation

Processes keep writing to open file descriptors after rename. Use service-supported reopen signals or packaged logrotate integration. `copytruncate` can lose/duplicate lines and should not be chosen casually. Check deleted-open files and free space.

```bash
sudo logrotate --debug /etc/logrotate.d/nginx
sudo lsof +L1 | grep -E 'nginx|httpd|haproxy'
```

<!-- LINE-BY-LINE AUTO-09_OBSERVABILITY-03 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo logrotate --debug /etc/logrotate.d/nginx</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |
| 2 | <code>sudo lsof +L1 &#124; grep -E 'nginx&#124;httpd&#124;haproxy'</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |

Debug mode should not rotate. Test real rotation in a lab and verify processes write to new files.

## Scenario: monitoring says 200 but users fail

Check whether the monitor uses localhost, IP instead of name/SNI, a shallow endpoint, privileged bypass header, different resolver, cached response, or no response-content validation. Monitoring must resemble the user path.

## Review

1. Why generate request IDs at a trusted boundary?
2. Which log fields expose upstream delay?
3. Why protect metrics endpoints?
4. What does a localhost check miss?
5. Why can naive log rotation fail to free space?
