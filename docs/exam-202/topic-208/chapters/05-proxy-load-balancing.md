# 05 — Reverse Proxy and Load Balancing

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

## Outcome

Design a trustworthy proxy boundary, meaningful health checks, safe retries, graceful draining, and observable upstream selection.

## Proxy roles

A reverse proxy accepts client requests for controlled sites and forwards them to backends. It may terminate TLS, route by name/path, normalize headers, authenticate, limit traffic, cache, compress, and balance. A forward proxy acts for clients toward arbitrary destinations; enabling one accidentally is a serious exposure.

## Trust boundary

The direct peer address is evidence. Forwarded headers are claims. At the public edge:

1. discard or overwrite untrusted incoming forwarding headers;
2. append the edge-observed client address;
3. make the application trust headers only from known proxy addresses;
4. protect the origin so clients cannot bypass the edge and forge claims.

If another CDN sits ahead, trust only its published/controlled address ranges and update them through a verified process. Never trust all addresses.

## Nginx upstream

```nginx
upstream app_pool {
    least_conn;
    server 192.0.2.31:8080 max_fails=3 fail_timeout=10s;
    server 192.0.2.32:8080 max_fails=3 fail_timeout=10s;
    keepalive 32;
}
```

<!-- LINE-BY-LINE AUTO-05_PROXY_LOAD_BALANCING-01 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>upstream app_pool {</code> | Opens a named group of backend servers. It opens the related configuration block. |
| 2 | <code>least_conn;</code> | Applies the `least_conn` directive with the shown value in the current context. |
| 3 | <code>server 192.0.2.31:8080 max_fails=3 fail_timeout=10s;</code> | Defines a listening virtual server or an upstream backend, depending on its context. |
| 4 | <code>server 192.0.2.32:8080 max_fails=3 fail_timeout=10s;</code> | Defines a listening virtual server or an upstream backend, depending on its context. |
| 5 | <code>keepalive 32;</code> | Keeps a bounded pool of idle upstream connections for reuse. |
| 6 | <code>}</code> | Opens or closes the current configuration block. |

- `least_conn` favors the server with fewer active connections; it does not know request cost.
- Passive failure settings mark failures based on proxied traffic under module rules.
- Open-source Nginx capabilities differ from commercial active health checks; verify installed features.
- Keepalive reuses idle upstream connections and changes capacity math.

## HAProxy baseline

```haproxy
global
    log /dev/log local0

defaults
    log global
    mode http
    option httplog
    timeout connect 3s
    timeout client 30s
    timeout server 30s

frontend https_in
    bind :443 ssl crt /etc/haproxy/certs/app.pem
    http-request set-header X-Forwarded-Proto https
    default_backend app_servers

backend app_servers
    balance roundrobin
    option httpchk GET /health/ready
    http-check expect status 200
    server app1 192.0.2.31:8080 check
    server app2 192.0.2.32:8080 check
```

<!-- LINE-BY-LINE AUTO-05_PROXY_LOAD_BALANCING-02 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>global</code> | Starts the HAProxy process-wide configuration section. |
| 2 | <code>log /dev/log local0</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |
| 3 | <code>defaults</code> | Starts HAProxy defaults inherited by later proxies. |
| 4 | <code>log global</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |
| 5 | <code>mode http</code> | Selects HAProxy TCP or HTTP processing for this section. |
| 6 | <code>option httplog</code> | Enables the named HAProxy behavior in this section. |
| 7 | <code>timeout connect 3s</code> | Sets a bounded timeout for the named HAProxy connection phase. |
| 8 | <code>timeout client 30s</code> | Sets a bounded timeout for the named HAProxy connection phase. |
| 9 | <code>timeout server 30s</code> | Sets a bounded timeout for the named HAProxy connection phase. |
| 10 | <code>frontend https_in</code> | Starts a client-facing HAProxy listener and routing section. |
| 11 | <code>bind :443 ssl crt /etc/haproxy/certs/app.pem</code> | Selects the local HAProxy listener and optional TLS certificate. |
| 12 | <code>http-request set-header X-Forwarded-Proto https</code> | Applies the specified HTTP request transformation or policy. |
| 13 | <code>default_backend app_servers</code> | Routes unmatched frontend traffic to the named backend pool. |
| 14 | <code>backend app_servers</code> | Starts an HAProxy backend-server pool section. |
| 15 | <code>balance roundrobin</code> | Selects the backend load-balancing algorithm. |
| 16 | <code>option httpchk GET /health/ready</code> | Enables the named HAProxy behavior in this section. |
| 17 | <code>http-check expect status 200</code> | Defines how HAProxy validates an HTTP health-check response. |
| 18 | <code>server app1 192.0.2.31:8080 check</code> | Defines a listening virtual server or an upstream backend, depending on its context. |
| 19 | <code>server app2 192.0.2.32:8080 check</code> | Defines a listening virtual server or an upstream backend, depending on its context. |

Explanation:

- Global logging sends HAProxy events to the local syslog socket when configured.
- Defaults establish HTTP log format and phase-specific timeouts.
- The frontend terminates TLS using a protected PEM bundle.
- It overwrites the scheme header at the trusted edge.
- The backend uses round-robin and application-level readiness.
- Each server participates in health checking.

Validate:

```bash
sudo haproxy -c -f /etc/haproxy/haproxy.cfg
sudo systemctl reload haproxy.service
sudo journalctl -u haproxy.service --since '-5 minutes'
```

<!-- LINE-BY-LINE AUTO-05_PROXY_LOAD_BALANCING-03 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo haproxy -c -f /etc/haproxy/haproxy.cfg</code> | Validates or runs HAProxy using the selected configuration file. |
| 2 | <code>sudo systemctl reload haproxy.service</code> | Inspects or changes the named systemd unit; reload is used only after validation. |
| 3 | <code>sudo journalctl -u haproxy.service --since '-5 minutes'</code> | Reads systemd journal records using the shown unit, priority, boot, or time filter. |

## Health endpoints

- Liveness: process is alive enough to avoid forced restart.
- Readiness: instance should receive user traffic.
- Startup: slow initialization is still in progress.

A readiness endpoint should test dependencies necessary to serve, but a check that performs expensive full transactions every second can create load or dependency cascades. A TCP connection proves less than a meaningful HTTP response.

## Retries

Retry only when failure type, method semantics, request body replay, timeout budget, and duplicate side effects are understood. GET is intended to be safe; a POST may charge twice. Coordinate proxy and application retries to avoid multiplicative storms.

## Timeouts and queues

Set connect timeout from network/backend establishment objectives, response timeout from endpoint behavior, client timeout from legitimate clients, and queue limits from capacity. Unlimited queues turn overload into long latency and resource exhaustion. Prefer bounded failure with accurate 503 and backpressure.

## WebSocket and upgrades

Nginx example:

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}

location /socket/ {
    proxy_pass http://app_pool;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $connection_upgrade;
    proxy_read_timeout 60s;
}
```

<!-- LINE-BY-LINE AUTO-05_PROXY_LOAD_BALANCING-04 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>map $http_upgrade $connection_upgrade {</code> | Creates a value derived from another variable before request processing. It opens the related configuration block. |
| 2 | <code>default upgrade;</code> | Provides the fallback value when no more specific mapping matches. |
| 3 | <code>'' close;</code> | Applies the `''` directive with the shown value in the current context. |
| 4 | <code>}</code> | Opens or closes the current configuration block. |
| 5 | <code>location /socket/ {</code> | Opens a URI-matching block whose rules apply to matching requests. It opens the related configuration block. |
| 6 | <code>proxy_pass http://app_pool;</code> | Forwards matching requests to the named upstream URL. |
| 7 | <code>proxy_http_version 1.1;</code> | Selects the HTTP version used between the proxy and upstream. |
| 8 | <code>proxy_set_header Upgrade $http_upgrade;</code> | Overwrites the named request header before forwarding it upstream. |
| 9 | <code>proxy_set_header Connection $connection_upgrade;</code> | Overwrites the named request header before forwarding it upstream. |
| 10 | <code>proxy_read_timeout 60s;</code> | Limits idle time while Nginx waits to read more upstream response data. |
| 11 | <code>}</code> | Opens or closes the current configuration block. |

Long-lived connections affect draining, file descriptors, memory, old worker lifetime, and load-balancing fairness.

## Graceful deployment and drain

1. Mark backend unready or place it in maintenance.
2. Wait for active requests/connections according to protocol limits.
3. Deploy and validate locally.
4. Restore readiness.
5. Observe errors/latency before proceeding to next backend.

Session state should not require sticky routing when avoidable. If persistence is necessary, understand cookie security, uneven load, failover behavior, and state recovery.

## Scenario: all backends healthy but users fail

Health may test `/health` while users require DNS, authentication, storage, a different route, or larger bodies. Compare a real synthetic transaction, proxy status/upstream timings, backend application logs with request ID, and dependency metrics.

## Review

1. Why are forwarding headers a trust boundary?
2. How do liveness and readiness differ?
3. Why can retries create duplicate business actions?
4. Why can a TCP health check be green while users fail?
5. What must happen before removing a backend?
