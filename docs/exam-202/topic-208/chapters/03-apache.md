# 03 — Apache HTTP Server Administration

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

## Outcome

Operate Apache modules, virtual hosts, directory authorization, MPMs, reverse proxying, reloads, and logs safely.

## Discover the installed layout

RHEL commonly uses `httpd`; Debian/Ubuntu commonly uses `apache2`. Paths and helper commands differ.

```bash
httpd -V
apachectl -M
apachectl -S
apachectl configtest
```

<!-- LINE-BY-LINE AUTO-03_APACHE-01 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>httpd -V</code> | Inspects or controls the Apache HTTP Server using its RHEL-family command name. |
| 2 | <code>apachectl -M</code> | Validates, inspects, or controls Apache through its administration wrapper. |
| 3 | <code>apachectl -S</code> | Validates, inspects, or controls Apache through its administration wrapper. |
| 4 | <code>apachectl configtest</code> | Validates, inspects, or controls Apache through its administration wrapper. |

- `-V` reports build-time roots, config file, MPM, and options.
- `-M` lists loaded modules.
- `-S` maps listeners and virtual-host selection.
- `configtest` parses configuration but cannot prove files, certificates, upstreams, or applications work at runtime.

## Virtual host

```apache
<VirtualHost *:80>
    ServerName app.realsam.ir
    DocumentRoot /srv/www/app/public

    <Directory /srv/www/app/public>
        Options -Indexes +FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>

    ErrorLog /var/log/httpd/app-error.log
    CustomLog /var/log/httpd/app-access.log combined
</VirtualHost>
```

<!-- LINE-BY-LINE AUTO-03_APACHE-02 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>&lt;VirtualHost *:80&gt;</code> | Opens an Apache `VirtualHost` section for the shown scope. |
| 2 | <code>ServerName app.realsam.ir</code> | Sets the primary hostname for this Apache virtual host. |
| 3 | <code>DocumentRoot /srv/www/app/public</code> | Selects the directory from which Apache serves files for this site. |
| 4 | <code>&lt;Directory /srv/www/app/public&gt;</code> | Opens an Apache `Directory` section for the shown scope. |
| 5 | <code>Options -Indexes +FollowSymLinks</code> | Enables or disables the listed Apache directory features. |
| 6 | <code>AllowOverride None</code> | Controls which directives a per-directory `.htaccess` file may override. |
| 7 | <code>Require all granted</code> | Defines the Apache authorization condition for this scope. |
| 8 | <code>&lt;/Directory&gt;</code> | Closes the Apache configuration section opened above. |
| 9 | <code>ErrorLog /var/log/httpd/app-error.log</code> | Selects the Apache error log for this server or virtual host. |
| 10 | <code>CustomLog /var/log/httpd/app-access.log combined</code> | Selects the Apache access log and log format. |
| 11 | <code>&lt;/VirtualHost&gt;</code> | Closes the Apache configuration section opened above. |

Line by line:

- `VirtualHost` selects all configured addresses on port 80; Apache must also `Listen 80`.
- `ServerName` identifies the name-based host and affects generated self-references.
- `DocumentRoot` maps requests into the filesystem.
- `<Directory>` applies policy to a filesystem path, not a URL.
- `-Indexes` prevents directory listing; `FollowSymLinks` permits symlink following and requires a conscious trust boundary.
- `AllowOverride None` prevents distributed `.htaccess` overrides and improves predictability/performance.
- `Require all granted` authorizes access after filesystem and MAC checks.
- Per-site logs aid ownership and incident correlation.

Validate selection:

```bash
sudo apachectl configtest
sudo apachectl -S
sudo systemctl reload httpd.service
curl --resolve app.realsam.ir:80:192.0.2.10 http://app.realsam.ir/
```

<!-- LINE-BY-LINE AUTO-03_APACHE-03 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo apachectl configtest</code> | Validates, inspects, or controls Apache through its administration wrapper. |
| 2 | <code>sudo apachectl -S</code> | Validates, inspects, or controls Apache through its administration wrapper. |
| 3 | <code>sudo systemctl reload httpd.service</code> | Inspects or changes the named systemd unit; reload is used only after validation. |
| 4 | <code>curl --resolve app.realsam.ir:80:192.0.2.10 http://app.realsam.ir/</code> | Makes a bounded HTTP request with the shown name-resolution, header, output, or failure options. |

## Configuration sections

- `<Directory>` matches filesystem paths.
- `<Location>` matches URL space.
- `<Files>` matches filenames.
- `<If>` evaluates runtime expressions.

Authorization can combine unexpectedly when sections overlap. Inspect official merge rules and test denied and allowed cases.

## Modules

Only loaded modules supply directives. RHEL loads modules through files under `/etc/httpd/conf.modules.d`; Debian-family systems provide `a2enmod`/`a2dismod`. Do not use Debian helpers on RHEL.

```bash
apachectl -M | sort
rpm -qf /usr/lib64/httpd/modules/mod_proxy.so
```

<!-- LINE-BY-LINE AUTO-03_APACHE-04 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>apachectl -M &#124; sort</code> | Validates, inspects, or controls Apache through its administration wrapper. |
| 2 | <code>rpm -qf /usr/lib64/httpd/modules/mod_proxy.so</code> | Queries installed RPM package versions and metadata. |

Remove unused modules only after mapping site dependencies and testing restart/reload.

## MPMs

The Multi-Processing Module defines connection/process/thread behavior:

- `prefork`: processes without worker threads; legacy module compatibility, higher memory per concurrency.
- `worker`: threaded workers.
- `event`: threaded with improved keepalive handling; common modern choice.

```bash
httpd -V | grep -i 'Server MPM'
apachectl -M | grep mpm
```

<!-- LINE-BY-LINE AUTO-03_APACHE-05 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>httpd -V &#124; grep -i 'Server MPM'</code> | Inspects or controls the Apache HTTP Server using its RHEL-family command name. |
| 2 | <code>apachectl -M &#124; grep mpm</code> | Validates, inspects, or controls Apache through its administration wrapper. |

Do not load multiple MPMs. Size from memory per process/thread, traffic, application gateway capacity, keepalive, and latency—not a copied `MaxRequestWorkers` number.

## Reverse proxy

```apache
<VirtualHost *:80>
    ServerName app.realsam.ir
    ProxyRequests Off
    ProxyPreserveHost On

    ProxyPass        / http://127.0.0.1:8080/ connectiontimeout=3 timeout=30
    ProxyPassReverse / http://127.0.0.1:8080/

    RequestHeader set X-Forwarded-Proto "http"
</VirtualHost>
```

<!-- LINE-BY-LINE AUTO-03_APACHE-06 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>&lt;VirtualHost *:80&gt;</code> | Opens an Apache `VirtualHost` section for the shown scope. |
| 2 | <code>ServerName app.realsam.ir</code> | Sets the primary hostname for this Apache virtual host. |
| 3 | <code>ProxyRequests Off</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |
| 4 | <code>ProxyPreserveHost On</code> | Controls whether Apache preserves the incoming Host header upstream. |
| 5 | <code>ProxyPass        / http://127.0.0.1:8080/ connectiontimeout=3 timeout=30</code> | Maps a public path to an upstream URL and sets proxy options. |
| 6 | <code>ProxyPassReverse / http://127.0.0.1:8080/</code> | Rewrites upstream redirect-related response headers for the public URL space. |
| 7 | <code>RequestHeader set X-Forwarded-Proto "http"</code> | Sets, edits, or removes a request header at the configured processing stage. |
| 8 | <code>&lt;/VirtualHost&gt;</code> | Closes the Apache configuration section opened above. |

- `ProxyRequests Off` prevents forward-proxy operation; reverse proxy directives still work.
- Preserving Host helps applications with name-based routing, but the application must validate allowed hosts.
- `ProxyPass` maps requests and defines phase-specific timeouts.
- `ProxyPassReverse` rewrites certain upstream redirect headers; it does not rewrite arbitrary HTML content.
- The scheme header must reflect the trusted edge. At TLS termination it should be `https`.

An accidentally enabled forward proxy can be abused. Confirm from an unauthorized client that proxy requests are rejected.

## `.htaccess`

Distributed configuration is read along the request path when overrides are enabled. It permits delegated control but adds per-request filesystem checks and hides effective policy. Prefer central virtual-host configuration. If an application requires `.htaccess`, allow only the minimum override classes on the narrow directory.

## Logs and request correlation

Define a request ID at the edge and forward it rather than accepting an arbitrary public value. Apache modules can log microsecond durations and proxy status. Sanitize query strings and headers.

```bash
sudo tail -F /var/log/httpd/app-access.log /var/log/httpd/app-error.log
sudo journalctl -u httpd.service --since '-10 minutes'
```

<!-- LINE-BY-LINE AUTO-03_APACHE-07 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo tail -F /var/log/httpd/app-access.log /var/log/httpd/app-error.log</code> | Displays the requested final lines of a log or file. |
| 2 | <code>sudo journalctl -u httpd.service --since '-10 minutes'</code> | Reads systemd journal records using the shown unit, priority, boot, or time filter. |

`tail -F` follows a filename across rotation better than `-f`, but interactive viewing is not monitoring.

## Failure scenarios

### Wrong default virtual host

Use `apachectl -S`, curl with explicit Host/resolve, and the listener address. The first virtual host for an address/port can be the default when no name matches.

### Configuration says allowed but returns 403

Check section merging, authentication/authorization result, Unix traversal, ACL, SELinux, and module-specific rules. Error logs usually identify the authorization provider or filesystem denial.

### Reload says success but old behavior remains

Verify process generation, effective config, correct unit/config root, load balancer path, cache/CDN, and whether a different server answers DNS.

## Review

1. What does `apachectl -S` reveal?
2. How do `<Directory>` and `<Location>` differ?
3. Why is an open forward proxy dangerous?
4. Why can `.htaccess` reduce predictability?
5. What determines MPM capacity?
