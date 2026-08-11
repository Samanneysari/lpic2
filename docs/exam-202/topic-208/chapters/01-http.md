# 01 — HTTP from Request to Response

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

## Outcome

Understand what a web server receives, chooses, forwards, caches, logs, and returns.

## URL and request

For `https://app.realsam.ir:443/api/items?id=7`:

- `https` selects HTTP protected by TLS.
- `app.realsam.ir` is the authority hostname and participates in DNS, TLS SNI, certificate validation, and virtual-host selection.
- `443` is the explicit port.
- `/api/items` is the path.
- `id=7` is the query string; it is commonly logged and must not contain secrets.

Example HTTP/1.1 request:

```http
GET /health HTTP/1.1
Host: app.realsam.ir
User-Agent: curl/8.x
Accept: */*
Connection: close
```

<!-- LINE-BY-LINE AUTO-01_HTTP-01 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>GET /health HTTP/1.1</code> | Defines the HTTP request method, target, and protocol version. |
| 2 | <code>Host: app.realsam.ir</code> | Sets or records the `Host` field in this protocol or report example. |
| 3 | <code>User-Agent: curl/8.x</code> | Sets or records the `User-Agent` field in this protocol or report example. |
| 4 | <code>Accept: */*</code> | Sets or records the `Accept` field in this protocol or report example. |
| 5 | <code>Connection: close</code> | Sets or records the `Connection` field in this protocol or report example. |

The request line contains method, target, and protocol version. `Host` selects a name-based site. Headers carry metadata. A blank line ends headers. A request body may follow for methods such as POST.

## Methods and semantics

| Method | Intended meaning | Important operational point |
| --- | --- | --- |
| `GET` | retrieve representation | should be safe; can be cached under correct rules |
| `HEAD` | GET metadata without response body | useful but application must implement consistently |
| `POST` | process submitted representation | usually not idempotent |
| `PUT` | create/replace target state | intended to be idempotent |
| `PATCH` | partial modification | semantics depend on patch format |
| `DELETE` | remove target state | repeated request should converge, but side effects matter |
| `OPTIONS` | describe communication options | used by CORS preflight |

Safe and idempotent are protocol properties, not guarantees that every application is correctly implemented. A proxy retry of a non-idempotent request can duplicate work.

## Status classes

- `1xx`: informational.
- `2xx`: request handled successfully; `204` deliberately has no body.
- `3xx`: redirect or conditional/cache result; `301/308` are persistent, `302/307` temporary with method differences.
- `4xx`: request/client-side condition; `401` means authentication required and `403` means understood but forbidden.
- `5xx`: server or gateway failed; `502` commonly means an invalid upstream response, `503` unavailable, `504` upstream timeout.

A load balancer returning 502 does not prove the application process is down. It may be protocol mismatch, DNS, TLS validation, wrong socket, reset, malformed headers, or no healthy backends.

## Headers that affect operations

| Header | Purpose and risk |
| --- | --- |
| `Host` / `:authority` | target virtual host; validate allowed values |
| `Content-Type` | media type of body |
| `Content-Length` / transfer framing | message boundary; conflicting framing is security-sensitive |
| `Location` | redirect target |
| `Cache-Control`, `ETag`, `Last-Modified` | cache policy and validation |
| `Authorization`, `Cookie`, `Set-Cookie` | credentials/session data; never log blindly |
| `Forwarded`, `X-Forwarded-For`, `X-Forwarded-Proto` | proxy metadata; trust only from controlled proxies |
| `Strict-Transport-Security` | tells browsers to require HTTPS after a valid HTTPS response |

## HTTP versions

HTTP/1.1 reuses TCP connections but requests can block behind prior responses. HTTP/2 multiplexes streams over one TCP connection and compresses headers. HTTP/3 carries HTTP over QUIC/UDP and changes transport behavior. Application semantics remain HTTP, but firewall, observability, TLS, and performance troubleshooting differ.

Use curl to see negotiated behavior:

```bash
curl --verbose --http2 --max-time 10 https://app.realsam.ir/health
```

<!-- LINE-BY-LINE AUTO-01_HTTP-02 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>curl --verbose --http2 --max-time 10 https://app.realsam.ir/health</code> | Makes a bounded HTTP request with the shown name-resolution, header, output, or failure options. |

Availability of HTTP/2 depends on curl build and server configuration. Browser fallback can hide HTTP/3 failure.

## Connections and timeouts

Separate:

- DNS timeout;
- TCP connect timeout;
- TLS handshake timeout;
- request-header/body read timeout;
- upstream connect/read/send timeout;
- client response write timeout;
- idle keepalive timeout.

One huge universal timeout ties up workers and hides failed dependencies. One tiny timeout fails normal slow operations. Define each from latency objectives and retry behavior.

## Caching

A cache key usually needs scheme, authority, path, query, and selected request headers. Incorrect keys can leak one user's response to another. Responses with authentication, cookies, or personal data require explicit design.

Inspect:

```bash
curl -sS -D - -o /dev/null https://app.realsam.ir/static/app.css
curl -sS -H 'If-None-Match: <etag>' -D - -o /dev/null \
  https://app.realsam.ir/static/app.css
```

<!-- LINE-BY-LINE AUTO-01_HTTP-03 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>curl -sS -D - -o /dev/null https://app.realsam.ir/static/app.css</code> | Makes a bounded HTTP request with the shown name-resolution, header, output, or failure options. |
| 2 | <code>curl -sS -H 'If-None-Match: &lt;etag&gt;' -D - -o /dev/null \</code> | Makes a bounded HTTP request with the shown name-resolution, header, output, or failure options. |
| 3 | <code>https://app.realsam.ir/static/app.css</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |

`-D -` writes response headers to stdout and `-o /dev/null` discards the body. A valid conditional request may return `304 Not Modified`.

## Scenario: redirect loop

The TLS terminator sends HTTP to an application. The application sees plaintext and redirects to HTTPS; the proxy repeats the request as HTTP, creating a loop. Evidence:

```bash
curl -IL --max-redirs 10 https://app.realsam.ir/
```

<!-- LINE-BY-LINE AUTO-01_HTTP-04 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>curl -IL --max-redirs 10 https://app.realsam.ir/</code> | Makes a bounded HTTP request with the shown name-resolution, header, output, or failure options. |

Preserve the original scheme through a trusted header, configure the framework's trusted-proxy list, and ensure only the controlled proxy can supply that header. Do not merely disable redirects.

## Scenario: wrong site is returned

Test address, SNI, and Host independently:

```bash
curl -v --resolve app.realsam.ir:443:192.0.2.10 \
  https://app.realsam.ir/
openssl s_client -connect 192.0.2.10:443 \
  -servername app.realsam.ir </dev/null
```

<!-- LINE-BY-LINE AUTO-01_HTTP-05 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>curl -v --resolve app.realsam.ir:443:192.0.2.10 \</code> | Makes a bounded HTTP request with the shown name-resolution, header, output, or failure options. |
| 2 | <code>https://app.realsam.ir/</code> | Executes or defines this step as part of the surrounding example; its effect is bounded by the current context. |
| 3 | <code>openssl s_client -connect 192.0.2.10:443 \</code> | Uses OpenSSL to create or inspect keys, CSRs, certificates, or a TLS connection. |
| 4 | <code>-servername app.realsam.ir &lt;/dev/null</code> | Adds the shown option or argument to the continued command; the trailing backslash continues it when present. |

Wrong DNS, default virtual host, SNI certificate choice, and application tenant selection are separate layers.

## Review

1. Why can query strings expose secrets?
2. Why is POST retry risky?
3. What is the difference between 401 and 403?
4. Which layers can produce an apparent 502?
5. Why is proxy-header trust a security boundary?
