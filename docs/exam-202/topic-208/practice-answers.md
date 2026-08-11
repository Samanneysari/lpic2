# Answer Key

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

1. Resolver returns edge address; client connects/TLS-authenticates edge; edge applies policy/cache and connects to origin; origin virtual host proxies to gateway/app and dependencies; response returns with correlated metadata.
2. SNI asks the TLS endpoint for a certificate/config, Host selects the HTTP virtual host, and SAN is what the client validates against the requested DNS name.
3. Syntax can be valid while Unix traversal, ACL, SELinux, location selection, or missing files deny runtime access.
4. Parsing does not prove key access, matching key/cert, complete chain, SNI selection, listener/firewall, or client trust.
5. 401 asks for valid authentication and commonly includes a challenge; 403 means the request was understood but authorization refuses it.
6. 502 is an invalid/failed upstream exchange, 503 is unavailable/no healthy capacity, and 504 is an upstream deadline exceeded; inspect the responding layer.
7. The first request may commit while its response is lost; a retry can commit again without an idempotency mechanism.
8. It bypasses DNS for one request while preserving the intended name for Host, SNI, and certificate validation.
9. Protocol intent cannot correct a server that mutates state on GET; test real application behavior.
10. Include normalized scheme/authority/path/query and only required `Vary` dimensions; never cache personalized/authenticated responses without explicit isolation.
11. Main controls global process, events controls connection engine, http controls protocol-wide settings, server selects a virtual host, and location selects URI handling.
12. `root` appends the URI; `alias` replaces the matching location prefix. Slashes and regex captures change results.
13. It first selects listen address/port, then exact/wildcard/regex/default name according to documented precedence.
14. A URI in `proxy_pass` replaces the matched normalized location prefix; no URI generally forwards the original/normalized URI.
15. Master validates/loads new config, starts new workers, and asks old workers to finish existing work.
16. Long-lived, slow, upgraded, or stuck connections keep the old generation alive.
17. `$upstream_connect_time`, `$upstream_header_time`, and `$upstream_response_time`, compared with `$request_time`.
18. Confirm correct unit/config root, effective `listen`, process generation, bind error, address availability, and socket ownership with `ss` and journal.
19. Directory applies to filesystem paths; Location applies to URL space. Their authorization merges can overlap.
20. Listeners, name-based virtual hosts, defaults, aliases, and source configuration locations.
21. Central config avoids per-request directory scans and hidden delegated policy; allow narrow overrides only when required.
22. Prefork uses nonthreaded processes; worker uses threads; event improves keepalive handling. Module compatibility and measured capacity decide.
23. It can let anyone relay traffic, hide abuse, reach internal destinations, and consume bandwidth.
24. It adjusts selected response headers such as redirects; it does not rewrite arbitrary HTML or application-generated body links.
25. Leaf identifies service; intermediate links issuer; root is client trust anchor; private key is secret proof material; CSR requests issuance for a public key/name set.
26. Derive public keys from each and compare cryptographic hashes of the public DER values.
27. Clients may not possess the intermediate; without it they cannot construct a path from leaf to a trusted root.
28. HTTP-01 needs reachable port-80 token path; DNS-01 needs controlled TXT changes and supports wildcards but exposes powerful DNS API credentials.
29. Files may renew while reload hook, replica distribution, permissions, or edge selection remains wrong. Check live serial/fingerprint.
30. It disables authentication and hides the root trust/name/chain/clock problem.
31. Browsers cache the policy and can make every included subdomain unreachable over HTTP; preload removal is slow and operationally difficult.
32. Probe every public edge with correct DNS/SNI/hostname validation, collect live expiry/serial/issuer/chain, alert with lead time, and test renewal/reload.
33. A client can supply them. Trust starts only after a controlled proxy overwrites/appends observations.
34. Restrict origin to CDN paths, configure exact trusted ranges/authenticated links, sanitize inbound headers at edge, and test direct forged requests.
35. Liveness controls restart, readiness controls traffic eligibility, and startup protects slow initialization from premature liveness failure.
36. Expensive dependency checks at high frequency can create traffic, load, locks, and a failure cascade.
37. Mark unready/maintenance, stop new assignment, wait or bound existing sessions, deploy, validate, restore readiness, and observe.
38. Connection count does not equal work cost; long cheap and short expensive requests distort it.
39. Each layer may retry multiple times, multiplying one user request into many backend attempts.
40. Unlimited waiting consumes memory/descriptors and converts overload into long timeout cascades.
41. Unix sockets avoid network exposure and use filesystem policy; TCP sockets cross namespaces/hosts and use address/firewall policy.
42. Parent directory traversal, socket owner/group/mode/ACL, service identities, SELinux labels, and namespace/sandbox visibility.
43. Pools isolate users, sockets, settings, resource capacity, logs, and compromise boundaries per application.
44. More workers issue more concurrent queries and consume memory/CPU, exceeding database pool or dependency capacity.
45. Client, CDN, proxy, server, gateway language runtime, temp filesystem, application, and backend storage/timeouts.
46. A parser/misconfiguration can execute uploaded content; separate roots and deny execution/content sniffing as appropriate.
47. Mandatory policy checks process domain against object type and operation after normal discretionary access checks.
48. Attackers fingerprint behavior by other means; supported patches, minimal modules, isolation, authorization, and monitoring matter more.
49. It can expose versions, upstream names, queue/load, routes, recent errors, and administrative actions.
50. Revoke/rotate it, investigate use, remove it from current/history where policy requires, and fix delivery; deletion alone does not revoke.
51. Each namespace/filesystem/capability restriction can block legitimate reads, writes, bind, reload, or renewal and needs tests/rollback.
52. Authorization, Cookie/Set-Cookie, session/token headers, sensitive query/body data, and personal data unless a governed need exists.
53. Traffic is requests/bytes, latency is operation duration, errors are failed responses/transactions, saturation is queued/exhausted capacity.
54. Averages hide a small but important population of very slow requests.
55. Network RTT/loss, new connections, certificate chain/algorithm, CPU, session reuse, client behavior, and TLS termination layer.
56. It skips normal DNS, network, firewall, edge/CDN, external TLS name/path, and realistic latency/concurrency.
57. Unit CPU quota or memory/pid limit can throttle/fail only that cgroup while global resources appear idle.
58. Define authorized target, gradual concurrency, duration, data, success objective, and abort thresholds for errors, latency, CPU, memory, queues, database, and user impact.
59. Backend accept queue, worker exhaustion, route/firewall loss, connection limit, or port/listener issue.
60. Application/dependency processing before first response header is slow; correlate app traces/logs.
61. Public input can forge/collide or inject logs; a controlled edge establishes consistent correlation, not authentication.
62. DNS, external routing, TCP, SNI/certificate chain/name, redirects/headers, HTTP/application content, and timing.
63. It may use localhost, cached response, IP, shallow endpoint, privileged bypass, different IP family/resolver, or omit content semantics.
64. Copy and truncate race writes, potentially losing or duplicating data; descriptor-aware reopen/rotation is preferable.
65. Site/impact, sustained condition, baseline/current value, evidence links, owner, urgency, safe first checks, and runbook.
66. A/AAAA map names to addresses; CNAME aliases; TTL guides cache lifetime; NS delegates/serves zone; SOA identifies zone/serial/timing; PTR is reverse address mapping.
67. Web clients normally resolve the requested hostname with A/AAAA/CNAME; PTR answers reverse lookups and does not redirect them.
68. Existing cached high-TTL answers must expire before the lower TTL can influence them.
69. AAAA may point to an unconfigured edge/origin, firewall may block IPv6, or listeners/routes/cert path can differ.
70. Old DNS, certificate transparency, email headers, other services/subdomains, scans, shared infrastructure, and archived records.
71. Test app directly, local proxy by name, remote origin by name, then public edge; first failing transition bounds the fault.
72. Graceful reload validates before replacing workers; old workers/config can continue after rejection.
73. Timestamp, impact, processes/generations, sockets, queues, effective config, time-bounded logs, capacity, current connections, and recent changes.
74. Find deleted-open inode with `lsof +L1`, identify writer/unit, safely reopen or restart under change control, verify freed blocks, fix rotation.
75. Unauthorized content/config/account/key/process, evidence of exploitation, data exposure, or loss of host trust requires IR authority and preservation.
76. Drain one node, deploy, validate local/origin/public transaction and metrics, restore readiness, observe, then repeat with rollback trigger.
77. Old code may not understand new schema and down-migration may lose data; version and recovery compatibility are distinct.
78. Config/package manifest, code lineage, TLS/key recovery, DNS/CDN/LB, data/uploads/database/queues, firewall/SELinux/systemd, secrets references, and tested runbook.
79. Include affected names/edges, UTC timeline, live/file serial/dates, renewal/hook status, mitigation, remaining risk, rollback, next checks, owner/time.
80. Two healthy drainable backends, correct DNS/TLS/headers/client identity, secured status, correlated logs, bounded performance, automatic renewal test, backup/isolated restore, and successful seeded-fault reports.
81. A forward proxy acts for controlled clients reaching destinations, while a reverse proxy acts for controlled services receiving client traffic; their allowed users, destinations, and trusted headers are therefore different boundaries.
82. Squid evaluates ordered policy. A final deny prevents unmatched or newly exposed traffic from being relayed through the server.
83. `acl` gives a name to matching conditions; `http_access` allows or denies requests that match those names. Squid evaluates access rules in order, so an earlier broad match can shadow every later rule.
84. Outsiders can hide abusive traffic, reach unintended destinations, consume bandwidth, damage IP reputation, and possibly use the proxy to approach internal services.
85. `CONNECT` creates a TCP tunnel. Limiting destination ports prevents the proxy from becoming a general-purpose tunnel to arbitrary protocols and services.
86. Protect the credential exchange with an appropriate trusted transport or controlled network, protect the password file and helper process, and never expose reusable credentials through logs.
87. `sudo squid -k parse`, using the installed Squid command and configuration path.
88. Valid examples include `cache_mem`, `cache_dir`, `maximum_object_size`, and bounded replacement or storage policy appropriate to the installed version.
89. Inspect the client response, Squid access/cache logs and result code, matched ACL intent, DNS resolution, TCP reachability, and destination response; a policy denial should be explained by the proxy decision rather than guessed from a timeout.
90. Configure one explicit private lab source ACL before the final deny, test an allowed URL from both clients, record the successful and denied access-log entries, and confirm the untrusted client cannot tunnel through `CONNECT` either.
