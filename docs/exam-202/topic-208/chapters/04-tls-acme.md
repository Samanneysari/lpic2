# 04 — TLS, Certificates, and ACME

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

## Outcome

Understand TLS identity and keys, deploy certificates, automate renewal, and distinguish DNS, TCP, TLS, and HTTP failures.

## TLS 1.3 mental model

After TCP (or QUIC for HTTP/3) connectivity:

1. ClientHello proposes version, algorithms, key share, SNI, and extensions.
2. ServerHello selects parameters and supplies its key share.
3. Server sends certificate chain and proves possession of the private key.
4. Client validates signatures, trust path, name, validity period, key usage, and policy.
5. Both derive traffic keys and authenticate the transcript.
6. Encrypted HTTP begins.

TLS protects data in transit and authenticates the endpoint under the trust model. It does not prove the application or host is uncompromised and does not hide all metadata.

## Certificate objects

- Private key: secret signing/key-agreement material; never place in Git or tickets.
- Leaf certificate: binds public key to DNS names and constraints.
- Intermediate certificate: connects leaf issuer toward a trusted root.
- Root certificate: trust anchor normally held by the client.
- CSR: public key plus requested identity signed by the private key; not a certificate.

Inspect a file:

```bash
openssl x509 -in fullchain.pem -noout \
  -subject -issuer -serial -dates -fingerprint -sha256 \
  -ext subjectAltName -ext keyUsage -ext extendedKeyUsage
```

<!-- LINE-BY-LINE AUTO-04_TLS_ACME-01 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>openssl x509 -in fullchain.pem -noout \</code> | Uses OpenSSL to create or inspect keys, CSRs, certificates, or a TLS connection. |
| 2 | <code>-subject -issuer -serial -dates -fingerprint -sha256 \</code> | Adds the shown option or argument to the continued command; the trailing backslash continues it when present. |
| 3 | <code>-ext subjectAltName -ext keyUsage -ext extendedKeyUsage</code> | Adds the shown option or argument to the continued command; the trailing backslash continues it when present. |

Modern hostname validation uses Subject Alternative Name. A matching Common Name is not a safe replacement for missing SAN under modern rules.

Check key/certificate public material matches without exposing the private key:

```bash
openssl pkey -in privkey.pem -pubout -outform DER |
  openssl sha256
openssl x509 -in cert.pem -pubkey -noout |
  openssl pkey -pubin -outform DER |
  openssl sha256
```

<!-- LINE-BY-LINE AUTO-04_TLS_ACME-02 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>openssl pkey -in privkey.pem -pubout -outform DER &#124;</code> | Uses OpenSSL to create or inspect keys, CSRs, certificates, or a TLS connection. |
| 2 | <code>openssl sha256</code> | Uses OpenSSL to create or inspect keys, CSRs, certificates, or a TLS connection. |
| 3 | <code>openssl x509 -in cert.pem -pubkey -noout &#124;</code> | Uses OpenSSL to create or inspect keys, CSRs, certificates, or a TLS connection. |
| 4 | <code>openssl pkey -pubin -outform DER &#124;</code> | Uses OpenSSL to create or inspect keys, CSRs, certificates, or a TLS connection. |
| 5 | <code>openssl sha256</code> | Uses OpenSSL to create or inspect keys, CSRs, certificates, or a TLS connection. |

The hashes should match. Running the private-key command requires authorized access; protect terminal output and key permissions.

## Live endpoint validation

```bash
openssl s_client -connect 192.0.2.10:443 \
  -servername app.realsam.ir \
  -verify_hostname app.realsam.ir \
  -verify_return_error </dev/null
```

<!-- LINE-BY-LINE AUTO-04_TLS_ACME-03 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>openssl s_client -connect 192.0.2.10:443 \</code> | Uses OpenSSL to create or inspect keys, CSRs, certificates, or a TLS connection. |
| 2 | <code>-servername app.realsam.ir \</code> | Adds the shown option or argument to the continued command; the trailing backslash continues it when present. |
| 3 | <code>-verify_hostname app.realsam.ir \</code> | Adds the shown option or argument to the continued command; the trailing backslash continues it when present. |
| 4 | <code>-verify_return_error &lt;/dev/null</code> | Adds the shown option or argument to the continued command; the trailing backslash continues it when present. |

- Connect to the selected address while sending intended SNI.
- Verify the DNS hostname independently of where DNS points.
- Return verification failure rather than continuing silently.

Then test HTTP:

```bash
curl --fail --show-error --silent \
  --resolve app.realsam.ir:443:192.0.2.10 \
  https://app.realsam.ir/health
```

<!-- LINE-BY-LINE AUTO-04_TLS_ACME-04 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>curl --fail --show-error --silent \</code> | Makes a bounded HTTP request with the shown name-resolution, header, output, or failure options. |
| 2 | <code>--resolve app.realsam.ir:443:192.0.2.10 \</code> | Adds the shown option or argument to the continued command; the trailing backslash continues it when present. |
| 3 | <code>https://app.realsam.ir/health</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |

Never use `-k`/`--insecure` as a production fix; it disables identity validation for that test.

## Nginx TLS virtual host

```nginx
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name app.realsam.ir;

    ssl_certificate /etc/pki/tls/certs/app.fullchain.pem;
    ssl_certificate_key /etc/pki/tls/private/app.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://app_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

<!-- LINE-BY-LINE AUTO-04_TLS_ACME-05 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>server {</code> | Defines a listening virtual server or an upstream backend, depending on its context. It opens the related configuration block. |
| 2 | <code>listen 443 ssl;</code> | Selects the local address, port, and optional listener parameters. |
| 3 | <code>listen [::]:443 ssl;</code> | Selects the local address, port, and optional listener parameters. |
| 4 | <code>server_name app.realsam.ir;</code> | Lists hostnames that select this Nginx server block. |
| 5 | <code>ssl_certificate /etc/pki/tls/certs/app.fullchain.pem;</code> | Points Nginx to the server certificate and intermediate chain file. |
| 6 | <code>ssl_certificate_key /etc/pki/tls/private/app.key;</code> | Points Nginx to the protected private key for this certificate. |
| 7 | <code>ssl_protocols TLSv1.2 TLSv1.3;</code> | Allows only the listed TLS protocol versions. |
| 8 | <code>location / {</code> | Opens a URI-matching block whose rules apply to matching requests. It opens the related configuration block. |
| 9 | <code>proxy_pass http://app_backend;</code> | Forwards matching requests to the named upstream URL. |
| 10 | <code>proxy_set_header Host $host;</code> | Overwrites the named request header before forwarding it upstream. |
| 11 | <code>proxy_set_header X-Forwarded-Proto https;</code> | Overwrites the named request header before forwarding it upstream. |
| 12 | <code>}</code> | Opens or closes the current configuration block. |
| 13 | <code>}</code> | Opens or closes the current configuration block. |

Use current distribution/vendor cipher guidance rather than freezing a copied cipher list. Ensure private-key owner/mode permits the master process and no broader access. Validate SELinux labels and any service sandbox.

## Apache TLS virtual host

```apache
<VirtualHost *:443>
    ServerName app.realsam.ir
    SSLEngine on
    SSLCertificateFile /etc/pki/tls/certs/app.fullchain.pem
    SSLCertificateKeyFile /etc/pki/tls/private/app.key
    SSLProtocol -all +TLSv1.2 +TLSv1.3
</VirtualHost>
```

<!-- LINE-BY-LINE AUTO-04_TLS_ACME-06 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>&lt;VirtualHost *:443&gt;</code> | Opens an Apache `VirtualHost` section for the shown scope. |
| 2 | <code>ServerName app.realsam.ir</code> | Sets the primary hostname for this Apache virtual host. |
| 3 | <code>SSLEngine on</code> | Enables TLS processing for this Apache virtual host. |
| 4 | <code>SSLCertificateFile /etc/pki/tls/certs/app.fullchain.pem</code> | Points Apache to the server certificate and required intermediate chain. |
| 5 | <code>SSLCertificateKeyFile /etc/pki/tls/private/app.key</code> | Points Apache to the protected server private key. |
| 6 | <code>SSLProtocol -all +TLSv1.2 +TLSv1.3</code> | Enables and disables TLS protocol versions. |
| 7 | <code>&lt;/VirtualHost&gt;</code> | Closes the Apache configuration section opened above. |

Directive availability depends on Apache/OpenSSL version. Run `apachectl configtest` and verify the live endpoint.

## ACME and Certbot

ACME automates domain-control validation and certificate lifecycle. Common challenge models:

- HTTP-01: CA fetches a token under `/.well-known/acme-challenge/` over port 80.
- DNS-01: a TXT record proves DNS control and supports wildcard names; API credentials become high-value secrets.
- TLS-ALPN-01: validation through a special TLS ALPN exchange.

Use distribution-supported Certbot packaging/instructions. Inspect existing lineages:

```bash
sudo certbot certificates
sudo certbot renew --dry-run
systemctl list-timers --all | grep -i certbot
```

<!-- LINE-BY-LINE AUTO-04_TLS_ACME-07 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo certbot certificates</code> | Requests, renews, or tests ACME-managed certificates using the selected plugin and options. |
| 2 | <code>sudo certbot renew --dry-run</code> | Requests, renews, or tests ACME-managed certificates using the selected plugin and options. |
| 3 | <code>systemctl list-timers --all &#124; grep -i certbot</code> | Inspects or changes the named systemd unit; reload is used only after validation. |

`renew --dry-run` tests against a staging environment when supported. It does not prove future DNS, firewall, rate limits, permissions, or deploy-hook behavior.

After renewal, the web process must load new files. A deploy hook should validate and reload the exact service only after successful renewal. Test live serial/fingerprint, not only file modification time.

## Redirect and HSTS

HTTP redirect:

```nginx
server {
    listen 80;
    server_name app.realsam.ir;
    return 308 https://$host$request_uri;
}
```

<!-- LINE-BY-LINE AUTO-04_TLS_ACME-08 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>server {</code> | Defines a listening virtual server or an upstream backend, depending on its context. It opens the related configuration block. |
| 2 | <code>listen 80;</code> | Selects the local address, port, and optional listener parameters. |
| 3 | <code>server_name app.realsam.ir;</code> | Lists hostnames that select this Nginx server block. |
| 4 | <code>return 308 https://$host$request_uri;</code> | Applies the `return` directive with the shown value in the current context. |
| 5 | <code>}</code> | Opens or closes the current configuration block. |

Validate Host policy to avoid open redirect behavior. HSTS:

```nginx
add_header Strict-Transport-Security "max-age=300" always;
```

<!-- LINE-BY-LINE AUTO-04_TLS_ACME-09 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>add_header Strict-Transport-Security "max-age=300" always;</code> | Adds the named response header under the directive's status and inheritance rules. |

Begin with a short duration. Increase only after every subdomain and recovery path is HTTPS-ready. `includeSubDomains` and preload are difficult to reverse quickly.

## Scenario table

| Symptom | First evidence |
| --- | --- |
| timeout | route, port, capture, listener/firewall |
| wrong certificate | address, SNI, virtual-host map, load-balancer replica |
| expired/not-yet-valid | file/live dates and client/server time |
| unknown issuer | served intermediate chain and client trust store |
| name mismatch | requested name, SAN, redirect target |
| file renewed but old live serial | process reload, replicas, CDN/edge termination |

## Review

1. What does SNI choose and what does SAN validate?
2. Why must the intermediate chain be served?
3. Why is HTTP-01 affected by redirects/proxies/firewalls?
4. Why does renewal success not prove deployment?
5. Why should HSTS begin conservatively?
