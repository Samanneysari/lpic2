# 10 — DNS, CDN, Reverse Proxy, and Origin Identity

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

## Outcome

Understand how users reach an edge, how the edge reaches the origin, why DNS alone does not hide the origin, and how to preserve trustworthy client identity.

## End-to-end path

1. Client resolves `app.realsam.ir` through its configured resolver.
2. DNS returns CDN/reverse-proxy addresses, possibly by geography or anycast.
3. Client validates TLS against `app.realsam.ir` at the edge.
4. Edge applies policy/cache and connects to the configured origin IP/name.
5. Origin validates edge identity or network source and serves the intended virtual host.

The public DNS A/AAAA record normally changes to the CDN endpoint. The origin still has an IP and may have separate internal DNS. Reverse DNS/PTR of the origin does not route web traffic and does not make a CDN work.

## DNS evidence

```bash
getent ahosts app.realsam.ir
dig app.realsam.ir A
dig app.realsam.ir AAAA
dig app.realsam.ir CNAME
dig +trace app.realsam.ir
```

<!-- LINE-BY-LINE AUTO-10_DNS_CDN-01 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>getent ahosts app.realsam.ir</code> | Uses the system NSS configuration to resolve the selected host or database entry. |
| 2 | <code>dig app.realsam.ir A</code> | Queries DNS for the selected name, type, or server and prints the response. |
| 3 | <code>dig app.realsam.ir AAAA</code> | Queries DNS for the selected name, type, or server and prints the response. |
| 4 | <code>dig app.realsam.ir CNAME</code> | Queries DNS for the selected name, type, or server and prints the response. |
| 5 | <code>dig +trace app.realsam.ir</code> | Queries DNS for the selected name, type, or server and prints the response. |

`getent` tests application NSS behavior. `dig` tests DNS records. `+trace` follows delegation and does not represent the client's recursive cache or split-DNS path.

## DNS change plan

Inventory current records, TTL, authoritative provider, DNSSEC, certificates, CDN validation, origin configuration, IPv4/IPv6, health checks, and rollback. Lower TTL far enough before migration for existing higher-TTL cache entries to expire. Validate authoritative answers and multiple real recursive/client paths.

## Origin Host and TLS

If a CDN connects by origin IP but sends `Host: app.realsam.ir`, the origin virtual host can select correctly. If origin HTTPS is used, SNI and certificate validation must also match the configured origin name. Do not disable origin TLS verification because the origin uses a private/self-signed certificate; establish an explicit trust model.

Test origin while preserving public name:

```bash
curl --resolve app.realsam.ir:443:192.0.2.10 \
  https://app.realsam.ir/health
```

<!-- LINE-BY-LINE AUTO-10_DNS_CDN-02 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>curl --resolve app.realsam.ir:443:192.0.2.10 \</code> | Makes a bounded HTTP request with the shown name-resolution, header, output, or failure options. |
| 2 | <code>https://app.realsam.ir/health</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |

## Client address chain

The TCP peer at origin is the CDN. Original client IP arrives in a provider-defined header. Configure Nginx/Apache real-IP handling only for verified CDN ranges or authenticated proxy connections. Remove direct public origin access or treat direct requests separately. Otherwise an attacker can bypass the CDN and forge the header.

## Cache

Define cache key, methods, response codes, cookies, Authorization, `Vary`, query normalization, TTL, purge, stale behavior, and private-data exclusions. A cached 200 can hide an unhealthy origin; a cache-key mistake can leak personalized content.

## CDN security boundaries

CDN services can provide scale, TLS, WAF, bot/rate controls, and caching, but cannot fix an exposed origin, vulnerable application, leaked credentials, incorrect authorization, or unprotected admin endpoints. Provider dashboards/logs are security-sensitive evidence.

## Scenario: CDN shows 502 but origin curl works

Compare CDN origin address/port/protocol/SNI/Host, allowed source ranges, origin firewall, certificate chain/trust, IPv6, health-check path, timeout/body limits, and the exact CDN request ID/time. Local curl may use a different name, path, protocol, or network.

## Scenario: origin IP is still visible

Historical DNS, email headers, certificate transparency, other subdomains, direct services, shared hosting, and old records can reveal it. Rotate origin IP if threat model requires, restrict new IP to edge paths, separate mail/other services, and monitor direct requests. No DNS setting guarantees secrecy.

## Review

1. What record normally changes when enabling a CDN?
2. Why is PTR unrelated to normal web routing?
3. Why can local origin curl pass while CDN fails?
4. How can a forged client-IP header bypass controls?
5. Why is cache-key design a security issue?
