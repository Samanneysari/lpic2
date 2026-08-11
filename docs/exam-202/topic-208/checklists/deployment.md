# Web Deployment Checklist

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

- [ ] Site/environment, owner, UTC window, version, impact, and approval recorded.
- [ ] DNS/CDN/load-balancer path and active backends mapped.
- [ ] Previous artifact/config and data rollback verified.
- [ ] Backup and restore evidence within policy.
- [ ] Native web/proxy/app validators pass.
- [ ] One backend drained; long-lived connections handled.
- [ ] Code/config owner, mode, ACL, SELinux, and secret references correct.
- [ ] Local application check passes.
- [ ] Origin virtual-host check with intended Host/SNI passes.
- [ ] Public DNS/CDN/TLS/application transaction passes.
- [ ] Status, latency, upstream timing, errors, saturation, and logs observed.
- [ ] Backend restored to readiness before moving to next.
- [ ] Monitoring, backup, certificate renewal, and log pipeline remain healthy.
- [ ] Temporary access/config removed or assigned expiry.
- [ ] Change record contains validation, rollback trigger, and final state.
