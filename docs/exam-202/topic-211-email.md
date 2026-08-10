# Topic 211: Email Services

Objectives: 211.1, 211.2, and 211.3

Email flow commonly uses:

1. MUA: user mail application
2. MTA: server that transfers mail, such as Postfix
3. MDA or LDA: local delivery component
4. IMAP or POP3 server: mailbox access, such as Dovecot

## 211.1 Postfix email server

Main files are normally /etc/postfix/main.cf and /etc/postfix/master.cf.

Safe basic identity:

~~~postfix
myhostname = mail.realsam.ir
mydomain = realsam.ir
myorigin = $mydomain
inet_interfaces = all
inet_protocols = all
mydestination = $myhostname, localhost.$mydomain, localhost, $mydomain
mynetworks = 127.0.0.0/8, [::1]/128, 10.20.0.0/24
relay_domains =
smtpd_relay_restrictions = permit_mynetworks, permit_sasl_authenticated, reject_unauth_destination
~~~

The reject_unauth_destination rule is essential to prevent an open relay. Do not put untrusted networks in mynetworks.

Check effective configuration:

~~~bash
postconf -n
postfix check
sudo systemctl reload postfix
journalctl -u postfix
~~~

### Aliases and virtual domains

/etc/aliases:

~~~text
postmaster: root
security: alice, bob
~~~

~~~bash
sudo newaliases
~~~

Virtual alias map:

~~~text
support@realsam.ir alice
sales@realsam.ir bob
~~~

~~~bash
sudo postmap /etc/postfix/virtual
postmap -q support@realsam.ir hash:/etc/postfix/virtual
~~~

Know canonical maps, virtual_alias_maps, virtual_mailbox_domains, transport maps, and local aliases.

### Queue management

~~~bash
mailq
postqueue -p
postqueue -f
postsuper -d QUEUE_ID
~~~

Inspect before deleting. Queue IDs identify messages. The sendmail compatibility command can submit a test message:

~~~bash
printf "Subject: test\n\nhello\n" | sendmail -v alice@realsam.ir
~~~

### TLS

Postfix needs a certificate, private key, protocol policy, and trusted CA information. Protect the private key. Separate opportunistic SMTP TLS from authenticated message submission policy.

~~~postfix
smtpd_tls_cert_file = /etc/ssl/realsam/mail-fullchain.pem
smtpd_tls_key_file = /etc/ssl/realsam/mail.key
smtpd_tls_security_level = may
smtp_tls_security_level = may
~~~

Use current distribution security defaults for protocols and ciphers.

Monitor logs, queue age, bounces, disk space, and delivery latency. Mailbox quotas may be enforced by the delivery or mailbox system.

## 211.2 Sieve delivery filtering

Sieve filters mail using structured rules. It does not execute arbitrary shell commands.

~~~sieve
require ["fileinto", "reject"];

if header :contains "subject" "[Project]" {
    fileinto "Projects";
    stop;
}

if size :over 10M {
    reject "Message is larger than the accepted limit.";
}
~~~

Important actions and terms:

- keep: retain normal delivery
- fileinto: deliver to a folder
- redirect: send to another address
- reject: refuse with a message
- discard: silently remove
- stop: stop processing rules
- conditions and comparison operators
- Dovecot vacation extension

procmail is an older filtering tool named for awareness.

Validate Sieve with the installed implementation, such as sievec, and enforce permissions on user scripts.

## 211.3 Dovecot mailbox access

Dovecot provides IMAP and POP3. IMAP keeps mail on the server and supports folders. POP3 is simpler and commonly downloads messages.

Configuration is under /etc/dovecot/.

Basic ideas:

~~~dovecot
protocols = imap pop3
mail_location = maildir:~/Maildir

ssl = required
ssl_cert = </etc/ssl/realsam/mail-fullchain.pem
ssl_key = </etc/ssl/realsam/mail.key

disable_plaintext_auth = yes
~~~

Inspect merged configuration:

~~~bash
doveconf -n
sudo doveconf -n
sudo systemctl reload dovecot
journalctl -u dovecot
~~~

Administration:

~~~bash
doveadm who
doveadm mailbox list -u alice
doveadm auth test alice
doveadm search -u alice mailbox INBOX ALL
~~~

Use encrypted IMAP or POP3 and a trusted certificate. Restrict file ownership for mailboxes and keys. Dovecot can provide SASL authentication to Postfix. Be aware of Courier as an alternative IMAP and POP3 implementation.

### Troubleshooting flow

1. Verify DNS MX and A or AAAA records.
2. Confirm ports with ss.
3. Test SMTP dialogue or openssl s_client.
4. Inspect Postfix queue and logs.
5. Confirm mailbox ownership and location.
6. Test Dovecot authentication.
7. Verify TLS name and certificate chain.

~~~bash
dig realsam.ir MX
ss -lntp
openssl s_client -connect mail.realsam.ir:25 -starttls smtp
openssl s_client -connect mail.realsam.ir:993
~~~

## Exam checklist

Postfix configuration, basic SMTP, aliases, quotas, virtual domains, internal relays, monitoring, TLS, Sieve conditions and actions, vacation, procmail awareness, Dovecot configuration, doveconf, doveadm, IMAP, POP3, and Courier awareness.

## Mini lab

Configure Postfix for realsam.ir without open relay, create aliases and one virtual mapping, submit a message, inspect its queue path, create a Sieve rule, then access a Maildir through Dovecot IMAPS.
