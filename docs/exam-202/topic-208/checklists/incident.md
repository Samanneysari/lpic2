# Web Incident Checklist

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

- [ ] State affected sites/users, symptom, severity, start/last-good time.
- [ ] Preserve console, existing sessions, configs, logs, process/socket state.
- [ ] Record versions, recent DNS/CDN/deploy/certificate/firewall changes.
- [ ] Test normal DNS and exact returned IPv4/IPv6 addresses.
- [ ] Test route, TCP, TLS SNI/name/chain, HTTP status/content/timing.
- [ ] Compare app-local, proxy-local, remote-origin, and public-edge paths.
- [ ] Inspect listener, unit, process generation, native config, and journal.
- [ ] Correlate request ID across proxy/gateway/application/dependencies.
- [ ] Inspect bytes, inodes, deleted-open files, OOM, and saturation.
- [ ] Check active firewalld zone, SELinux AVCs, path modes/ACLs/labels.
- [ ] Declare hypothesis, prediction, alternative, rollback, and validation.
- [ ] Escalate to security IR for unauthorized changes or compromise signs.
- [ ] Validate real transaction, metrics/logs/renewal/backups after recovery.
- [ ] Record root cause, contributors, monitoring gap, owner, and due date.
