# 08 — Performance and Capacity

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

## Outcome

Locate latency and capacity constraints across client, DNS, network, TLS, web server, gateway, application, dependencies, and storage.

## Define the service result

Measure request rate, concurrency, response-size distribution, error rate, and latency percentiles by endpoint. An average hides tail latency. Separate edge time, connect time, TLS time, time to first byte, and total time:

```bash
curl --silent --show-error --output /dev/null \
  --write-out 'dns=%{time_namelookup} connect=%{time_connect} tls=%{time_appconnect} first=%{time_starttransfer} total=%{time_total} code=%{http_code}\n' \
  https://app.realsam.ir/health
```

<!-- LINE-BY-LINE AUTO-08_PERFORMANCE-01 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>curl --silent --show-error --output /dev/null \</code> | Makes a bounded HTTP request with the shown name-resolution, header, output, or failure options. |
| 2 | <code>--write-out 'dns=%{time_namelookup} connect=%{time_connect} tls=%{time_appconnect} first=%{time_starttransfer} total=%{time_total} code=%{http_code}\n' \</code> | Adds the shown option or argument to the continued command; the trailing backslash continues it when present. |
| 3 | <code>https://app.realsam.ir/health</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |

These timings are from one client and one request, not a capacity benchmark.

## Layer evidence

```bash
uptime
vmstat 1 10
pidstat -dur 1 10
iostat -xz 1 10
ss -s
sudo ss -lntp
```

<!-- LINE-BY-LINE AUTO-08_PERFORMANCE-02 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>uptime</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |
| 2 | <code>vmstat 1 10</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |
| 3 | <code>pidstat -dur 1 10</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |
| 4 | <code>iostat -xz 1 10</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |
| 5 | <code>ss -s</code> | Displays listening or connected sockets with the requested protocol and process details. |
| 6 | <code>sudo ss -lntp</code> | Displays listening or connected sockets with the requested protocol and process details. |

Correlate host utilization, saturation, errors, and application latency. High load can be blocked storage. Low host CPU can hide one saturated worker, cgroup quota, backend queue, or lock.

## Web-server limits

Inspect:

- workers/processes/threads and live connections;
- open-file limits and descriptor count;
- listen backlog and kernel drops;
- keepalive lifetime;
- request/body buffers and temp-file I/O;
- TLS handshakes and session reuse;
- upstream connection pools, queues, health, and retries.

```bash
systemctl show nginx.service -p LimitNOFILE -p TasksMax
cat /proc/$(cat /run/nginx.pid)/limits
sudo ls /proc/$(cat /run/nginx.pid)/fd | wc -l
ss -lnt 'sport = :443'
```

<!-- LINE-BY-LINE AUTO-08_PERFORMANCE-03 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>systemctl show nginx.service -p LimitNOFILE -p TasksMax</code> | Inspects or changes the named systemd unit; reload is used only after validation. |
| 2 | <code>cat /proc/$(cat /run/nginx.pid)/limits</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |
| 3 | <code>sudo ls /proc/$(cat /run/nginx.pid)/fd &#124; wc -l</code> | Lists the selected file metadata, including security labels when requested. |
| 4 | <code>ss -lnt 'sport = :443'</code> | Displays listening or connected sockets with the requested protocol and process details. |

Do not raise limits before proving exhaustion and the downstream system can accept more load.

## Static files

Filesystem cache often makes repeated reads fast. Tune correct cache headers and compression before adding complex caches. Precompressed or dynamic compression trades CPU for bytes. Do not compress already compressed formats or sensitive dynamic content without understanding compression side channels.

## TLS

Handshake cost depends on key exchange, certificates, client distance, session resumption, CPU, and connection reuse. Measure rather than using weak algorithms. HTTP/2 can reduce connection count but one TCP loss event affects multiplexed streams. HTTP/3 may help some paths and complicate UDP/firewall observability.

## Upstream timing

Log total and upstream connect/header/response time. Patterns:

| Pattern | Likely boundary |
| --- | --- |
| high connect time | backend accept queue, route/firewall, no free workers |
| fast connect, high header time | application/dependency processing |
| fast header, high response time | streaming/body generation/client backpressure |
| low upstream, high total | client transfer, proxy buffering, logging, local resource |

Prove with correlated backend logs and request ID.

## Load testing safely

Define target environment, request data, authentication, concurrency ramp, duration, stop thresholds, and owners. Start below expected load. Monitor client generator and every dependency. Never point a generator at production without explicit authorization.

Use a tool such as `wrk`, `hey`, or ApacheBench only after reading its semantics. A static `/health` benchmark does not represent login, upload, database, or cache-miss workloads.

## Overload behavior

A robust system has bounded queues, timeouts, backpressure, accurate 429/503 responses, circuit behavior, and headroom. Unlimited concurrency moves failure into OOM, database collapse, or timeouts. Capacity includes failure scenarios such as one backend unavailable and certificate renewal/reload during traffic.

## Scenario: latency spikes every hour

Correlate exact UTC minute with systemd timers/cron, log rotation/compression, backups, certificate tasks, cache expiry, application batch jobs, storage queue, and worker recycling. Change schedule or resource policy only after a mechanism is established.

## Review

1. Why are percentile latencies important?
2. What does time to first byte combine?
3. Why can a larger worker pool harm dependencies?
4. Why is `/health` a poor complete benchmark?
5. What should overload look like?
