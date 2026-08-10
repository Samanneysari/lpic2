# Topic 208: HTTP Services

Objectives: 208.1, 208.2, 208.3, and 208.4

<!-- BEGIN BEGINNER FOUNDATION -->
## Learn the idea before running commands

### What an HTTP service does

A web client opens a TCP connection to a server, sends an HTTP request, and receives a response containing a status code, headers, and usually a body. The Host header lets one IP address serve several names. A web server selects a virtual host, maps the request to static content or an application, applies access rules, writes logs, and sends the response.

Apache and Nginx can both serve files and proxy requests. Apache is highly modular and commonly uses per-directory configuration. Nginx uses an event-driven design and is commonly used for static files, TLS termination, and reverse proxying. The exam expects both; they do not need to be installed on the same lab host.

### Files, processes, and permissions

The service normally starts as root only long enough to bind privileged ports, then handles requests with an unprivileged account. Content should be readable by that account but should not all be writable by it. Give write permission only to paths that an application must modify, such as a dedicated upload directory.

A name-based virtual host needs DNS, a matching ServerName or server_name, a listening address and port, readable content, and an allowed firewall path. Always validate syntax before reload, then test the exact hostname and inspect both access and error logs.

### What TLS adds

TLS authenticates the server with a certificate and protects traffic in transit. The private key stays secret on the server. A certificate binds public-key information to names such as www.realsam.ir. Modern clients verify the requested name against the Subject Alternative Name extension and build a trust chain to a trusted certificate authority.

The handshake uses asymmetric cryptography for authentication and key agreement, then efficient symmetric keys protect application data. HTTPS does not make an insecure application safe, but it prevents passive observers from reading or silently modifying traffic when certificate validation succeeds.

### Forward and reverse proxies

A Squid **forward proxy** acts for clients. Policy decides which clients may use it and which destinations or ports are allowed. An open forward proxy is unsafe.

An Nginx **reverse proxy** acts for servers. Clients connect to the proxy, which selects a backend and forwards the request. The proxy can centralize TLS and load distribution, but the backend must trust forwarded headers only from known proxies.

### Safe implementation sequence

1. Decide the service name, document root, backend, and trust boundary.
2. Confirm DNS for the chosen realsam.ir subdomain.
3. Install the package and inspect its default configuration.
4. Create the minimum required content and permissions.
5. Write one virtual host or proxy policy.
6. Validate syntax.
7. Reload rather than interrupting healthy connections when supported.
8. Test locally and remotely.
9. Inspect logs.
10. Add TLS and authentication only after plain request routing is understood.
<!-- END BEGINNER FOUNDATION -->

## 208.1 Basic Apache configuration

Apache is called apache2 on Debian-family systems and httpd on RHEL-family systems.

~~~bash
sudo apachectl configtest
sudo apache2ctl -S
sudo httpd -S
sudo systemctl reload apache2
sudo systemctl reload httpd
~~~

<!-- LINE-BY-LINE 1 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo apachectl configtest</code> | sudo requests administrator privileges for this operation. Validates or controls Apache using its generic command name. |
| 2 | <code>sudo apache2ctl -S</code> | sudo requests administrator privileges for this operation. Validates or controls Apache on Debian-family systems. |
| 3 | <code>sudo httpd -S</code> | sudo requests administrator privileges for this operation. Runs or inspects Apache on RHEL-family systems. |
| 4 | <code>sudo systemctl reload apache2</code> | sudo requests administrator privileges for this operation. Inspects or changes systemd units, targets, enablement, or system state. |
| 5 | <code>sudo systemctl reload httpd</code> | sudo requests administrator privileges for this operation. Inspects or changes systemd units, targets, enablement, or system state. |

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

<!-- LINE-BY-LINE 2 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code><VirtualHost *:80></code> | Opens the Apache configuration section named between angle brackets. |
| 2 | <code>ServerName www.realsam.ir</code> | Sets the primary hostname matched by this Apache virtual host. |
| 3 | <code>ServerAlias realsam.ir</code> | Adds alternate hostnames for the same Apache virtual host. |
| 4 | <code>DocumentRoot /srv/www/realsam.ir</code> | Sets the directory from which this virtual host serves files. |
| 6 | <code>ErrorLog  /var/log/httpd/realsam-error.log</code> | Selects the error-log file for this virtual host. |
| 7 | <code>CustomLog /var/log/httpd/realsam-access.log combined</code> | Selects the access-log file and format. |
| 9 | <code><Directory "/srv/www/realsam.ir"></code> | Opens the Apache configuration section named between angle brackets. |
| 10 | <code>Options -Indexes +FollowSymLinks</code> | Enables or disables the listed Apache directory features. |
| 11 | <code>AllowOverride None</code> | Controls which directives an .htaccess file may override. |
| 12 | <code>Require all granted</code> | Defines the Apache authorization requirement. |
| 13 | <code></Directory></code> | Closes the Apache configuration section opened above. |
| 15 | <code>Redirect permanent /old https://www.realsam.ir/new</code> | Returns the selected HTTP redirect to the new URL. |
| 16 | <code></VirtualHost></code> | Closes the Apache configuration section opened above. |

Use the distribution log directory. A dedicated-IP virtual host places a specific address in the VirtualHost argument.

Validate file ownership and access. Do not make the whole site writable by Apache. Do not use recursive 755 against user home directories.

### Authentication and authorization

~~~bash
sudo htpasswd -c /etc/httpd/auth/realsam-users alice
sudo htpasswd /etc/httpd/auth/realsam-users bob
~~~

<!-- LINE-BY-LINE 3 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo htpasswd -c /etc/httpd/auth/realsam-users alice</code> | sudo requests administrator privileges for this operation. Creates or updates an Apache-compatible hashed password file; -c must only create the file once. |
| 2 | <code>sudo htpasswd /etc/httpd/auth/realsam-users bob</code> | sudo requests administrator privileges for this operation. Creates or updates an Apache-compatible hashed password file; -c must only create the file once. |

Use -c only for the first creation.

~~~apache
<Directory "/srv/www/realsam.ir/private">
    AuthType Basic
    AuthName "Realsam private area"
    AuthUserFile /etc/httpd/auth/realsam-users
    Require valid-user
</Directory>
~~~

<!-- LINE-BY-LINE 4 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code><Directory "/srv/www/realsam.ir/private"></code> | Opens the Apache configuration section named between angle brackets. |
| 2 | <code>AuthType Basic</code> | Selects the Apache authentication mechanism. |
| 3 | <code>AuthName "Realsam private area"</code> | Sets the authentication realm text shown to a user. |
| 4 | <code>AuthUserFile /etc/httpd/auth/realsam-users</code> | Points to the protected password database. |
| 5 | <code>Require valid-user</code> | Defines the Apache authorization requirement. |
| 6 | <code></Directory></code> | Closes the Apache configuration section opened above. |

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

<!-- LINE-BY-LINE 5 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>curl -I http://www.realsam.ir</code> | Makes an HTTP request; -I requests response headers without downloading the body. |
| 2 | <code>tail -f /var/log/httpd/realsam-error.log</code> | Shows the end of a file; follow mode continues displaying new log entries. |
| 3 | <code>journalctl -u httpd</code> | Reads structured systemd journal records with the shown unit or time filter. |
| 4 | <code>journalctl -u apache2</code> | Reads structured systemd journal records with the shown unit or time filter. |

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

<!-- LINE-BY-LINE 6 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo openssl req -new -newkey rsa:3072 -nodes \</code> | sudo requests administrator privileges for this operation. Creates or inspects keys, CSRs, certificates, and TLS sessions as selected by its subcommand. The final backslash continues this logical command on the next physical line. |
| 2 | <code>-keyout /etc/pki/tls/private/realsam.ir.key \</code> | This physical line adds the shown option or argument to the command started on the previous line. The final backslash continues the same command on the next line. |
| 3 | <code>-out /root/realsam.ir.csr \</code> | This physical line adds the shown option or argument to the command started on the previous line. The final backslash continues the same command on the next line. |
| 4 | <code>-subj "/CN=www.realsam.ir" \</code> | This physical line adds the shown option or argument to the command started on the previous line. The final backslash continues the same command on the next line. |
| 5 | <code>-addext "subjectAltName=DNS:www.realsam.ir,DNS:realsam.ir"</code> | This physical line adds the shown option or argument to the command started on the previous line. |
| 7 | <code>sudo chmod 0600 /etc/pki/tls/private/realsam.ir.key</code> | sudo requests administrator privileges for this operation. Changes permission bits; verify the exact path before recursive use. |

For a test certificate:

~~~bash
sudo openssl req -x509 -newkey rsa:3072 -nodes -days 30 \
  -keyout /etc/pki/tls/private/realsam-test.key \
  -out /etc/pki/tls/certs/realsam-test.crt \
  -subj "/CN=www.realsam.ir" \
  -addext "subjectAltName=DNS:www.realsam.ir,DNS:realsam.ir"
~~~

<!-- LINE-BY-LINE 7 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo openssl req -x509 -newkey rsa:3072 -nodes -days 30 \</code> | sudo requests administrator privileges for this operation. Creates or inspects keys, CSRs, certificates, and TLS sessions as selected by its subcommand. The final backslash continues this logical command on the next physical line. |
| 2 | <code>-keyout /etc/pki/tls/private/realsam-test.key \</code> | This physical line adds the shown option or argument to the command started on the previous line. The final backslash continues the same command on the next line. |
| 3 | <code>-out /etc/pki/tls/certs/realsam-test.crt \</code> | This physical line adds the shown option or argument to the command started on the previous line. The final backslash continues the same command on the next line. |
| 4 | <code>-subj "/CN=www.realsam.ir" \</code> | This physical line adds the shown option or argument to the command started on the previous line. The final backslash continues the same command on the next line. |
| 5 | <code>-addext "subjectAltName=DNS:www.realsam.ir,DNS:realsam.ir"</code> | This physical line adds the shown option or argument to the command started on the previous line. |

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

<!-- LINE-BY-LINE 8 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code><VirtualHost *:443></code> | Opens the Apache configuration section named between angle brackets. |
| 2 | <code>ServerName www.realsam.ir</code> | Sets the primary hostname matched by this Apache virtual host. |
| 3 | <code>ServerAlias realsam.ir</code> | Adds alternate hostnames for the same Apache virtual host. |
| 4 | <code>DocumentRoot /srv/www/realsam.ir</code> | Sets the directory from which this virtual host serves files. |
| 6 | <code>SSLEngine on</code> | Enables TLS for this Apache virtual host. |
| 7 | <code>SSLCertificateFile /etc/pki/tls/certs/realsam-fullchain.pem</code> | Points to the server certificate plus required intermediate certificates. |
| 8 | <code>SSLCertificateKeyFile /etc/pki/tls/private/realsam.ir.key</code> | Points to the server private key, which must be tightly protected. |
| 10 | <code>SSLProtocol -all +TLSv1.2 +TLSv1.3</code> | Allows only the listed TLS protocol versions. |
| 11 | <code>ServerTokens Prod</code> | Limits server-version information in response headers. |
| 12 | <code>ServerSignature Off</code> | Disables detailed server signatures on generated pages. |
| 13 | <code>TraceEnable Off</code> | Disables the HTTP TRACE method. |
| 14 | <code></VirtualHost></code> | Closes the Apache configuration section opened above. |

SSLCertificateFile should contain the server certificate followed by required intermediate certificates on current Apache 2.4. SSLCertificateChainFile is obsolete on current Apache.

SNI lets several HTTPS names share an address. Learn SSLCACertificateFile, SSLCACertificatePath, SSLCipherSuite, and the operational risks of old protocols and ciphers.

Test:

~~~bash
sudo apachectl configtest
openssl s_client -connect www.realsam.ir:443 -servername www.realsam.ir -showcerts
curl -I https://www.realsam.ir
~~~

<!-- LINE-BY-LINE 9 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo apachectl configtest</code> | sudo requests administrator privileges for this operation. Validates or controls Apache using its generic command name. |
| 2 | <code>openssl s_client -connect www.realsam.ir:443 -servername www.realsam.ir -showcerts</code> | Creates or inspects keys, CSRs, certificates, and TLS sessions as selected by its subcommand. |
| 3 | <code>curl -I https://www.realsam.ir</code> | Makes an HTTP request; -I requests response headers without downloading the body. |

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

<!-- LINE-BY-LINE 10 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>acl realsam_lan src 10.20.0.0/24</code> | Creates a named Squid ACL that matches the shown source network, port, method, or authenticated user state. |
| 2 | <code>acl SSL_ports port 443</code> | Creates a named Squid ACL that matches the shown source network, port, method, or authenticated user state. |
| 3 | <code>acl Safe_ports port 80 443 1024-65535</code> | Creates a named Squid ACL that matches the shown source network, port, method, or authenticated user state. |
| 4 | <code>acl CONNECT method CONNECT</code> | Creates a named Squid ACL that matches the shown source network, port, method, or authenticated user state. |
| 6 | <code>http_access deny !Safe_ports</code> | Applies this Squid allow or deny rule in top-to-bottom order. |
| 7 | <code>http_access deny CONNECT !SSL_ports</code> | Applies this Squid allow or deny rule in top-to-bottom order. |
| 8 | <code>http_access allow localhost</code> | Applies this Squid allow or deny rule in top-to-bottom order. |
| 9 | <code>http_access allow realsam_lan</code> | Applies this Squid allow or deny rule in top-to-bottom order. |
| 10 | <code>http_access deny all</code> | Applies this Squid allow or deny rule in top-to-bottom order. |
| 12 | <code>http_port 3128</code> | Sets the port on which Squid accepts client proxy requests. |
| 13 | <code>cache_mem 128 MB</code> | Sets an approximate memory target for selected cached objects. |
| 14 | <code>maximum_object_size 64 MB</code> | Limits the largest object stored in the cache. |
| 15 | <code>access_log stdio:/var/log/squid/access.log</code> | Selects the service access-log destination. |

Validate before reload:

~~~bash
sudo squid -k parse
sudo systemctl reload squid
tail -f /var/log/squid/access.log
~~~

<!-- LINE-BY-LINE 11 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo squid -k parse</code> | sudo requests administrator privileges for this operation. Runs Squid or parses and controls its configuration. |
| 2 | <code>sudo systemctl reload squid</code> | sudo requests administrator privileges for this operation. Inspects or changes systemd units, targets, enablement, or system state. |
| 3 | <code>tail -f /var/log/squid/access.log</code> | Shows the end of a file; follow mode continues displaying new log entries. |

The objectives require awareness of client authentication. A basic NCSA example uses an auth helper and an ACL, but password transport must be protected by the network design:

~~~squid
auth_param basic program /usr/lib64/squid/basic_ncsa_auth /etc/squid/passwd
acl authenticated proxy_auth REQUIRED
http_access allow realsam_lan authenticated
~~~

<!-- LINE-BY-LINE 12 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>auth_param basic program /usr/lib64/squid/basic_ncsa_auth /etc/squid/passwd</code> | Configures the selected Squid authentication helper. |
| 2 | <code>acl authenticated proxy_auth REQUIRED</code> | Creates a named Squid ACL that matches the shown source network, port, method, or authenticated user state. |
| 3 | <code>http_access allow realsam_lan authenticated</code> | Applies this Squid allow or deny rule in top-to-bottom order. |

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

<!-- LINE-BY-LINE 13 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>server {</code> | Opens an Nginx virtual-server block. |
| 2 | <code>listen 80 default_server;</code> | Makes Nginx accept connections on the shown address and port; default_server marks the fallback virtual host. |
| 3 | <code>listen [::]:80 default_server;</code> | Makes Nginx accept connections on the shown address and port; default_server marks the fallback virtual host. |
| 4 | <code>server_name www.realsam.ir realsam.ir;</code> | Lists the hostnames matched by this Nginx server block. |
| 5 | <code>root /srv/www/realsam.ir;</code> | Sets the filesystem root used to resolve request paths. |
| 6 | <code>index index.html;</code> | Lists default files for a directory request. |
| 8 | <code>access_log /var/log/nginx/realsam-access.log;</code> | Selects the service access-log destination. |
| 9 | <code>error_log  /var/log/nginx/realsam-error.log;</code> | Selects the Nginx error-log destination. |
| 11 | <code>location / {</code> | Opens an Nginx location block for requests matching the shown path. |
| 12 | <code>try_files $uri $uri/ =404;</code> | Tests candidate paths in order and returns the final result if none exists. |
| 13 | <code>}</code> | Closes the configuration or multi-line value opened above. |
| 14 | <code>}</code> | Closes the configuration or multi-line value opened above. |

server_name with an underscore is not itself a catch-all. The default_server parameter on listen chooses the default server.

~~~bash
sudo nginx -t
sudo systemctl reload nginx
~~~

<!-- LINE-BY-LINE 14 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo nginx -t</code> | sudo requests administrator privileges for this operation. Runs Nginx or validates its complete configuration with -t. |
| 2 | <code>sudo systemctl reload nginx</code> | sudo requests administrator privileges for this operation. Inspects or changes systemd units, targets, enablement, or system state. |

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

<!-- LINE-BY-LINE 15 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>upstream realsam_backend {</code> | Opens the named Nginx backend pool used by proxy_pass. |
| 2 | <code>least_conn;</code> | Selects the backend with the fewest active connections. |
| 3 | <code>server 10.20.0.21:8080 max_fails=3 fail_timeout=30s;</code> | Adds this backend address and port, and marks it unavailable temporarily after the configured passive failures. |
| 4 | <code>server 10.20.0.22:8080 max_fails=3 fail_timeout=30s;</code> | Adds this backend address and port, and marks it unavailable temporarily after the configured passive failures. |
| 5 | <code>keepalive 16;</code> | Keeps the shown number of idle upstream connections available per worker. |
| 6 | <code>}</code> | Closes the configuration or multi-line value opened above. |
| 8 | <code>server {</code> | Opens an Nginx virtual-server block. |
| 9 | <code>listen 80;</code> | Makes Nginx accept connections on the shown address and port; default_server marks the fallback virtual host. |
| 10 | <code>server_name app.realsam.ir;</code> | Lists the hostnames matched by this Nginx server block. |
| 12 | <code>location / {</code> | Opens an Nginx location block for requests matching the shown path. |
| 13 | <code>proxy_pass http://realsam_backend;</code> | Forwards the request to the selected backend. |
| 14 | <code>proxy_http_version 1.1;</code> | Uses the selected HTTP version for the backend connection. |
| 15 | <code>proxy_set_header Host $host;</code> | Sets or replaces one header sent to the backend. |
| 16 | <code>proxy_set_header X-Real-IP $remote_addr;</code> | Sets or replaces one header sent to the backend. |
| 17 | <code>proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;</code> | Sets or replaces one header sent to the backend. |
| 18 | <code>proxy_set_header X-Forwarded-Proto $scheme;</code> | Sets or replaces one header sent to the backend. |
| 19 | <code>proxy_set_header Connection "";</code> | Sets or replaces one header sent to the backend. |
| 20 | <code>proxy_connect_timeout 5s;</code> | Limits time spent establishing a backend connection. |
| 21 | <code>proxy_read_timeout 60s;</code> | Limits the wait between reads from the backend. |
| 22 | <code>}</code> | Closes the configuration or multi-line value opened above. |
| 23 | <code>}</code> | Closes the configuration or multi-line value opened above. |

Open-source Nginx normally uses passive failure detection with max_fails and fail_timeout; do not describe it as active health checking unless an appropriate module or product provides that feature.

Back ends must trust forwarding headers only from known proxies. On SELinux systems, proxy connections may require the approved httpd_can_network_connect policy boolean:

~~~bash
sudo setsebool -P httpd_can_network_connect 1
~~~

<!-- LINE-BY-LINE 16 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo setsebool -P httpd_can_network_connect 1</code> | sudo requests administrator privileges for this operation. Changes an SELinux policy boolean; -P also makes it persistent. |

Enable only when the server is intended to make network connections.

## Exam checklist

Apache logs, .htaccess, httpd.conf, mod_auth_basic, mod_authz_host, mod_access_compat, htpasswd, AuthUserFile, AuthGroupFile, apachectl, apache2ctl, httpd, SSL files, openssl, SNI, SSL directives, Squid ACLs and authentication, squid.conf, http_access, /etc/nginx/, nginx, web server, and reverse proxy.

## Mini lab

Publish www.realsam.ir with Apache and HTTPS, protect one directory, inspect logs, configure Squid for one lab subnet with authentication, then configure Nginx as a web server and a reverse proxy for two back ends. Validate every configuration before reload.
