# Optional Appendix: LAMP, LEMP, and WordPress

LAMP and LEMP are useful practical subjects, but they do not replace the official LPIC-2 objectives.

- LAMP: Linux, Apache, MariaDB or MySQL, and PHP.
- LEMP: Linux, Nginx, MariaDB or MySQL, and PHP-FPM.

Use a supported PHP version. Do not hard-code an end-of-life stream.

## Safe site permissions

~~~bash
sudo install -d -o root -g root -m 0755 /srv/www/realsam.ir
sudo install -d -o www-data -g www-data -m 0750 /srv/www/realsam.ir/uploads
sudo find /srv/www/realsam.ir -type d -exec chmod 0755 {} +
sudo find /srv/www/realsam.ir -type f -exec chmod 0644 {} +
~~~

On RHEL-family systems the web account is commonly apache or nginx. Do not run recursive chmod against all of /var/www.

## Dedicated database

~~~sql
CREATE DATABASE realsam_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'realsam_app'@'localhost' IDENTIFIED BY 'REPLACE_WITH_A_RANDOM_SECRET';
GRANT ALL PRIVILEGES ON realsam_app.* TO 'realsam_app'@'localhost';
~~~

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

## SELinux

~~~bash
sudo semanage fcontext -a -t httpd_sys_content_t "/srv/www/realsam.ir(/.*)?"
sudo semanage fcontext -a -t httpd_sys_rw_content_t "/srv/www/realsam.ir/uploads(/.*)?"
sudo restorecon -Rv /srv/www/realsam.ir
~~~

Do not disable SELinux.

## Verification

~~~bash
curl -I https://www.realsam.ir
sudo ss -lntp
sudo systemctl --no-pager status nginx php-fpm mariadb
sudo journalctl -p warning..alert --since today
~~~
