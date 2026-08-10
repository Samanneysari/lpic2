# Topic 211: Email Services

Objectives: 211.1, 211.2, and 211.3

<!-- BEGIN BEGINNER FOUNDATION -->
## Learn the idea before running commands

### The parts of an email system

Email delivery uses several roles:

- A **Mail User Agent (MUA)** is the user's client.
- A **Mail Transfer Agent (MTA)** accepts and relays messages with SMTP.
- A **Mail Delivery Agent (MDA)** places a message into a mailbox.
- An IMAP or POP3 server lets a user read stored mail.
- Sieve applies server-side filtering rules during delivery.

Postfix is the main MTA in this objective. Dovecot commonly provides IMAP, POP3, authentication, and local delivery integration. These services can run together but have separate configurations and logs.

### How a message moves

A submitting client usually authenticates on port 587 and sends a message to its MTA. The MTA finds the recipient domain's MX record, connects to the destination MTA on port 25, and transfers the message. The destination applies policy, queues the message, and delivers it to a mailbox. The recipient reads it through IMAP, POP3, or local access.

SMTP is store-and-forward. A temporary failure keeps mail in a queue for retry; a permanent failure creates a bounce. Queue inspection and logs are therefore essential diagnostic evidence.

### Domains, destinations, and relaying

Postfix must distinguish domains it delivers locally from destinations it may relay to. An **open relay** accepts mail from arbitrary senders to arbitrary destinations and will be abused. mynetworks, authentication, recipient restrictions, and TLS policy must be designed carefully.

Aliases redirect local recipient names. Virtual alias or mailbox maps handle hosted domains. Canonical and generic maps rewrite addresses in different directions. Know which map is being queried and run the correct database command after editing a hash map.

### Mailboxes and filtering

Maildir stores each message as a separate file; mbox stores many messages in one file. Permissions and UID consistency matter. Dovecot passdb verifies credentials and userdb supplies mailbox identity and location.

Sieve rules are user-controlled filtering logic. Validate and compile them with the appropriate tools before relying on them.

### Safe implementation sequence

1. Plan hostnames, DNS A/AAAA, MX, reverse DNS, and TLS names.
2. Configure local delivery before Internet relay.
3. Validate Postfix and Dovecot syntax.
4. Test with a lab domain and non-sensitive message.
5. Confirm authentication is protected by TLS.
6. Verify that unauthorized relay is rejected.
7. Inspect the queue and logs.
8. Add SPF, DKIM, and DMARC operationally even though their full deployment is beyond the core objective.

For a public outbound server, verify that the provider-controlled PTR points to the intended mail hostname and that the hostname resolves back to the same address. The ownership model, BIND examples, FCrDNS test, and limitations of rDNS are explained in [Topic 207](topic-207-dns.md#reverse-dns-rdns-and-ptr-records).
<!-- END BEGINNER FOUNDATION -->

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

<!-- LINE-BY-LINE 1 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>myhostname = mail.realsam.ir</code> | Sets Postfix's fully qualified host name to mail.realsam.ir. |
| 2 | <code>mydomain = realsam.ir</code> | Sets the parent mail domain used by other Postfix parameters. |
| 3 | <code>myorigin = $mydomain</code> | Makes locally submitted mail use the configured domain after the @ sign. |
| 4 | <code>inet_interfaces = all</code> | Makes Postfix listen on all configured network interfaces; firewall and relay policy must still restrict use. |
| 5 | <code>inet_protocols = all</code> | Enables both IPv4 and IPv6 support in Postfix. |
| 6 | <code>mydestination = $myhostname, localhost.$mydomain, localhost, $mydomain</code> | Lists domains that Postfix treats as final local destinations. |
| 7 | <code>mynetworks = 127.0.0.0/8, [::1]/128, 10.20.0.0/24</code> | Lists trusted client networks allowed by permit_mynetworks; keep this list narrow. |
| 8 | <code>relay_domains =</code> | Leaves explicit relay domains empty so Postfix does not become a general relay for other domains. |
| 9 | <code>smtpd_relay_restrictions = permit_mynetworks, permit_sasl_authenticated, reject_unauth_destination</code> | Allows trusted or SASL-authenticated clients and rejects mail for unauthorized destinations. |

The reject_unauth_destination rule is essential to prevent an open relay. Do not put untrusted networks in mynetworks.

Check effective configuration:

~~~bash
postconf -n
postfix check
sudo systemctl reload postfix
journalctl -u postfix
~~~

<!-- LINE-BY-LINE 2 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>postconf -n</code> | Displays or changes Postfix parameters and can validate parameter syntax. |
| 2 | <code>postfix check</code> | Checks or controls the Postfix mail system. |
| 3 | <code>sudo systemctl reload postfix</code> | sudo requests administrator privileges for this operation. Inspects or changes systemd units, targets, enablement, or system state. |
| 4 | <code>journalctl -u postfix</code> | Reads structured systemd journal records with the shown unit or time filter. |

### Aliases and virtual domains

/etc/aliases:

~~~text
postmaster: root
security: alice, bob
~~~

<!-- LINE-BY-LINE 3 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>postmaster: root</code> | Creates a required local alias that delivers postmaster mail to root. |
| 2 | <code>security: alice, bob</code> | Expands mail for the local security alias to the listed recipients. |

~~~bash
sudo newaliases
~~~

<!-- LINE-BY-LINE 4 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo newaliases</code> | sudo requests administrator privileges for this operation. Rebuilds the local aliases database after /etc/aliases changes. |

Virtual alias map:

~~~text
support@realsam.ir alice
sales@realsam.ir bob
~~~

<!-- LINE-BY-LINE 5 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>support@realsam.ir alice</code> | Maps the virtual recipient support@realsam.ir to the local user alice. |
| 2 | <code>sales@realsam.ir bob</code> | Maps the virtual recipient sales@realsam.ir to the local user bob. |

~~~bash
sudo postmap /etc/postfix/virtual
postmap -q support@realsam.ir hash:/etc/postfix/virtual
~~~

<!-- LINE-BY-LINE 6 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo postmap /etc/postfix/virtual</code> | sudo requests administrator privileges for this operation. Builds or queries an indexed Postfix lookup table. |
| 2 | <code>postmap -q support@realsam.ir hash:/etc/postfix/virtual</code> | Builds or queries an indexed Postfix lookup table. |

Know canonical maps, virtual_alias_maps, virtual_mailbox_domains, transport maps, and local aliases.

### Queue management

~~~bash
mailq
postqueue -p
postqueue -f
postsuper -d QUEUE_ID
~~~

<!-- LINE-BY-LINE 7 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>mailq</code> | Displays mail waiting in the Postfix queue. |
| 2 | <code>postqueue -p</code> | Lists, flushes, or otherwise controls the Postfix queue. |
| 3 | <code>postqueue -f</code> | Lists, flushes, or otherwise controls the Postfix queue. |
| 4 | <code>postsuper -d QUEUE_ID</code> | Performs privileged queue maintenance on selected message IDs. |

Inspect before deleting. Queue IDs identify messages. The sendmail compatibility command can submit a test message:

~~~bash
printf "Subject: test\n\nhello\n" | sendmail -v alice@realsam.ir
~~~

<!-- LINE-BY-LINE 8 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>printf "Subject: test\n\nhello\n" \| sendmail -v alice@realsam.ir</code> | Writes formatted text; the pipe may feed it to another command. The pipe sends standard output from the command on the left to standard input of the command on the right. |

### TLS

Postfix needs a certificate, private key, protocol policy, and trusted CA information. Protect the private key. Separate opportunistic SMTP TLS from authenticated message submission policy.

~~~postfix
smtpd_tls_cert_file = /etc/ssl/realsam/mail-fullchain.pem
smtpd_tls_key_file = /etc/ssl/realsam/mail.key
smtpd_tls_security_level = may
smtp_tls_security_level = may
~~~

<!-- LINE-BY-LINE 9 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>smtpd_tls_cert_file = /etc/ssl/realsam/mail-fullchain.pem</code> | Points Postfix's inbound SMTP service to the certificate and intermediate chain. |
| 2 | <code>smtpd_tls_key_file = /etc/ssl/realsam/mail.key</code> | Points Postfix's inbound SMTP service to its protected private key. |
| 3 | <code>smtpd_tls_security_level = may</code> | Offers STARTTLS for inbound SMTP while still permitting plaintext delivery for compatibility. |
| 4 | <code>smtp_tls_security_level = may</code> | Attempts TLS for outbound SMTP and falls back when a remote server does not support it. |

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

<!-- LINE-BY-LINE 10 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>require ["fileinto", "reject"];</code> | Declares the Sieve extension needed by this script. |
| 3 | <code>if header :contains "subject" "[Project]" {</code> | Starts a conditional filter that matches the stated message property. |
| 4 | <code>fileinto "Projects";</code> | Delivers matching mail into the named mailbox folder. |
| 5 | <code>stop;</code> | Stops further Sieve rule processing after this rule has handled the message. |
| 6 | <code>}</code> | Closes the configuration or multi-line value opened above. |
| 8 | <code>if size :over 10M {</code> | Starts a conditional filter that matches the stated message property. |
| 9 | <code>reject "Message is larger than the accepted limit.";</code> | Rejects the matching message with the shown explanatory text. |
| 10 | <code>}</code> | Closes the configuration or multi-line value opened above. |

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

<!-- LINE-BY-LINE 11 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>protocols = imap pop3</code> | Enables Dovecot's IMAP and POP3 protocol services. |
| 2 | <code>mail_location = maildir:~/Maildir</code> | Stores each user's mailbox in Maildir format below the user's home directory. |
| 4 | <code>ssl = required</code> | Requires encrypted TLS sessions before normal mailbox access. |
| 5 | <code>ssl_cert = </etc/ssl/realsam/mail-fullchain.pem</code> | Loads Dovecot's certificate and intermediate chain; the leading < tells Dovecot to read the file. |
| 6 | <code>ssl_key = </etc/ssl/realsam/mail.key</code> | Loads Dovecot's protected private key; the leading < tells Dovecot to read the file. |
| 8 | <code>disable_plaintext_auth = yes</code> | Rejects plaintext authentication unless the connection is protected as permitted by Dovecot policy. |

Inspect merged configuration:

~~~bash
doveconf -n
sudo doveconf -n
sudo systemctl reload dovecot
journalctl -u dovecot
~~~

<!-- LINE-BY-LINE 12 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>doveconf -n</code> | Prints and validates Dovecot's effective configuration. |
| 2 | <code>sudo doveconf -n</code> | sudo requests administrator privileges for this operation. Prints and validates Dovecot's effective configuration. |
| 3 | <code>sudo systemctl reload dovecot</code> | sudo requests administrator privileges for this operation. Inspects or changes systemd units, targets, enablement, or system state. |
| 4 | <code>journalctl -u dovecot</code> | Reads structured systemd journal records with the shown unit or time filter. |

Administration:

~~~bash
doveadm who
doveadm mailbox list -u alice
doveadm auth test alice
doveadm search -u alice mailbox INBOX ALL
~~~

<!-- LINE-BY-LINE 13 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>doveadm who</code> | Runs Dovecot administrative and authentication diagnostics. |
| 2 | <code>doveadm mailbox list -u alice</code> | Runs Dovecot administrative and authentication diagnostics. |
| 3 | <code>doveadm auth test alice</code> | Runs Dovecot administrative and authentication diagnostics. |
| 4 | <code>doveadm search -u alice mailbox INBOX ALL</code> | Runs Dovecot administrative and authentication diagnostics. |

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

<!-- LINE-BY-LINE 14 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>dig realsam.ir MX</code> | Sends a DNS query and prints the detailed response. |
| 2 | <code>ss -lntp</code> | Displays listening or connected sockets and summary counters. |
| 3 | <code>openssl s_client -connect mail.realsam.ir:25 -starttls smtp</code> | Creates or inspects keys, CSRs, certificates, and TLS sessions as selected by its subcommand. |
| 4 | <code>openssl s_client -connect mail.realsam.ir:993</code> | Creates or inspects keys, CSRs, certificates, and TLS sessions as selected by its subcommand. |

## Exam checklist

Postfix configuration, basic SMTP, aliases, quotas, virtual domains, internal relays, monitoring, TLS, Sieve conditions and actions, vacation, procmail awareness, Dovecot configuration, doveconf, doveadm, IMAP, POP3, and Courier awareness.

## Mini lab

Configure Postfix for realsam.ir without open relay, create aliases and one virtual mapping, submit a message, inspect its queue path, create a Sieve rule, then access a Maildir through Dovecot IMAPS.
