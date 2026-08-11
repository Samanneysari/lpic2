# 07 — Web-Server Security and Hardening

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

## Outcome

Reduce attack surface across network, TLS, HTTP, filesystem, process, proxy, application, and operations without using destructive shortcuts.

## Threat model

Identify assets (credentials, personal data, content, private keys), actors, entry paths, trust boundaries, and required availability. A static public site, admin portal, API, and upload service need different controls.

## Minimum exposure

```bash
sudo ss -lntup
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --zone=public --list-all
ps -eo user,pid,ppid,cmd -C nginx -C httpd -C php-fpm
```

<!-- LINE-BY-LINE AUTO-07_SECURITY-01 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo ss -lntup</code> | Displays listening or connected sockets with the requested protocol and process details. |
| 2 | <code>sudo firewall-cmd --get-active-zones</code> | Inspects or changes firewalld policy using the stated runtime or permanent option. |
| 3 | <code>sudo firewall-cmd --zone=public --list-all</code> | Inspects or changes firewalld policy using the stated runtime or permanent option. |
| 4 | <code>ps -eo user,pid,ppid,cmd -C nginx -C httpd -C php-fpm</code> | Lists matching processes with parent, user, state, elapsed time, and command details. |

Every listener needs an owner, client population, authentication, encryption, and business reason. Bind backends/status endpoints to loopback or management networks and enforce host firewalls.

## Filesystem and process identity

- Configuration and executable content are root-owned and not writable by the web identity.
- Upload/cache/session paths are separate and writable only where required.
- Private keys are narrowly readable.
- Directory listing is disabled unless intentional.
- Backups, `.git`, environment files, editor swaps, and source maps are not under the document root.
- SELinux remains enforcing with correct types and booleans.

```bash
namei -l /srv/www/app/public/index.html
getfacl -p /srv/www/app/public
ls -ldZ /srv/www/app/public
sudo find /srv/www -xdev -type f -perm /002 -ls
```

<!-- LINE-BY-LINE AUTO-07_SECURITY-02 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>namei -l /srv/www/app/public/index.html</code> | Shows permissions and ownership for every component of a filesystem path. |
| 2 | <code>getfacl -p /srv/www/app/public</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |
| 3 | <code>ls -ldZ /srv/www/app/public</code> | Lists the selected file metadata, including security labels when requested. |
| 4 | <code>sudo find /srv/www -xdev -type f -perm /002 -ls</code> | Selects filesystem objects using the shown safe criteria and action. |

## Request controls

Validate allowed Host names, methods, body size, content type, paths, authentication, and authorization in the application. The web server can reject obvious invalid traffic, but URL rewriting is not an application security model.

Do not expose version banners unnecessarily, but banner removal is minor compared with patching and architecture.

## Security headers

Headers require application-aware testing:

- HSTS forces future HTTPS.
- Content-Security-Policy restricts content sources and can break applications; begin in report-only mode.
- `X-Content-Type-Options: nosniff` limits MIME sniffing.
- `Referrer-Policy` controls referrer disclosure.
- `Permissions-Policy` controls selected browser features.
- Frame protection can use CSP `frame-ancestors`; legacy `X-Frame-Options` supports simpler cases.

Do not copy a huge CSP with `unsafe-inline` and assume security. Inventory real resources and nonces/hashes.

## Proxy and client IP

Only a known proxy may set trusted client-IP headers. Configure real-IP modules with exact trusted ranges and a recursive policy matching the proxy chain. Test a direct-origin request with forged `X-Forwarded-For`; it must not gain trusted identity or bypass rate limits.

Origin protection includes firewall allowlists/private networking, separate authentication when appropriate, and DNS/certificate design. CDN DNS alone does not hide an origin that remains reachable.

## Rate limiting

Rate limits protect resources but can block users behind NAT, accessibility tools, or legitimate bursts. Key on an authenticated identity when possible, separate login/upload/API policies, return observable status, and coordinate with upstream/CDN limits. Rate limiting is not complete DDoS protection.

## Secrets

Do not place secrets in:

- repository or image;
- URI/query string;
- environment visible to broad process inspection when avoidable;
- Nginx variables/log format;
- Apache command-line arguments;
- world-readable application config.

Use an approved delivery store, narrow service credentials, rotation, and audit. If a secret reached Git, rotate it; deleting history does not revoke it.

## Patch and module review

```bash
sudo dnf updateinfo list --security
nginx -V 2>&1
apachectl -M
rpm -Va nginx httpd
```

<!-- LINE-BY-LINE AUTO-07_SECURITY-03 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo dnf updateinfo list --security</code> | Installs or inspects packages on a RHEL-family system. |
| 2 | <code>nginx -V 2&gt;&amp;1</code> | Invokes Nginx with the shown validation, build-information, or configuration-dump option. |
| 3 | <code>apachectl -M</code> | Validates, inspects, or controls Apache through its administration wrapper. |
| 4 | <code>rpm -Va nginx httpd</code> | Queries installed RPM package versions and metadata. |

Verify package provenance and support. A changed config is expected in RPM verification and must be reconciled with change records. Remove unused modules only after testing.

## systemd hardening

Inspect vendor protection:

```bash
systemctl cat nginx.service
systemd-analyze security nginx.service
systemctl show nginx.service -p User -p Group -p NoNewPrivileges \
  -p ProtectSystem -p ReadWritePaths -p CapabilityBoundingSet
```

<!-- LINE-BY-LINE AUTO-07_SECURITY-04 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>systemctl cat nginx.service</code> | Inspects or changes the named systemd unit; reload is used only after validation. |
| 2 | <code>systemd-analyze security nginx.service</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |
| 3 | <code>systemctl show nginx.service -p User -p Group -p NoNewPrivileges \</code> | Inspects or changes the named systemd unit; reload is used only after validation. |
| 4 | <code>-p ProtectSystem -p ReadWritePaths -p CapabilityBoundingSet</code> | Adds the shown option or argument to the continued command; the trailing backslash continues it when present. |

Add one sandbox directive at a time. Web servers may need privileged bind, logs, runtime PID/socket directories, certificate reads, and content. A perfect score that prevents reload or renewal is not production security.

## Logs and sensitive data

Sanitize credentials, session identifiers, personal data, authorization headers, and sensitive query/body data. Restrict log access, rotate predictably, send protected copies off-host, and monitor suppression or disk growth.

## Incident signs

Unexpected content changes, new virtual hosts/modules/listeners/users/keys, outbound connections, modified systemd timers, unfamiliar workers, high error bursts, cryptomining CPU, or web-root executables require incident handling—not a quick reinstall of one file.

## Review

1. Why must writable uploads be separate from executable content?
2. Why does hiding a version banner provide little protection?
3. Why can trusting every forwarding header bypass controls?
4. Why must a leaked secret be rotated?
5. Why is a maximum systemd security score not the goal?
