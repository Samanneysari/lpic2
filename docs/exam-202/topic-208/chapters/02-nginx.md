# 02 — Nginx Administration

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

## Outcome

Operate Nginx configuration hierarchy, request selection, static files, reverse proxying, processes, logs, reloads, and failure recovery.

## Architecture

The master process reads configuration, binds privileged sockets, manages workers, and performs graceful reloads. Worker processes handle connections using event-driven I/O. Do not size workers solely from request count; upstream latency, TLS, open files, CPU, memory, and kernel queues matter.

```bash
ps -o pid,ppid,user,stat,etime,cmd -C nginx
sudo nginx -V 2>&1
sudo nginx -T
```

<!-- LINE-BY-LINE AUTO-02_NGINX-01 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>ps -o pid,ppid,user,stat,etime,cmd -C nginx</code> | Lists matching processes with parent, user, state, elapsed time, and command details. |
| 2 | <code>sudo nginx -V 2&gt;&amp;1</code> | Invokes Nginx with the shown validation, build-information, or configuration-dump option. |
| 3 | <code>sudo nginx -T</code> | Invokes Nginx with the shown validation, build-information, or configuration-dump option. |

`-V` prints build options and module paths. `-T` validates and prints the full configuration with included files; it may expose internal data.

## Configuration contexts

```nginx
user nginx;
worker_processes auto;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    include /etc/nginx/conf.d/*.conf;
}
```

<!-- LINE-BY-LINE AUTO-02_NGINX-02 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>user nginx;</code> | Selects the unprivileged account used by worker processes. |
| 2 | <code>worker_processes auto;</code> | Selects the number of Nginx worker processes; `auto` follows available CPUs. |
| 3 | <code>events {</code> | Opens the `events` configuration block. |
| 4 | <code>worker_connections 1024;</code> | Sets the maximum connections handled by each Nginx worker, including upstream connections. |
| 5 | <code>}</code> | Opens or closes the current configuration block. |
| 6 | <code>http {</code> | Opens the `http` configuration block. |
| 7 | <code>include /etc/nginx/mime.types;</code> | Loads configuration from the named file or matching files. |
| 8 | <code>default_type application/octet-stream;</code> | Sets the fallback media type when no more specific type is known. |
| 9 | <code>include /etc/nginx/conf.d/*.conf;</code> | Loads configuration from the named file or matching files. |
| 10 | <code>}</code> | Opens or closes the current configuration block. |

- Main-context directives affect the master/global process.
- `events` configures connection processing.
- `http` contains HTTP-wide policy and server blocks.
- `worker_connections` is per worker and includes upstream connections, not simply users.
- Include order can create duplicate or shadowing definitions.

## Server and location selection

Nginx first selects a listen address/port, then matches server name. It then selects a location through prefix and regular-expression rules. A common safe static site:

```nginx
server {
    listen 80;
    server_name app.realsam.ir;
    root /srv/www/app/public;

    location /static/ {
        expires 1h;
        try_files $uri =404;
    }

    location / {
        try_files $uri $uri/ =404;
    }
}
```

<!-- LINE-BY-LINE AUTO-02_NGINX-03 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>server {</code> | Defines a listening virtual server or an upstream backend, depending on its context. It opens the related configuration block. |
| 2 | <code>listen 80;</code> | Selects the local address, port, and optional listener parameters. |
| 3 | <code>server_name app.realsam.ir;</code> | Lists hostnames that select this Nginx server block. |
| 4 | <code>root /srv/www/app/public;</code> | Builds a filesystem path by appending the request URI to this directory. |
| 5 | <code>location /static/ {</code> | Opens a URI-matching block whose rules apply to matching requests. It opens the related configuration block. |
| 6 | <code>expires 1h;</code> | Controls the response expiration time and related cache headers. |
| 7 | <code>try_files $uri =404;</code> | Tests candidate paths in order and uses the final fallback when none exists. |
| 8 | <code>}</code> | Opens or closes the current configuration block. |
| 9 | <code>location / {</code> | Opens a URI-matching block whose rules apply to matching requests. It opens the related configuration block. |
| 10 | <code>try_files $uri $uri/ =404;</code> | Tests candidate paths in order and uses the final fallback when none exists. |
| 11 | <code>}</code> | Opens or closes the current configuration block. |
| 12 | <code>}</code> | Opens or closes the current configuration block. |

Use `nginx -T` and deliberate test URIs. Do not guess location precedence from file order alone.

## `root` versus `alias`

```nginx
location /images/ {
    alias /srv/media/;
}
```

<!-- LINE-BY-LINE AUTO-02_NGINX-04 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>location /images/ {</code> | Opens a URI-matching block whose rules apply to matching requests. It opens the related configuration block. |
| 2 | <code>alias /srv/media/;</code> | Replaces the matched location prefix with the specified filesystem path. |
| 3 | <code>}</code> | Opens or closes the current configuration block. |

For `/images/logo.png`, `alias` replaces the matching location prefix and reads `/srv/media/logo.png`. With `root /srv/media;`, the path would include `/images/`. Trailing slashes and regex captures matter. Validate path traversal, symlinks, permissions, and SELinux.

## Reverse proxy baseline

```nginx
upstream app_backend {
    server 127.0.0.1:8080;
    keepalive 16;
}

server {
    listen 80;
    server_name app.realsam.ir;

    location / {
        proxy_pass http://app_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 3s;
        proxy_read_timeout 30s;
    }
}
```

<!-- LINE-BY-LINE AUTO-02_NGINX-05 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>upstream app_backend {</code> | Opens a named group of backend servers. It opens the related configuration block. |
| 2 | <code>server 127.0.0.1:8080;</code> | Defines a listening virtual server or an upstream backend, depending on its context. |
| 3 | <code>keepalive 16;</code> | Keeps a bounded pool of idle upstream connections for reuse. |
| 4 | <code>}</code> | Opens or closes the current configuration block. |
| 5 | <code>server {</code> | Defines a listening virtual server or an upstream backend, depending on its context. It opens the related configuration block. |
| 6 | <code>listen 80;</code> | Selects the local address, port, and optional listener parameters. |
| 7 | <code>server_name app.realsam.ir;</code> | Lists hostnames that select this Nginx server block. |
| 8 | <code>location / {</code> | Opens a URI-matching block whose rules apply to matching requests. It opens the related configuration block. |
| 9 | <code>proxy_pass http://app_backend;</code> | Forwards matching requests to the named upstream URL. |
| 10 | <code>proxy_http_version 1.1;</code> | Selects the HTTP version used between the proxy and upstream. |
| 11 | <code>proxy_set_header Host $host;</code> | Overwrites the named request header before forwarding it upstream. |
| 12 | <code>proxy_set_header X-Real-IP $remote_addr;</code> | Overwrites the named request header before forwarding it upstream. |
| 13 | <code>proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;</code> | Overwrites the named request header before forwarding it upstream. |
| 14 | <code>proxy_set_header X-Forwarded-Proto $scheme;</code> | Overwrites the named request header before forwarding it upstream. |
| 15 | <code>proxy_connect_timeout 3s;</code> | Limits how long Nginx waits to establish an upstream connection. |
| 16 | <code>proxy_read_timeout 30s;</code> | Limits idle time while Nginx waits to read more upstream response data. |
| 17 | <code>}</code> | Opens or closes the current configuration block. |
| 18 | <code>}</code> | Opens or closes the current configuration block. |

Line by line:

- The upstream names one backend and creates an idle keepalive pool.
- `proxy_pass` forwards to the group.
- HTTP/1.1 is required for upstream keepalive and some upgraded protocols.
- `Host $host` sends Nginx's normalized selected host; `$http_host` preserves the raw value including port.
- `$remote_addr` is the direct peer unless a trusted real-IP module rewrites it.
- `$proxy_add_x_forwarded_for` appends that peer to an existing chain. At an Internet edge, sanitize untrusted inbound forwarding headers first.
- `$scheme` records what the client used at this hop.
- Connect and read timeouts govern different phases.

## URI rewrite trap

These differ:

```nginx
location /api/ { proxy_pass http://backend; }
location /api/ { proxy_pass http://backend/; }
```

<!-- LINE-BY-LINE AUTO-02_NGINX-06 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>location /api/ { proxy_pass http://backend; }</code> | Opens a URI-matching block whose rules apply to matching requests. |
| 2 | <code>location /api/ { proxy_pass http://backend/; }</code> | Opens a URI-matching block whose rules apply to matching requests. |

Without a URI, Nginx generally forwards the normalized original URI. With the trailing slash URI, the matching prefix is replaced. Test exact paths, encoded characters, redirects, and application route expectations.

## Safe reload

```bash
sudo nginx -t
sudo systemctl reload nginx.service
systemctl status nginx.service --no-pager
sudo journalctl -u nginx.service --since '-5 minutes'
curl --fail --resolve app.realsam.ir:80:192.0.2.10 \
  http://app.realsam.ir/health
```

<!-- LINE-BY-LINE AUTO-02_NGINX-07 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo nginx -t</code> | Invokes Nginx with the shown validation, build-information, or configuration-dump option. |
| 2 | <code>sudo systemctl reload nginx.service</code> | Inspects or changes the named systemd unit; reload is used only after validation. |
| 3 | <code>systemctl status nginx.service --no-pager</code> | Inspects or changes the named systemd unit; reload is used only after validation. |
| 4 | <code>sudo journalctl -u nginx.service --since '-5 minutes'</code> | Reads systemd journal records using the shown unit, priority, boot, or time filter. |
| 5 | <code>curl --fail --resolve app.realsam.ir:80:192.0.2.10 \</code> | Makes a bounded HTTP request with the shown name-resolution, header, output, or failure options. |
| 6 | <code>http://app.realsam.ir/health</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |

A graceful reload starts workers with new configuration and asks old workers to finish. Long-lived connections can keep old workers. Monitor process generations and memory. A successful systemd reload job does not prove the new site serves the intended response.

## Logging

```nginx
log_format main_timed '$remote_addr - $request_id [$time_iso8601] '
                      '"$request" $status $body_bytes_sent '
                      'rt=$request_time uct=$upstream_connect_time '
                      'uht=$upstream_header_time urt=$upstream_response_time '
                      'us=$upstream_status';
```

<!-- LINE-BY-LINE AUTO-02_NGINX-08 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>log_format main_timed '$remote_addr - $request_id [$time_iso8601] '</code> | Defines a named access-log format and its recorded fields. |
| 2 | <code>'"$request" $status $body_bytes_sent '</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |
| 3 | <code>'rt=$request_time uct=$upstream_connect_time '</code> | Assigns the shown value to `'rt` in this configuration or shell context. |
| 4 | <code>'uht=$upstream_header_time urt=$upstream_response_time '</code> | Assigns the shown value to `'uht` in this configuration or shell context. |
| 5 | <code>'us=$upstream_status';</code> | Assigns the shown value to `'us` in this configuration or shell context. |

Request time is total Nginx processing; upstream timings separate connection, first header, and response. Multi-upstream attempts can produce comma-separated values. Do not log Authorization, cookies, tokens, or full sensitive query strings.

## Failure scenarios

### Active but not listening

```bash
systemctl status nginx.service
sudo ss -lntp
sudo nginx -T
sudo journalctl -u nginx.service -b
```

<!-- LINE-BY-LINE AUTO-02_NGINX-09 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>systemctl status nginx.service</code> | Inspects or changes the named systemd unit; reload is used only after validation. |
| 2 | <code>sudo ss -lntp</code> | Displays listening or connected sockets with the requested protocol and process details. |
| 3 | <code>sudo nginx -T</code> | Invokes Nginx with the shown validation, build-information, or configuration-dump option. |
| 4 | <code>sudo journalctl -u nginx.service -b</code> | Reads systemd journal records using the shown unit, priority, boot, or time filter. |

The service may use a different config prefix, bind only another address, or have an old process after failed reload.

### Static file returns 403

```bash
namei -l /srv/www/app/public/index.html
ls -lZ /srv/www/app/public/index.html
sudo ausearch -m AVC -ts recent
sudo -u nginx test -r /srv/www/app/public/index.html
```

<!-- LINE-BY-LINE AUTO-02_NGINX-10 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>namei -l /srv/www/app/public/index.html</code> | Shows permissions and ownership for every component of a filesystem path. |
| 2 | <code>ls -lZ /srv/www/app/public/index.html</code> | Lists the selected file metadata, including security labels when requested. |
| 3 | <code>sudo ausearch -m AVC -ts recent</code> | Searches the audit log for recent SELinux AVC or other selected records. |
| 4 | <code>sudo -u nginx test -r /srv/www/app/public/index.html</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |

Check every parent directory, file mode/ACL, service identity, SELinux, mount/sandbox, and Nginx location. Do not use `chmod -R 777`.

### 502 from upstream

```bash
sudo ss -lntp 'sport = :8080'
curl -v --max-time 5 http://127.0.0.1:8080/health
sudo tail -n 100 /var/log/nginx/app.error.log
```

<!-- LINE-BY-LINE AUTO-02_NGINX-11 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo ss -lntp 'sport = :8080'</code> | Displays listening or connected sockets with the requested protocol and process details. |
| 2 | <code>curl -v --max-time 5 http://127.0.0.1:8080/health</code> | Makes a bounded HTTP request with the shown name-resolution, header, output, or failure options. |
| 3 | <code>sudo tail -n 100 /var/log/nginx/app.error.log</code> | Displays the requested final lines of a log or file. |

For Unix sockets, inspect socket path owner/mode, parent traversal, SELinux, service sandbox, and whether both processes see the same namespace.

## Review

1. Why does `worker_connections` not equal concurrent users?
2. How do `root` and `alias` differ?
3. Why are the two `proxy_pass` trailing-slash forms different?
4. What can keep old workers after reload?
5. Which log timings separate proxy versus upstream delay?
