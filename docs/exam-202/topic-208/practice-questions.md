# Exercises

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

1. Trace a request from recursive DNS through CDN, origin proxy, gateway, and application.
2. Explain SNI, Host, and certificate SAN as separate choices.
3. Why can `nginx -t` pass while a site returns 403?
4. Why can `apachectl configtest` pass while TLS fails?
5. Compare HTTP 401 and 403.
6. Compare 502, 503, and 504 operationally.
7. Why can retrying POST duplicate an action?
8. What does `curl --resolve` isolate?
9. Why can GET still have dangerous side effects in a broken application?
10. Design a safe cache key for public static content.
11. Explain Nginx main, events, http, server, and location contexts.
12. Compare `root` and `alias`.
13. Explain Nginx server-name selection.
14. Why can two `proxy_pass` directives differing only by slash route differently?
15. What happens during graceful Nginx reload?
16. Why can old workers remain?
17. Which Nginx timings separate upstream connect and processing?
18. Diagnose active Nginx with no expected listener.
19. Compare Apache `<Directory>` and `<Location>`.
20. What does `apachectl -S` show?
21. Why prefer central config over broad `.htaccess`?
22. Compare prefork, worker, and event MPMs.
23. Why is `ProxyRequests On` dangerous on an edge?
24. What does `ProxyPassReverse` not rewrite?
25. Define leaf, intermediate, root, key, and CSR.
26. How do you prove a certificate matches a private key without printing the key?
27. Why is an intermediate chain necessary?
28. Compare HTTP-01 and DNS-01 ACME challenges.
29. Why does renewal not prove deployment?
30. Why is `curl -k` not remediation?
31. What risks accompany HSTS `includeSubDomains` and preload?
32. Design live certificate monitoring.
33. Why are forwarding headers untrusted by default?
34. How should a CDN-to-origin client-IP chain be configured?
35. Compare liveness, readiness, and startup checks.
36. Why can a health check cause load?
37. How do you drain a backend with long-lived connections?
38. Why can least-connections still make poor decisions?
39. How can proxy and application retries multiply?
40. Why should queues be bounded?
41. Compare Unix and TCP application sockets.
42. What permissions affect a Unix socket path?
43. Why separate PHP-FPM pools?
44. Why can more PHP workers overload a database?
45. Which layers can limit an upload?
46. Why keep uploads outside executable content?
47. What does SELinux add after Unix permissions?
48. Why is hiding a banner a minor control?
49. How can a status endpoint leak information?
50. What should happen after a secret enters Git?
51. Why is systemd hardening iterative?
52. Which headers should normally not be logged?
53. Define traffic, latency, errors, and saturation for a web service.
54. Why use percentiles rather than only averages?
55. What can increase TLS handshake cost?
56. Why does a localhost benchmark not represent users?
57. How can a cgroup limit hide behind idle host CPU?
58. Design stop conditions for a load test.
59. What does high upstream connect time suggest?
60. What does high upstream header time suggest?
61. Why generate request ID at the edge?
62. What does an external synthetic check cover?
63. Why can monitoring get 200 while users fail?
64. Why can `copytruncate` lose log lines?
65. What makes an alert actionable?
66. Explain A/AAAA, CNAME, TTL, NS, SOA, and PTR in a CDN migration.
67. Why does PTR not send users to a web server?
68. Why must TTL be lowered in advance?
69. Why can DNS/CDN fail only over IPv6?
70. How can historical data reveal an origin IP?
71. Design a four-path comparison for a 502.
72. Why can failed reload leave service online?
73. What evidence should precede a web-server restart?
74. Diagnose disk full when a large log was deleted.
75. When does troubleshooting become incident response?
76. Design a one-node-at-a-time deployment.
77. Why are schema migrations separate from code rollback?
78. What belongs in a web-service backup?
79. Design a certificate-expiry incident handover.
80. Write acceptance criteria for the full capstone.
81. What is the trust-direction difference between a forward proxy and a reverse proxy?
82. Why must a Squid configuration end with a controlled deny rule instead of becoming an open proxy?
83. How do `acl` and `http_access` work together, and why does rule order matter?
84. What risk does `http_access allow all` create on an Internet-reachable Squid server?
85. Why should `CONNECT` normally be limited to approved TLS ports?
86. What should be protected when Squid Basic authentication is used?
87. Which command validates Squid configuration without applying a reload?
88. Name two settings that bound Squid memory, disk, or object resource usage.
89. Which evidence distinguishes a policy denial from a destination or network failure?
90. Design a client test proving that one authorized subnet works while an untrusted subnet is denied.
