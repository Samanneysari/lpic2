# 06 — Application Gateways and PHP-FPM

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

## Outcome

Connect web servers to application workers through Unix or TCP sockets, preserve identity, limit privilege, and diagnose gateway failures.

## Static server versus application gateway

Nginx and Apache can serve files directly or pass requests to an application protocol such as FastCGI, HTTP, WSGI, uWSGI, or SCGI. The web server and application have different users, filesystem views, timeouts, logs, and resource limits.

## PHP-FPM pool

Illustrative pool configuration:

```ini
[app]
user = app
group = app
listen = /run/php-fpm/app.sock
listen.owner = nginx
listen.group = nginx
listen.mode = 0660
pm = dynamic
pm.max_children = 20
pm.start_servers = 4
pm.min_spare_servers = 2
pm.max_spare_servers = 6
pm.max_requests = 500
request_terminate_timeout = 30s
```

<!-- LINE-BY-LINE AUTO-06_APPLICATION_GATEWAYS-01 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>[app]</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |
| 2 | <code>user = app</code> | Selects the unprivileged account used by worker processes. |
| 3 | <code>group = app</code> | Assigns the shown value to `group` in this configuration or shell context. |
| 4 | <code>listen = /run/php-fpm/app.sock</code> | Selects the local address, port, and optional listener parameters. |
| 5 | <code>listen.owner = nginx</code> | Sets the owner of the PHP-FPM Unix socket. |
| 6 | <code>listen.group = nginx</code> | Sets the group of the PHP-FPM Unix socket. |
| 7 | <code>listen.mode = 0660</code> | Sets permission bits on the PHP-FPM Unix socket. |
| 8 | <code>pm = dynamic</code> | Selects the PHP-FPM process-management strategy. |
| 9 | <code>pm.max_children = 20</code> | Caps simultaneously active PHP-FPM worker processes. |
| 10 | <code>pm.start_servers = 4</code> | Sets the initial worker count for dynamic process management. |
| 11 | <code>pm.min_spare_servers = 2</code> | Sets the minimum idle worker count maintained in dynamic mode. |
| 12 | <code>pm.max_spare_servers = 6</code> | Sets the maximum idle worker count maintained in dynamic mode. |
| 13 | <code>pm.max_requests = 500</code> | Recycles a worker after this many requests to bound long-term leaks. |
| 14 | <code>request_terminate_timeout = 30s</code> | Stops a PHP-FPM request that exceeds this execution deadline. |

- A dedicated pool identity separates applications.
- A Unix socket avoids network exposure; web-server identity receives socket access.
- `pm.max_children` caps concurrent executing workers and must fit memory/database/upstream capacity.
- Spare/start values control process availability for dynamic mode.
- Recycling after requests can limit long-lived growth but is not a memory-leak fix.
- Termination timeout bounds stuck scripts and can interrupt legitimate work.

Exact file, service name, PHP version, and directive support vary.

## Nginx FastCGI mapping

```nginx
location ~ \.php$ {
    try_files $uri =404;
    include fastcgi_params;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    fastcgi_param HTTP_PROXY "";
    fastcgi_pass unix:/run/php-fpm/app.sock;
    fastcgi_connect_timeout 3s;
    fastcgi_read_timeout 30s;
}
```

<!-- LINE-BY-LINE AUTO-06_APPLICATION_GATEWAYS-02 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>location ~ \.php$ {</code> | Opens a URI-matching block whose rules apply to matching requests. It opens the related configuration block. |
| 2 | <code>try_files $uri =404;</code> | Tests candidate paths in order and uses the final fallback when none exists. |
| 3 | <code>include fastcgi_params;</code> | Loads configuration from the named file or matching files. |
| 4 | <code>fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;</code> | Sets one FastCGI parameter passed to the application worker. |
| 5 | <code>fastcgi_param HTTP_PROXY "";</code> | Sets one FastCGI parameter passed to the application worker. |
| 6 | <code>fastcgi_pass unix:/run/php-fpm/app.sock;</code> | Sends the request to the selected FastCGI/PHP-FPM endpoint. |
| 7 | <code>fastcgi_connect_timeout 3s;</code> | Applies the `fastcgi_connect_timeout` directive with the shown value in the current context. |
| 8 | <code>fastcgi_read_timeout 30s;</code> | Applies the `fastcgi_read_timeout` directive with the shown value in the current context. |
| 9 | <code>}</code> | Opens or closes the current configuration block. |

- `try_files` prevents passing a nonexistent path under common configurations.
- Included parameters supply request metadata.
- `SCRIPT_FILENAME` maps the selected file; wrong `root`, `alias`, or path construction can execute/read the wrong target.
- Clearing `HTTP_PROXY` avoids a dangerous environment-variable ambiguity in affected application patterns.
- `fastcgi_pass` connects to the pool socket.

Applications should place only a public document root behind the web server; configuration, uploads, source control, backups, and secrets must not be executable/downloadable.

## Unix socket troubleshooting

```bash
sudo ss -xlpn | grep php
namei -l /run/php-fpm/app.sock
ls -lZ /run/php-fpm/app.sock
systemctl status php-fpm.service --no-pager
sudo journalctl -u php-fpm.service --since '-10 minutes'
sudo ausearch -m AVC -ts recent
```

<!-- LINE-BY-LINE AUTO-06_APPLICATION_GATEWAYS-03 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo ss -xlpn &#124; grep php</code> | Displays listening or connected sockets with the requested protocol and process details. |
| 2 | <code>namei -l /run/php-fpm/app.sock</code> | Shows permissions and ownership for every component of a filesystem path. |
| 3 | <code>ls -lZ /run/php-fpm/app.sock</code> | Lists the selected file metadata, including security labels when requested. |
| 4 | <code>systemctl status php-fpm.service --no-pager</code> | Inspects or changes the named systemd unit; reload is used only after validation. |
| 5 | <code>sudo journalctl -u php-fpm.service --since '-10 minutes'</code> | Reads systemd journal records using the shown unit, priority, boot, or time filter. |
| 6 | <code>sudo ausearch -m AVC -ts recent</code> | Searches the audit log for recent SELinux AVC or other selected records. |

The socket must exist after service start, both identities need directory traversal and socket permission, SELinux must allow the connection, and systemd namespaces must expose the same path.

## TCP application upstream

Bind an application to loopback or a private address, not `0.0.0.0`, unless network policy and authentication explicitly require exposure.

```bash
sudo ss -lntp 'sport = :8080'
curl --fail --max-time 5 http://127.0.0.1:8080/health
```

<!-- LINE-BY-LINE AUTO-06_APPLICATION_GATEWAYS-04 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo ss -lntp 'sport = :8080'</code> | Displays listening or connected sockets with the requested protocol and process details. |
| 2 | <code>curl --fail --max-time 5 http://127.0.0.1:8080/health</code> | Makes a bounded HTTP request with the shown name-resolution, header, output, or failure options. |

Local curl proves application HTTP without the proxy. Then test proxy with intended Host. The contrast bounds the fault.

## Capacity

If each PHP worker has a measured 80 MiB resident working set and the pool has 20 children, plan roughly 1.6 GiB plus master/shared memory, web server, OS cache, agents, and headroom. RSS sharing makes this estimate imperfect; measure proportional memory and peak workload.

A larger pool can overload database connections, CPU, storage, or APIs. Queue length and request latency determine whether workers are insufficient.

## Uploads

Limits can exist at client, CDN, proxy, Nginx/Apache, PHP, application, temp filesystem, and backend. For a failed upload inspect status, exact responding layer, request size, timeout, temp capacity/inodes, permissions/SELinux, and application logs. Raising every limit is not diagnosis.

## Scenario: intermittent 502

Correlate request ID and time across proxy error log, PHP-FPM slow/error log, pool saturation, OOM, socket backlog, application timeout, and dependency latency. A reload may hide the condition. Capture worker/queue/memory state first.

## Review

1. Why use one PHP-FPM pool per trust boundary?
2. What controls access to a Unix socket?
3. Why can increasing `pm.max_children` worsen availability?
4. Why must only the public application directory be exposed?
5. Which layers can reject a large upload?
