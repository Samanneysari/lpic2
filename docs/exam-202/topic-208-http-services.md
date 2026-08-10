# Topic 208: HTTP Services

Objectives: 208.1, 208.2, 208.3, and 208.4

## 208.1 Basic Apache configuration

Apache is called apache2 on Debian-family systems and httpd on RHEL-family systems.

~~~bash
sudo apachectl configtest
sudo apache2ctl -S
sudo httpd -S
sudo systemctl reload apache2
sudo systemctl reload httpd
~~~

Important configuration includes httpd.conf, included conf files, modules, virtual hosts, access logs, and error logs.

### Name-based virtual host

~~~apache
<VirtualHost *:80>
    ServerName www.realsam.ir
    ServerAlias realsam.ir
    DocumentRoot /srv/www/realsam.ir

    ErrorLog  /var/log/httpd/realsam-error.log
    CustomLog /var/log/httpd/realsam-access.log combined

    <Directory "/srv/www/realsam.ir">
        Options -Indexes +FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>

    Redirect permanent /old https://www.realsam.ir/new
</VirtualHost>
~~~

Use the distribution log directory. A dedicated-IP virtual host places a specific address in the VirtualHost argument.

Validate file ownership and access. Do not make the whole site writable by Apache. Do not use recursive 755 against user home directories.

### Authentication and authorization

~~~bash
sudo htpasswd -c /etc/httpd/auth/realsam-users alice
sudo htpasswd /etc/httpd/auth/realsam-users bob
~~~

Use -c only for the first creation.

~~~apache
<Directory "/srv/www/realsam.ir/private">
    AuthType Basic
    AuthName "Realsam private area"
    AuthUserFile /etc/httpd/auth/realsam-users
    Require valid-user
</Directory>
~~~

Basic authentication must be protected by HTTPS. Know AuthGroupFile, mod_auth_basic, mod_authz_host, and mod_access_compat.

.htaccess allows directory-level configuration only when AllowOverride permits it. Central configuration is normally faster and easier to audit.

### Performance and dynamic content

Know KeepAlive, Timeout, ServerLimit, MaxRequestWorkers, MinSpareServers, MaxSpareServers, and the prefork, worker, and event MPMs. Values depend on RAM, application behavior, and concurrency; do not copy a tuning value without measurement.

Use mod_status carefully and restrict access. Understand PHP and mod_perl integration even when a current deployment uses PHP-FPM instead of an in-process module.

Monitor:

~~~bash
curl -I http://www.realsam.ir
tail -f /var/log/httpd/realsam-error.log
journalctl -u httpd
journalctl -u apache2
~~~

## 208.2 Apache HTTPS

TLS uses asymmetric cryptography for authentication and key agreement, then symmetric session keys for application data. A CA issues and signs a certificate based on validated identity information and a CSR.

Generate a protected private key and CSR with SAN:

~~~bash
sudo openssl req -new -newkey rsa:3072 -nodes \
  -keyout /etc/pki/tls/private/realsam.ir.key \
  -out /root/realsam.ir.csr \
  -subj "/CN=www.realsam.ir" \
  -addext "subjectAltName=DNS:www.realsam.ir,DNS:realsam.ir"

sudo chmod 0600 /etc/pki/tls/private/realsam.ir.key
~~~

For a test certificate:

~~~bash
sudo openssl req -x509 -newkey rsa:3072 -nodes -days 30 \
  -keyout /etc/pki/tls/private/realsam-test.key \
  -out /etc/pki/tls/certs/realsam-test.crt \
  -subj "/CN=www.realsam.ir" \
  -addext "subjectAltName=DNS:www.realsam.ir,DNS:realsam.ir"
~~~

HTTPS virtual host:

~~~apache
<VirtualHost *:443>
    ServerName www.realsam.ir
    ServerAlias realsam.ir
    DocumentRoot /srv/www/realsam.ir

    SSLEngine on
    SSLCertificateFile /etc/pki/tls/certs/realsam-fullchain.pem
    SSLCertificateKeyFile /etc/pki/tls/private/realsam.ir.key

    SSLProtocol -all +TLSv1.2 +TLSv1.3
    ServerTokens Prod
    ServerSignature Off
    TraceEnable Off
</VirtualHost>
~~~

SSLCertificateFile should contain the server certificate followed by required intermediate certificates on current Apache 2.4. SSLCertificateChainFile is obsolete on current Apache.

SNI lets several HTTPS names share an address. Learn SSLCACertificateFile, SSLCACertificatePath, SSLCipherSuite, and the operational risks of old protocols and ciphers.

Test:

~~~bash
sudo apachectl configtest
openssl s_client -connect www.realsam.ir:443 -servername www.realsam.ir -showcerts
curl -I https://www.realsam.ir
~~~

If Certbot is used, test automatic renewal with its supported dry-run command and confirm the systemd timer.

## 208.3 Squid caching proxy

Do not erase the packaged squid.conf. Preserve its Safe_ports and localhost protections, then add a small included policy or controlled edits.

~~~squid
acl realsam_lan src 10.20.0.0/24
acl SSL_ports port 443
acl Safe_ports port 80 443 1024-65535
acl CONNECT method CONNECT

http_access deny !Safe_ports
http_access deny CONNECT !SSL_ports
http_access allow localhost
http_access allow realsam_lan
http_access deny all

http_port 3128
cache_mem 128 MB
maximum_object_size 64 MB
access_log stdio:/var/log/squid/access.log
~~~

Validate before reload:

~~~bash
sudo squid -k parse
sudo systemctl reload squid
tail -f /var/log/squid/access.log
~~~

The objectives require awareness of client authentication. A basic NCSA example uses an auth helper and an ACL, but password transport must be protected by the network design:

~~~squid
auth_param basic program /usr/lib64/squid/basic_ncsa_auth /etc/squid/passwd
acl authenticated proxy_auth REQUIRED
http_access allow realsam_lan authenticated
~~~

Helper paths differ. Test the installed package. Resource controls include cache_mem, cache_dir, object-size limits, and log rotation.

A forward proxy does not automatically make clients anonymous or safe. Headers, policy, TLS behavior, and application traffic matter.

## 208.4 Nginx web and reverse proxy

### Basic web server

~~~nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name www.realsam.ir realsam.ir;
    root /srv/www/realsam.ir;
    index index.html;

    access_log /var/log/nginx/realsam-access.log;
    error_log  /var/log/nginx/realsam-error.log;

    location / {
        try_files $uri $uri/ =404;
    }
}
~~~

server_name with an underscore is not itself a catch-all. The default_server parameter on listen chooses the default server.

~~~bash
sudo nginx -t
sudo systemctl reload nginx
~~~

### Reverse proxy

~~~nginx
upstream realsam_backend {
    least_conn;
    server 10.20.0.21:8080 max_fails=3 fail_timeout=30s;
    server 10.20.0.22:8080 max_fails=3 fail_timeout=30s;
    keepalive 16;
}

server {
    listen 80;
    server_name app.realsam.ir;

    location / {
        proxy_pass http://realsam_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        proxy_connect_timeout 5s;
        proxy_read_timeout 60s;
    }
}
~~~

Open-source Nginx normally uses passive failure detection with max_fails and fail_timeout; do not describe it as active health checking unless an appropriate module or product provides that feature.

Back ends must trust forwarding headers only from known proxies. On SELinux systems, proxy connections may require the approved httpd_can_network_connect policy boolean:

~~~bash
sudo setsebool -P httpd_can_network_connect 1
~~~

Enable only when the server is intended to make network connections.

## Exam checklist

Apache logs, .htaccess, httpd.conf, mod_auth_basic, mod_authz_host, mod_access_compat, htpasswd, AuthUserFile, AuthGroupFile, apachectl, apache2ctl, httpd, SSL files, openssl, SNI, SSL directives, Squid ACLs and authentication, squid.conf, http_access, /etc/nginx/, nginx, web server, and reverse proxy.

## Mini lab

Publish www.realsam.ir with Apache and HTTPS, protect one directory, inspect logs, configure Squid for one lab subnet with authentication, then configure Nginx as a web server and a reverse proxy for two back ends. Validate every configuration before reload.
