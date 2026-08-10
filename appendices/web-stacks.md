# Optional Appendix: LAMP, LEMP, and WordPress

LAMP and LEMP are useful practical subjects, but they do not replace the official LPIC-2 objectives.

- LAMP: Linux, Apache, MariaDB or MySQL, and PHP.
- LEMP: Linux, Nginx, MariaDB or MySQL, and PHP-FPM.

Use a supported PHP version. Do not hard-code an end-of-life stream.

<!-- BEGIN BEGINNER FOUNDATION -->
## Learn the idea before running commands

### What LAMP and LEMP are

A web application stack combines several independent services. Linux provides the operating system. Apache in LAMP or Nginx in LEMP accepts HTTP requests. MariaDB or MySQL stores structured application data. PHP executes application code. In a common LEMP design, Nginx sends PHP requests to a separate PHP-FPM process through FastCGI.

A request therefore crosses several permission and trust boundaries: browser to web server, web server to PHP, PHP to the database, and the application to writable files. Diagnose each boundary separately instead of making the entire site writable.

### Build the stack in this order

1. Choose supported distribution, database, and PHP versions.
2. Create DNS for www.realsam.ir and test it.
3. Install and start the database locally.
4. Create a dedicated database and least-privilege application user.
5. Install the web server and PHP packages.
6. Create the document root with restrictive ownership.
7. Configure one virtual host and PHP handler.
8. Validate each configuration before reload.
9. Install the application from a trusted source and verify it.
10. Add HTTPS, backups, updates, monitoring, and restore tests.

The database should not listen publicly unless the architecture requires it. The web service account should not own application code. Only directories that the application must modify should be writable by the runtime account.

### WordPress responsibilities

WordPress core, themes, and plugins are executable application code. A vulnerable or abandoned extension can compromise the site. Keep a minimal set, update it, and remove unused components. wp-config.php contains database credentials and salts and must not be publicly readable.

A complete backup includes both files and the database. Test restoration into a separate environment. HTTPS, a firewall, and SELinux/AppArmor help reduce risk but do not replace application updates and strong administrator authentication.
<!-- END BEGINNER FOUNDATION -->

## Safe site permissions

~~~bash
sudo install -d -o root -g root -m 0755 /srv/www/realsam.ir
sudo install -d -o www-data -g www-data -m 0750 /srv/www/realsam.ir/uploads
sudo find /srv/www/realsam.ir -type d -exec chmod 0755 {} +
sudo find /srv/www/realsam.ir -type f -exec chmod 0644 {} +
~~~

<!-- LINE-BY-LINE 1 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo install -d -o root -g root -m 0755 /srv/www/realsam.ir</code> | sudo requests administrator privileges for this operation. Creates a file or directory with explicit owner, group, and permission mode. |
| 2 | <code>sudo install -d -o www-data -g www-data -m 0750 /srv/www/realsam.ir/uploads</code> | sudo requests administrator privileges for this operation. Creates a file or directory with explicit owner, group, and permission mode. |
| 3 | <code>sudo find /srv/www/realsam.ir -type d -exec chmod 0755 {} +</code> | sudo requests administrator privileges for this operation. Selects matching files or directories and runs the requested safe action on them. |
| 4 | <code>sudo find /srv/www/realsam.ir -type f -exec chmod 0644 {} +</code> | sudo requests administrator privileges for this operation. Selects matching files or directories and runs the requested safe action on them. |

On RHEL-family systems the web account is commonly apache or nginx. Do not run recursive chmod against all of /var/www.

## Dedicated database

~~~sql
CREATE DATABASE realsam_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'realsam_app'@'localhost' IDENTIFIED BY 'REPLACE_WITH_A_RANDOM_SECRET';
GRANT ALL PRIVILEGES ON realsam_app.* TO 'realsam_app'@'localhost';
~~~

<!-- LINE-BY-LINE 2 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>CREATE DATABASE realsam_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;</code> | Creates a separate application database with the selected character set and collation. |
| 2 | <code>CREATE USER 'realsam_app'@'localhost' IDENTIFIED BY 'REPLACE_WITH_A_RANDOM_SECRET';</code> | Creates a database login limited to local connections; replace the placeholder with a generated secret. |
| 3 | <code>GRANT ALL PRIVILEGES ON realsam_app.* TO 'realsam_app'@'localhost';</code> | Grants the application user privileges only on the named application database. |

Never commit the real secret. Do not connect a web application with a database administrator account.

## WordPress checklist

- Download only from wordpress.org.
- Verify checksums when possible.
- Generate unique authentication salts.
- Protect wp-config.php.
- Update the core, plugins, and themes.
- Remove unused extensions.
- Use HTTPS for www.realsam.ir.
- Make only required upload paths writable.
- Back up both files and database.
- Test restoration.
- Remove phpinfo test files.

## Firewall

~~~bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
~~~

<!-- LINE-BY-LINE 3 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo firewall-cmd --permanent --add-service=http</code> | sudo requests administrator privileges for this operation. Changes firewalld policy; permanent rules become active after a reload. |
| 2 | <code>sudo firewall-cmd --permanent --add-service=https</code> | sudo requests administrator privileges for this operation. Changes firewalld policy; permanent rules become active after a reload. |
| 3 | <code>sudo firewall-cmd --reload</code> | sudo requests administrator privileges for this operation. Changes firewalld policy; permanent rules become active after a reload. |

## SELinux

~~~bash
sudo semanage fcontext -a -t httpd_sys_content_t "/srv/www/realsam.ir(/.*)?"
sudo semanage fcontext -a -t httpd_sys_rw_content_t "/srv/www/realsam.ir/uploads(/.*)?"
sudo restorecon -Rv /srv/www/realsam.ir
~~~

<!-- LINE-BY-LINE 4 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo semanage fcontext -a -t httpd_sys_content_t "/srv/www/realsam.ir(/.*)?"</code> | sudo requests administrator privileges for this operation. Adds or changes a persistent SELinux policy mapping. |
| 2 | <code>sudo semanage fcontext -a -t httpd_sys_rw_content_t "/srv/www/realsam.ir/uploads(/.*)?"</code> | sudo requests administrator privileges for this operation. Adds or changes a persistent SELinux policy mapping. |
| 3 | <code>sudo restorecon -Rv /srv/www/realsam.ir</code> | sudo requests administrator privileges for this operation. Applies persistent SELinux labels to the selected path. |

Do not disable SELinux.

## Verification

~~~bash
curl -I https://www.realsam.ir
sudo ss -lntp
sudo systemctl --no-pager status nginx php-fpm mariadb
sudo journalctl -p warning..alert --since today
~~~

<!-- LINE-BY-LINE 5 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>curl -I https://www.realsam.ir</code> | Makes an HTTP request; -I requests response headers without downloading the body. |
| 2 | <code>sudo ss -lntp</code> | sudo requests administrator privileges for this operation. Displays listening or connected sockets and summary counters. |
| 3 | <code>sudo systemctl --no-pager status nginx php-fpm mariadb</code> | sudo requests administrator privileges for this operation. Inspects or changes systemd units, targets, enablement, or system state. |
| 4 | <code>sudo journalctl -p warning..alert --since today</code> | sudo requests administrator privileges for this operation. Reads structured systemd journal records with the shown unit or time filter. |
