# TLS and Certificate Checklist

<!-- BEGIN BEGINNER FOUNDATION -->
## Beginner foundation

This material starts with purpose, mental model, and safety before commands. Read each example from top to bottom, then use its line-by-line table to explain what every non-empty line changes or verifies.
<!-- END BEGINNER FOUNDATION -->

- [ ] Intended DNS names present in SAN.
- [ ] Leaf dates, issuer, serial, key usage, and algorithm meet policy.
- [ ] Private key matches certificate and has narrow protected access.
- [ ] Full intermediate chain served; root not unnecessarily bundled.
- [ ] Correct certificate selected for every SNI name and edge/replica.
- [ ] Supported protocol policy checked against current vendor guidance.
- [ ] HTTP redirect correct and does not trust arbitrary Host.
- [ ] HSTS staged conservatively; subdomain/preload decision documented.
- [ ] ACME challenge path/DNS API ownership and credentials protected.
- [ ] Renewal timer scheduled and dry-run tested.
- [ ] Deploy hook validates before reload.
- [ ] Live external serial/fingerprint changes after renewal.
- [ ] Expiry monitored from multiple user paths with owner/runbook.
- [ ] Emergency issuance, revocation, key rotation, and rollback tested.
