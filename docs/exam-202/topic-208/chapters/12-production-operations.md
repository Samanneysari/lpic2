# 12 — Production Operations

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

## Outcome

Operate deployments, patches, certificate renewal, backups, restores, capacity, handovers, and decommissioning as controlled systems.

## Site inventory

For each site record owners, names/records, VIP/CDN, origin addresses, web/proxy versions, config paths, document/app roots, TLS issuer and expiry, upstreams/dependencies, authentication, data class, logs/metrics, backup RPO/RTO, deployment method, and runbooks.

## Deployment sequence

1. Define version, change, expected result, and rollback artifact.
2. Test configuration/app in an equivalent environment.
3. Confirm backup and independent recovery path.
4. Drain one backend.
5. Deploy immutable/reproducible artifact with root-owned code.
6. Run application migrations under a separate compatible plan.
7. Validate locally, then through proxy/edge.
8. Restore readiness and observe.
9. Continue one backend at a time.
10. Record exact result and remove temporary access.

Symlink releases can provide fast code rollback, but database/schema, cache, upload, and background-job compatibility still govern recoverability.

## Patch sequence

Read advisories and version changes; identify restart/reboot, module/API compatibility, and TLS behavior. Baseline, drain, update one node, validate configuration, restart/reload as required, run synthetic tests, observe, and then roll through the pool.

`dnf history undo` is not a universal application rollback. Keep previous package/artifact and data recovery procedures.

## Certificate lifecycle

Monitor days remaining from the live external endpoint, not only local files. Test automatic renewal with staging/dry-run, hook validation, service reload, file permissions, replicas, and alert path. Keep emergency manual issuance documented without sharing account credentials.

## Backup and restore

Protect:

- effective web/proxy/application configuration and package manifest;
- certificates when policy permits and private keys through protected key recovery;
- application code artifact/lineage;
- uploads/content, databases, and queues with consistency method;
- DNS/CDN/load-balancer configuration exports;
- systemd, firewall, SELinux, and secret references;
- runbooks and monitoring definitions.

Restore to an isolated environment and validate TLS/name handling, permissions/labels, application data, user transaction, background work, logs, and monitoring. A config tarball alone is not a site backup.

## Change handover

```text
Site/environment and UTC window:
Version/change ID:
Nodes drained/deployed:
Validation results:
Error/latency comparison:
Temporary changes and expiry:
Rollback artifact/trigger:
Open risk, owner, due time:
```

<!-- LINE-BY-LINE AUTO-12_PRODUCTION_OPERATIONS-01 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>Site/environment and UTC window:</code> | Sets or records the `Site/environment and UTC window` field in this protocol or report example. |
| 2 | <code>Version/change ID:</code> | Sets or records the `Version/change ID` field in this protocol or report example. |
| 3 | <code>Nodes drained/deployed:</code> | Sets or records the `Nodes drained/deployed` field in this protocol or report example. |
| 4 | <code>Validation results:</code> | Sets or records the `Validation results` field in this protocol or report example. |
| 5 | <code>Error/latency comparison:</code> | Sets or records the `Error/latency comparison` field in this protocol or report example. |
| 6 | <code>Temporary changes and expiry:</code> | Sets or records the `Temporary changes and expiry` field in this protocol or report example. |
| 7 | <code>Rollback artifact/trigger:</code> | Sets or records the `Rollback artifact/trigger` field in this protocol or report example. |
| 8 | <code>Open risk, owner, due time:</code> | Sets or records the `Open risk, owner, due time` field in this protocol or report example. |

## Decommission

Confirm owner and retention; remove traffic from load balancer/CDN; reduce DNS only after consumers migrate; revoke certificates/keys/tokens; remove origin firewall access; archive or destroy data per policy; remove monitoring/backups/inventory; and watch old names for unexpected traffic.

## Capstone

Deploy two backends behind HAProxy or Nginx, TLS at the edge, static and application routes, request-ID logs, safe client-IP policy, metrics restricted to management, automated certificate-renewal test, and a tested isolated restore. Then resolve seeded backend, DNS, certificate, permission, timeout, and disk incidents.

## Review

1. Why deploy one backend at a time?
2. Why are database migrations a separate rollback concern?
3. Which live endpoint should certificate monitoring test?
4. What belongs in a recoverable site backup?
5. Why monitor an old name after decommissioning?
