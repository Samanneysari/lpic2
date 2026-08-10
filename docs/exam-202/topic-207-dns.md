# Topic 207: Domain Name Server

Objectives: 207.1, 207.2, and 207.3

<!-- BEGIN BEGINNER FOUNDATION -->
## Learn the idea before running commands

### What DNS is

The Domain Name System is a distributed database. It translates names such as www.realsam.ir into records such as IPv4 or IPv6 addresses, mail destinations, service locations, and policy text. DNS is hierarchical: the root delegates to top-level domains, a top-level domain delegates to a domain, and that domain may delegate to subdomains.

A **stub resolver** in an application or operating system sends a question to a **recursive resolver**. The recursive resolver checks its cache and, when necessary, follows referrals until it reaches an **authoritative server** for the requested zone. The authoritative server answers from zone data it is responsible for. Recursion and authority are separate roles and should often be separated on public systems.

### Names, zones, and records

A fully qualified domain name ends at the DNS root; zone files show this with a final dot, for example ns1.realsam.ir. A name without the final dot may be made relative to the current $ORIGIN.

A **zone** is the administratively managed part of the namespace served from a zone file or database. It is not necessarily the same as an entire domain tree because a parent can delegate a child zone.

Common records are:

- SOA identifies the zone and its timing metadata.
- NS lists authoritative name servers.
- A and AAAA map names to IPv4 and IPv6 addresses.
- CNAME makes one name an alias of another canonical name.
- MX selects mail exchangers by priority.
- PTR maps an address back to a name in a reverse zone.
- TXT stores text such as email policy.
- SRV advertises a service, protocol, port, priority, and weight.

### Caching and timing

The TTL tells caches how long they may reuse a record. The SOA serial identifies the zone version; increase it after every published change. Refresh, retry, and expire values control secondary-server behavior. Negative caching controls how long a resolver may remember that a name or record does not exist.

### Primary, secondary, and transfer

A primary server holds the editable zone. A secondary obtains a copy through AXFR or IXFR transfer. NOTIFY can tell secondaries that a new version exists. Restrict transfers by address and preferably TSIG. TSIG authenticates DNS messages with a shared secret; it does not encrypt them.

### Safe implementation sequence

1. Decide whether this server is authoritative, recursive, or deliberately both for an isolated lab.
2. Install BIND from the distribution.
3. Restrict listening addresses and recursion before exposing port 53.
4. Declare the zone.
5. Write forward and reverse data.
6. Validate configuration and zones without reloading.
7. Reload.
8. Test directly against each server.
9. Test from trusted and untrusted clients.
10. Inspect logs.

DNSSEC adds origin authentication and integrity to DNS data. It does not hide queries. A correct deployment also needs parent DS records, key management, rollover planning, and validating resolvers.
<!-- END BEGINNER FOUNDATION -->

DNS maps names to data such as addresses, mail servers, and services. An authoritative server owns zones. A recursive resolver searches on behalf of clients. Keep public authoritative service separate from unrestricted recursion.

## 207.1 Basic BIND configuration

Package and paths differ by distribution. RHEL-family systems commonly use /etc/named.conf and /var/named. Debian-family systems commonly use /etc/bind/.

Important tools:

~~~bash
named -v
named-checkconf
named-checkconf -z
rndc status
rndc reload
dig @127.0.0.1 realsam.ir SOA
host www.realsam.ir 127.0.0.1
~~~

<!-- LINE-BY-LINE 1 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>named -v</code> | Runs BIND or prints its installed version. |
| 2 | <code>named-checkconf</code> | Parses BIND configuration and reports syntax or zone-loading errors without starting the service. |
| 3 | <code>named-checkconf -z</code> | Parses BIND configuration and reports syntax or zone-loading errors without starting the service. |
| 4 | <code>rndc status</code> | Sends an authenticated control command to the running BIND server. |
| 5 | <code>rndc reload</code> | Sends an authenticated control command to the running BIND server. |
| 6 | <code>dig @127.0.0.1 realsam.ir SOA</code> | Sends a DNS query and prints the detailed response. |
| 7 | <code>host www.realsam.ir 127.0.0.1</code> | Performs a concise DNS lookup, optionally against a selected server. |

nslookup is an exam term, although dig and host are usually better diagnostic tools.

### Safe role separation

An internal recursive resolver can use:

~~~text
acl trusted_clients {
    127.0.0.1;
    10.20.0.0/24;
    2001:db8:20::/64;
};

options {
    listen-on port 53 { 127.0.0.1; 10.20.0.53; };
    listen-on-v6 port 53 { ::1; 2001:db8:20::53; };
    recursion yes;
    allow-recursion { trusted_clients; };
    allow-query-cache { trusted_clients; };
    forwarders { 192.0.2.53; 198.51.100.53; };
    forward first;
};
~~~

<!-- LINE-BY-LINE 2 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>acl trusted_clients {</code> | Opens a BIND ACL named trusted_clients; the following address prefixes become its members. |
| 2 | <code>127.0.0.1;</code> | Adds this host or network prefix to the surrounding BIND access-control list. |
| 3 | <code>10.20.0.0/24;</code> | Adds this host or network prefix to the surrounding BIND access-control list. |
| 4 | <code>2001:db8:20::/64;</code> | Adds this host or network prefix to the surrounding BIND access-control list. |
| 5 | <code>};</code> | Closes the configuration or multi-line value opened above. |
| 7 | <code>options {</code> | Assigns the shown parameter value whenever modprobe loads this module. |
| 8 | <code>listen-on port 53 { 127.0.0.1; 10.20.0.53; };</code> | Restricts BIND's IPv4 listening addresses and port. |
| 9 | <code>listen-on-v6 port 53 { ::1; 2001:db8:20::53; };</code> | Restricts BIND's IPv6 listening addresses and port. |
| 10 | <code>recursion yes;</code> | Enables or disables recursive DNS resolution. |
| 11 | <code>allow-recursion { trusted_clients; };</code> | Limits which clients may use recursive resolution. |
| 12 | <code>allow-query-cache { trusted_clients; };</code> | Limits which clients may receive cached recursive answers. |
| 13 | <code>forwarders { 192.0.2.53; 198.51.100.53; };</code> | Lists resolvers to which recursive questions are forwarded. |
| 14 | <code>forward first;</code> | Controls whether normal recursion is attempted if forwarding fails. |
| 15 | <code>};</code> | Closes the configuration or multi-line value opened above. |

A public authoritative server should normally disable recursion:

~~~text
options {
    recursion no;
    allow-query { any; };
};
~~~

<!-- LINE-BY-LINE 3 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>options {</code> | Assigns the shown parameter value whenever modprobe loads this module. |
| 2 | <code>recursion no;</code> | Enables or disables recursive DNS resolution. |
| 3 | <code>allow-query { any; };</code> | Controls which clients may query authoritative data. |
| 4 | <code>};</code> | Closes the configuration or multi-line value opened above. |

allow-query controls access to authoritative data. allow-recursion and allow-query-cache protect resolver functions. Do not create an open resolver.

### Logging

~~~text
logging {
    channel security_log {
        file "/var/log/named/security.log" versions 5 size 10m;
        severity info;
        print-time yes;
    };
    category security { security_log; };
};
~~~

<!-- LINE-BY-LINE 4 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>logging {</code> | Opens BIND's logging configuration. |
| 2 | <code>channel security_log {</code> | Opens a named BIND log channel whose destination and format are set by the following lines. |
| 3 | <code>file "/var/log/named/security.log" versions 5 size 10m;</code> | Writes this channel to the selected file, rotates five versions, and caps each file at 10 MB. |
| 4 | <code>severity info;</code> | Sets the minimum log severity written to this BIND channel. |
| 5 | <code>print-time yes;</code> | Adds a timestamp to each log entry. |
| 6 | <code>};</code> | Closes the configuration or multi-line value opened above. |
| 7 | <code>category security { security_log; };</code> | Routes BIND security-category messages to the security_log channel. |
| 8 | <code>};</code> | Closes the configuration or multi-line value opened above. |

Create the directory with correct ownership and security labels. On systemd systems, also use:

~~~bash
journalctl -u named
journalctl -u bind9
~~~

<!-- LINE-BY-LINE 5 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>journalctl -u named</code> | Reads structured systemd journal records with the shown unit or time filter. |
| 2 | <code>journalctl -u bind9</code> | Reads structured systemd journal records with the shown unit or time filter. |

Be aware of dnsmasq, djbdns, and PowerDNS as alternative name servers.

## 207.2 Create and maintain zones

### Primary zone declaration

The objective uses master and slave terminology. This guide uses primary and secondary, with traditional terms in parentheses.

~~~text
zone "realsam.ir" IN {
    type primary;
    file "realsam.ir.zone";
    allow-update { none; };
    allow-transfer { key "realsam-xfr"; };
    also-notify { 198.51.100.53; };
};
~~~

<!-- LINE-BY-LINE 6 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>zone "realsam.ir" IN {</code> | Opens the authoritative zone declaration for realsam.ir in the Internet class. |
| 2 | <code>type primary;</code> | Makes this server the editable primary source for the zone. |
| 3 | <code>file "realsam.ir.zone";</code> | Loads the primary zone data from the named file relative to the distribution's zone directory. |
| 4 | <code>allow-update { none; };</code> | Controls dynamic DNS updates; none disables them. |
| 5 | <code>allow-transfer { key "realsam-xfr"; };</code> | Controls full and incremental zone transfers. |
| 6 | <code>also-notify { 198.51.100.53; };</code> | Adds secondary servers that receive DNS NOTIFY messages. |
| 7 | <code>};</code> | Closes the configuration or multi-line value opened above. |

Older BIND accepts type master. A secondary may use:

~~~text
zone "realsam.ir" IN {
    type secondary;
    file "slaves/realsam.ir.zone";
    primaries { 203.0.113.53 key "realsam-xfr"; };
};
~~~

<!-- LINE-BY-LINE 7 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>zone "realsam.ir" IN {</code> | Opens the authoritative zone declaration for realsam.ir in the Internet class. |
| 2 | <code>type secondary;</code> | Makes this server obtain and serve a transferred copy of the zone. |
| 3 | <code>file "slaves/realsam.ir.zone";</code> | Stores transferred secondary data in the writable slaves directory. |
| 4 | <code>primaries { 203.0.113.53 key "realsam-xfr"; };</code> | Lists primary servers from which a secondary obtains its zone. |
| 5 | <code>};</code> | Closes the configuration or multi-line value opened above. |

Older syntax uses type slave and masters.

### Forward zone file

~~~dns
$ORIGIN realsam.ir.
$TTL 3600

@ IN SOA ns1.realsam.ir. hostmaster.realsam.ir. (
    2026081001 ; serial
    1800       ; refresh
    900        ; retry
    1209600    ; expire
    300        ; negative cache TTL
)

@        IN NS    ns1.realsam.ir.
@        IN NS    ns2.realsam.ir.

ns1      IN A     203.0.113.53
ns2      IN A     198.51.100.53
@        IN A     203.0.113.20
www      IN A     203.0.113.20
www      IN AAAA  2001:db8:20::20
mail     IN A     203.0.113.25
@        IN MX 10 mail.realsam.ir.
proxy    IN A     203.0.113.30
_sip._tcp IN SRV 10 60 5060 sip.realsam.ir.
sip      IN A     203.0.113.40
@        IN TXT   "v=spf1 mx -all"
~~~

<!-- LINE-BY-LINE 8 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>$ORIGIN realsam.ir.</code> | Sets the suffix added to relative names in this DNS zone file. |
| 2 | <code>$TTL 3600</code> | Sets the default DNS cache lifetime in seconds. |
| 4 | <code>@ IN SOA ns1.realsam.ir. hostmaster.realsam.ir. (</code> | Starts the SOA record with the primary server and responsible mailbox; serial and timing values follow. |
| 5 | <code>2026081001 ; serial</code> | Sets the SOA serial; increase it after every published zone change. |
| 6 | <code>1800       ; refresh</code> | Sets how often a secondary checks for a newer zone serial. |
| 7 | <code>900        ; retry</code> | Sets how soon a secondary retries after a failed refresh. |
| 8 | <code>1209600    ; expire</code> | Sets when a secondary stops serving data it can no longer refresh. |
| 9 | <code>300        ; negative cache TTL</code> | Sets how long resolvers may cache a negative answer. |
| 10 | <code>)</code> | Closes the configuration or multi-line value opened above. |
| 12 | <code>@        IN NS    ns1.realsam.ir.</code> | Publishes an authoritative name server for this zone. |
| 13 | <code>@        IN NS    ns2.realsam.ir.</code> | Publishes an authoritative name server for this zone. |
| 15 | <code>ns1      IN A     203.0.113.53</code> | Maps the owner name to the shown IPv4 address. |
| 16 | <code>ns2      IN A     198.51.100.53</code> | Maps the owner name to the shown IPv4 address. |
| 17 | <code>@        IN A     203.0.113.20</code> | Maps the owner name to the shown IPv4 address. |
| 18 | <code>www      IN A     203.0.113.20</code> | Maps the owner name to the shown IPv4 address. |
| 19 | <code>www      IN AAAA  2001:db8:20::20</code> | Maps the owner name to the shown IPv6 address. |
| 20 | <code>mail     IN A     203.0.113.25</code> | Maps the owner name to the shown IPv4 address. |
| 21 | <code>@        IN MX 10 mail.realsam.ir.</code> | Publishes a mail exchanger; lower preference values are tried first. |
| 22 | <code>proxy    IN A     203.0.113.30</code> | Maps the owner name to the shown IPv4 address. |
| 23 | <code>_sip._tcp IN SRV 10 60 5060 sip.realsam.ir.</code> | Publishes a service target with priority, weight, port, and hostname. |
| 24 | <code>sip      IN A     203.0.113.40</code> | Maps the owner name to the shown IPv4 address. |
| 25 | <code>@        IN TXT   "v=spf1 mx -all"</code> | Publishes the shown text value, commonly for policy or verification. |

The second SOA name represents hostmaster@realsam.ir; the first dot replaces the at sign. Increase the serial after every change.

The ns1 and ns2 A records are authoritative data in this child zone. Glue is supplied by the parent zone or registrar when a delegated nameserver is inside the delegated domain.

Validate before reload:

~~~bash
named-checkconf -z
named-checkzone realsam.ir /var/named/realsam.ir.zone
named-compilezone -o /tmp/realsam.ir.raw -f text -F raw realsam.ir /var/named/realsam.ir.zone
sudo rndc reload realsam.ir
~~~

<!-- LINE-BY-LINE 9 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>named-checkconf -z</code> | Parses BIND configuration and reports syntax or zone-loading errors without starting the service. |
| 2 | <code>named-checkzone realsam.ir /var/named/realsam.ir.zone</code> | Validates one zone file against its zone name. |
| 3 | <code>named-compilezone -o /tmp/realsam.ir.raw -f text -F raw realsam.ir /var/named/realsam.ir.zone</code> | Validates a zone and converts it between supported master-file formats. |
| 4 | <code>sudo rndc reload realsam.ir</code> | sudo requests administrator privileges for this operation. Sends an authenticated control command to the running BIND server. |

### Reverse IPv4 zone

For 203.0.113.0/24, the zone is 113.0.203.in-addr.arpa.

~~~dns
$ORIGIN 113.0.203.in-addr.arpa.
$TTL 3600
@ IN SOA ns1.realsam.ir. hostmaster.realsam.ir. (
    2026081001 1800 900 1209600 300
)
@  IN NS  ns1.realsam.ir.
@  IN NS  ns2.realsam.ir.
20 IN PTR www.realsam.ir.
25 IN PTR mail.realsam.ir.
30 IN PTR proxy.realsam.ir.
~~~

<!-- LINE-BY-LINE 10 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>$ORIGIN 113.0.203.in-addr.arpa.</code> | Sets the suffix added to relative names in this DNS zone file. |
| 2 | <code>$TTL 3600</code> | Sets the default DNS cache lifetime in seconds. |
| 3 | <code>@ IN SOA ns1.realsam.ir. hostmaster.realsam.ir. (</code> | Starts the SOA record with the primary server and responsible mailbox; serial and timing values follow. |
| 4 | <code>2026081001 1800 900 1209600 300</code> | Provides the SOA serial, refresh, retry, expire, and negative-cache values in seconds. |
| 5 | <code>)</code> | Closes the configuration or multi-line value opened above. |
| 6 | <code>@  IN NS  ns1.realsam.ir.</code> | Publishes an authoritative name server for this zone. |
| 7 | <code>@  IN NS  ns2.realsam.ir.</code> | Publishes an authoritative name server for this zone. |
| 8 | <code>20 IN PTR www.realsam.ir.</code> | Maps this reverse-zone address label to the shown fully qualified name. |
| 9 | <code>25 IN PTR mail.realsam.ir.</code> | Maps this reverse-zone address label to the shown fully qualified name. |
| 10 | <code>30 IN PTR proxy.realsam.ir.</code> | Maps this reverse-zone address label to the shown fully qualified name. |

IPv6 reverse DNS uses nibble-reversed names under ip6.arpa.

### Delegation and root hints

A parent delegates a child with NS records and, when required, glue. Example inside realsam.ir:

~~~dns
lab       IN NS ns1.lab.realsam.ir.
ns1.lab   IN A  203.0.113.60
~~~

<!-- LINE-BY-LINE 11 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>lab       IN NS ns1.lab.realsam.ir.</code> | Publishes an authoritative name server for this zone. |
| 2 | <code>ns1.lab   IN A  203.0.113.60</code> | Maps the owner name to the shown IPv4 address. |

A caching resolver can use a root-hints file. Update it from an authoritative source and declare it as a hint zone when the distribution does not manage it automatically.

### Query practice

~~~bash
dig realsam.ir SOA
dig realsam.ir NS
dig www.realsam.ir A
dig -x 203.0.113.20
dig +trace www.realsam.ir
dig @ns1.realsam.ir realsam.ir AXFR
~~~

<!-- LINE-BY-LINE 12 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>dig realsam.ir SOA</code> | Sends a DNS query and prints the detailed response. |
| 2 | <code>dig realsam.ir NS</code> | Sends a DNS query and prints the detailed response. |
| 3 | <code>dig www.realsam.ir A</code> | Sends a DNS query and prints the detailed response. |
| 4 | <code>dig -x 203.0.113.20</code> | Sends a DNS query and prints the detailed response. |
| 5 | <code>dig +trace www.realsam.ir</code> | Sends a DNS query and prints the detailed response. |
| 6 | <code>dig @ns1.realsam.ir realsam.ir AXFR</code> | Sends a DNS query and prints the detailed response. |

The AXFR command should fail for unauthorized clients.

## 207.3 Secure DNS

### Run with limited privilege

BIND should drop root privileges after binding low ports. Distribution packages normally supply a dedicated user. Chroot packages or options can isolate filesystem access. A chroot adds containment but does not replace updates, permissions, and access controls.

### TSIG

Generate a shared key on a protected host:

~~~bash
tsig-keygen -a hmac-sha256 realsam-xfr
~~~

<!-- LINE-BY-LINE 13 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>tsig-keygen -a hmac-sha256 realsam-xfr</code> | Generates a TSIG shared secret that must be stored with restrictive permissions. |

Key file:

~~~text
key "realsam-xfr" {
    algorithm hmac-sha256;
    secret "REPLACE_WITH_GENERATED_SECRET";
};
~~~

<!-- LINE-BY-LINE 14 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>key "realsam-xfr" {</code> | Opens the TSIG key definition named realsam-xfr. |
| 2 | <code>algorithm hmac-sha256;</code> | Selects the TSIG authentication algorithm. |
| 3 | <code>secret "REPLACE_WITH_GENERATED_SECRET";</code> | Stores the TSIG shared secret; replace the placeholder and protect the file. |
| 4 | <code>};</code> | Closes the configuration or multi-line value opened above. |

Restrict key permissions and include it from named.conf. Use TSIG to authenticate zone transfers, NOTIFY, or dynamic updates. TSIG provides message authentication, not confidentiality.

### DNSSEC and DANE

DNSSEC signs DNS data so validators can detect modification and forged answers. Important tools include dnssec-keygen and dnssec-signzone. Operational DNSSEC also requires DS data at the parent and careful key rollover.

DANE stores certificate or public-key association information in TLSA records and relies on validated DNSSEC.

### Security checklist

- disable public recursion
- limit transfers with IP and TSIG
- separate authoritative and recursive roles
- run as the packaged unprivileged account
- patch BIND
- restrict control channels and rndc keys
- protect key files
- log denied recursion and transfer attempts
- validate configuration before reload
- test from trusted and untrusted clients

## Exam checklist

/etc/named.conf, /var/named/, rndc, named-checkconf, named-checkzone, named-compilezone, dig, host, nslookup, zone syntax, resource records, masterfile-format, chroot, TSIG, DNSSEC, dnssec-keygen, dnssec-signzone, DANE, dnsmasq, djbdns, and PowerDNS.

## Mini lab

Create an internal resolver and separate authoritative server for realsam.ir. Add forward and reverse zones, configure a secondary, protect transfer with TSIG, confirm unauthorized AXFR fails, and capture all validation commands.
