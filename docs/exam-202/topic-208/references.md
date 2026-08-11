# Official References

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

- [Official LPIC-2 exam 201 and 202 objectives](https://www.lpi.org/our-certifications/exam-201-202-objectives/)

Use documentation matching the installed package version. Start with:

```bash
nginx -V
httpd -V
apachectl -M
openssl version -a
rpm -q nginx httpd openssl
```

<!-- LINE-BY-LINE AUTO-REFERENCES-01 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>nginx -V</code> | Invokes Nginx with the shown validation, build-information, or configuration-dump option. |
| 2 | <code>httpd -V</code> | Inspects or controls the Apache HTTP Server using its RHEL-family command name. |
| 3 | <code>apachectl -M</code> | Validates, inspects, or controls Apache through its administration wrapper. |
| 4 | <code>openssl version -a</code> | Uses OpenSSL to create or inspect keys, CSRs, certificates, or a TLS connection. |
| 5 | <code>rpm -q nginx httpd openssl</code> | Queries installed RPM package versions and metadata. |

## Web servers and proxies

- [Nginx documentation](https://nginx.org/en/docs/)
- [Nginx proxy module](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)
- [Nginx upstream module](https://nginx.org/en/docs/http/ngx_http_upstream_module.html)
- [Apache HTTP Server 2.4 documentation](https://httpd.apache.org/docs/2.4/)
- [Apache virtual-host examples](https://httpd.apache.org/docs/2.4/vhosts/examples.html)
- [Apache mod_ssl](https://httpd.apache.org/docs/2.4/mod/mod_ssl.html)
- [Squid configuration reference](https://www.squid-cache.org/Doc/config/)
- [HAProxy configuration manual](https://www.haproxy.com/documentation/haproxy-configuration-manual/latest/)
- [HAProxy health checks](https://www.haproxy.com/documentation/haproxy-configuration-tutorials/reliability/health-checks/)
- [PHP-FPM documentation](https://www.php.net/manual/en/install.fpm.php)

## TLS, DNS, and protocols

- [OpenSSL documentation](https://docs.openssl.org/)
- [Certbot user guide](https://eff-certbot.readthedocs.io/en/stable/using.html)
- [Let's Encrypt documentation](https://letsencrypt.org/docs/)
- [IETF HTTP specifications](https://httpwg.org/specs/)
- [IETF TLS 1.3, RFC 8446](https://www.rfc-editor.org/rfc/rfc8446)
- [IETF DNS terminology, RFC 9499](https://www.rfc-editor.org/rfc/rfc9499)

## Linux platform

- [RHEL networking documentation](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/configuring_and_managing_networking/)
- [firewalld documentation](https://firewalld.org/documentation/)
- [SELinux Project](https://selinuxproject.org/page/Main_Page)
- [systemd manuals](https://www.freedesktop.org/software/systemd/man/latest/)

Secondary examples are hypotheses until verified with official documentation and a disposable lab. Record versions with every production runbook.
