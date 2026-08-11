# 00 — Lab and Operating Model

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

## Outcome

Build a two-VM environment and deploy a site through DNS-independent, HTTP, and service-level tests.

## Topology

| Node | Suggested OS | Address | Role |
| --- | --- | --- | --- |
| `web1.realsam.ir` | Rocky/AlmaLinux 9 | `192.0.2.10` | Nginx, Apache, HAProxy, PHP-FPM labs |
| `client1.realsam.ir` | Current Linux | `192.0.2.20` | Independent DNS, TCP, TLS, HTTP, and load tests |

Use an isolated network plus NAT for package access. Take a clean snapshot. Never expose the lab directly to the Internet.

## Install Nginx on RHEL family

```bash
sudo dnf install nginx
sudo nginx -t
sudo systemctl enable --now nginx.service
sudo firewall-cmd --zone=public --add-service=http --permanent
sudo firewall-cmd --reload
```

<!-- LINE-BY-LINE AUTO-00_LAB-01 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo dnf install nginx</code> | Installs or inspects packages on a RHEL-family system. |
| 2 | <code>sudo nginx -t</code> | Invokes Nginx with the shown validation, build-information, or configuration-dump option. |
| 3 | <code>sudo systemctl enable --now nginx.service</code> | Inspects or changes the named systemd unit; reload is used only after validation. |
| 4 | <code>sudo firewall-cmd --zone=public --add-service=http --permanent</code> | Inspects or changes firewalld policy using the stated runtime or permanent option. |
| 5 | <code>sudo firewall-cmd --reload</code> | Inspects or changes firewalld policy using the stated runtime or permanent option. |

Line by line:

- DNF resolves the signed package and dependencies; review the transaction.
- `nginx -t` parses configuration and tries required files before the first start.
- `enable --now` creates boot enablement and starts the service now; these are separate effects.
- The permanent firewalld rule allows the predefined HTTP service in the explicitly named zone.
- Reload makes persistent firewalld policy active. Verify the interface really belongs to `public`.

On Ubuntu, packages are installed with APT and firewall tooling may differ. Do not blindly mix RHEL paths and unit names with Ubuntu instructions.

## Create the first site

```bash
sudo install -d -o root -g nginx -m 0750 /srv/www/app.realsam.ir/public
printf '%s\n' '<h1>app.realsam.ir</h1>' |
  sudo tee /srv/www/app.realsam.ir/public/index.html >/dev/null
sudo chmod 0640 /srv/www/app.realsam.ir/public/index.html
```

<!-- LINE-BY-LINE AUTO-00_LAB-02 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo install -d -o root -g nginx -m 0750 /srv/www/app.realsam.ir/public</code> | Creates a file or directory with explicit owner, group, and permission mode. |
| 2 | <code>printf '%s\n' '&lt;h1&gt;app.realsam.ir&lt;/h1&gt;' &#124;</code> | Produces the exact formatted text used by the next pipeline stage or file write. |
| 3 | <code>sudo tee /srv/www/app.realsam.ir/public/index.html &gt;/dev/null</code> | Writes standard input to the selected file while allowing controlled privileged output. |
| 4 | <code>sudo chmod 0640 /srv/www/app.realsam.ir/public/index.html</code> | Changes permission bits on the exact selected path. |

The content is root-owned so the web process cannot rewrite executable/site content. The group can read it. Directory traversal requires execute permission on every parent.

Create `/etc/nginx/conf.d/app.realsam.ir.conf`:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name app.realsam.ir;

    root /srv/www/app.realsam.ir/public;
    index index.html;

    access_log /var/log/nginx/app.access.log;
    error_log /var/log/nginx/app.error.log warn;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

<!-- LINE-BY-LINE AUTO-00_LAB-03 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>server {</code> | Defines a listening virtual server or an upstream backend, depending on its context. It opens the related configuration block. |
| 2 | <code>listen 80;</code> | Selects the local address, port, and optional listener parameters. |
| 3 | <code>listen [::]:80;</code> | Selects the local address, port, and optional listener parameters. |
| 4 | <code>server_name app.realsam.ir;</code> | Lists hostnames that select this Nginx server block. |
| 5 | <code>root /srv/www/app.realsam.ir/public;</code> | Builds a filesystem path by appending the request URI to this directory. |
| 6 | <code>index index.html;</code> | Applies the `index` directive with the shown value in the current context. |
| 7 | <code>access_log /var/log/nginx/app.access.log;</code> | Selects the access-log destination and optional format. |
| 8 | <code>error_log /var/log/nginx/app.error.log warn;</code> | Selects the error-log destination and severity threshold. |
| 9 | <code>location / {</code> | Opens a URI-matching block whose rules apply to matching requests. It opens the related configuration block. |
| 10 | <code>try_files $uri $uri/ =404;</code> | Tests candidate paths in order and uses the final fallback when none exists. |
| 11 | <code>}</code> | Opens or closes the current configuration block. |
| 12 | <code>}</code> | Opens or closes the current configuration block. |

Explanation:

- `listen` accepts IPv4 and IPv6 port 80 according to address availability.
- `server_name` selects this server block from the request Host authority.
- `root` maps URI paths below a controlled document root.
- `index` defines the directory index candidate.
- Per-site logs make ownership and incident scope clearer.
- `try_files` tests the normalized URI path, then directory, and otherwise returns 404; it does not route every missing file into an application.

Label nonstandard content for SELinux:

```bash
sudo semanage fcontext -a -t httpd_sys_content_t \
  '/srv/www/app.realsam.ir/public(/.*)?'
sudo restorecon -RFv /srv/www/app.realsam.ir/public
```

<!-- LINE-BY-LINE AUTO-00_LAB-04 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo semanage fcontext -a -t httpd_sys_content_t \</code> | Creates or changes a persistent SELinux policy mapping. |
| 2 | <code>'/srv/www/app.realsam.ir/public(/.*)?'</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |
| 3 | <code>sudo restorecon -RFv /srv/www/app.realsam.ir/public</code> | Applies the persistent SELinux file-context mapping to the selected path. |

Use a persistent label mapping and then apply it. `semanage` may require an additional policy utility package.

## Validate without waiting for DNS

```bash
sudo nginx -t
sudo systemctl reload nginx.service
curl --fail --silent --show-error \
  --resolve app.realsam.ir:80:127.0.0.1 \
  http://app.realsam.ir/
```

<!-- LINE-BY-LINE AUTO-00_LAB-05 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo nginx -t</code> | Invokes Nginx with the shown validation, build-information, or configuration-dump option. |
| 2 | <code>sudo systemctl reload nginx.service</code> | Inspects or changes the named systemd unit; reload is used only after validation. |
| 3 | <code>curl --fail --silent --show-error \</code> | Makes a bounded HTTP request with the shown name-resolution, header, output, or failure options. |
| 4 | <code>--resolve app.realsam.ir:80:127.0.0.1 \</code> | Adds the shown option or argument to the continued command; the trailing backslash continues it when present. |
| 5 | <code>http://app.realsam.ir/</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |

`--resolve` supplies an address for this curl request while retaining the intended Host value. It isolates web configuration from DNS. Then test remotely from `client1` with `192.0.2.10` in `--resolve`.

Validation layers:

```bash
getent ahosts app.realsam.ir
ip route get 192.0.2.10
nc -vz -w 3 192.0.2.10 80
curl -v --max-time 10 http://app.realsam.ir/
```

<!-- LINE-BY-LINE AUTO-00_LAB-06 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>getent ahosts app.realsam.ir</code> | Uses the system NSS configuration to resolve the selected host or database entry. |
| 2 | <code>ip route get 192.0.2.10</code> | Displays or changes the selected Linux link, address, neighbor, route, or policy state. |
| 3 | <code>nc -vz -w 3 192.0.2.10 80</code> | Tests a TCP or UDP connection using the selected address, port, and timeout. |
| 4 | <code>curl -v --max-time 10 http://app.realsam.ir/</code> | Makes a bounded HTTP request with the shown name-resolution, header, output, or failure options. |

These respectively test the normal name-service path, kernel route, TCP port, and HTTP transaction.

## First failure drill

Seed one at a time: stopped unit, syntax error in a new file, wrong `server_name`, wrong document-root permissions, SELinux wrong label, closed firewall, or client DNS pointing elsewhere. Before repair, collect:

```bash
systemctl status nginx.service --no-pager
sudo journalctl -u nginx.service --since '-10 minutes'
sudo nginx -T
sudo ss -lntp 'sport = :80'
namei -l /srv/www/app.realsam.ir/public/index.html
ls -lZ /srv/www/app.realsam.ir/public/index.html
```

<!-- LINE-BY-LINE AUTO-00_LAB-07 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>systemctl status nginx.service --no-pager</code> | Inspects or changes the named systemd unit; reload is used only after validation. |
| 2 | <code>sudo journalctl -u nginx.service --since '-10 minutes'</code> | Reads systemd journal records using the shown unit, priority, boot, or time filter. |
| 3 | <code>sudo nginx -T</code> | Invokes Nginx with the shown validation, build-information, or configuration-dump option. |
| 4 | <code>sudo ss -lntp 'sport = :80'</code> | Displays listening or connected sockets with the requested protocol and process details. |
| 5 | <code>namei -l /srv/www/app.realsam.ir/public/index.html</code> | Shows permissions and ownership for every component of a filesystem path. |
| 6 | <code>ls -lZ /srv/www/app.realsam.ir/public/index.html</code> | Lists the selected file metadata, including security labels when requested. |

## Lab report

Record impact, UTC timeline, current versions, three observations, primary and alternate hypothesis, change, rollback, local validation, remote validation, root cause, and prevention.

## Review

1. Why does `nginx -t` not prove the site works remotely?
2. What does `--resolve` isolate?
3. Why use `semanage fcontext` rather than only `chcon`?
4. Why must the active firewalld zone be checked?
