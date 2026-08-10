# Topic 207: Domain Name Server

Objectives: 207.1, 207.2, and 207.3

<!-- BEGIN BEGINNER FOUNDATION -->
## Learn the idea before running commands

### What DNS is

The Domain Name System is a distributed database. It translates names such as www.realsam.ir into records such as IPv4 or IPv6 addresses, mail destinations, service locations, and policy text. DNS is hierarchical: the root delegates to top-level domains, a top-level domain delegates to a domain, and that domain may delegate to subdomains.

A **stub resolver** in an application or operating system sends a question to a **recursive resolver**. The recursive resolver checks its cache and, when necessary, follows referrals until it reaches an **authoritative server** for the requested zone. The authoritative server answers from zone data it is responsible for. Recursion and authority are separate roles and should often be separated on public systems.

### DNS hierarchy and delegated structure

DNS is one tree read from right to left. The invisible top of that tree is the root, written as a final dot. The hierarchy for <code>www.realsam.ir.</code> is:

| Level | Example | Responsibility |
|---|---|---|
| Root | <code>.</code> | Refers resolvers to the authoritative servers for top-level domains. |
| Top-level domain | <code>ir.</code> | Refers resolvers to the authoritative servers registered for <code>realsam.ir.</code>. |
| Registered domain | <code>realsam.ir.</code> | Contains or delegates the authoritative data for the domain. |
| Host or owner name | <code>www.realsam.ir.</code> | Owns an RRset such as A or AAAA. |
| Delegated child zone | <code>lab.realsam.ir.</code> | Can have different authoritative servers and its own SOA. |

The registrar records which name servers are authoritative for the registered domain. The registry publishes that delegation in the parent zone. The parent does not normally store the web server's A record; it stores the child NS delegation and any necessary glue addresses.

A **domain** is any node and everything below it in the namespace. A **zone** is the part currently managed by one authority. They are not always equal. If <code>lab.realsam.ir</code> is delegated, it remains inside the <code>realsam.ir</code> domain tree but becomes a separate zone.

### From a URL to a rendered page: the complete path

Assume a user enters <code>https://www.realsam.ir/docs/start</code> in a browser:

1. The browser parses the scheme (<code>https</code>), hostname (<code>www.realsam.ir</code>), default port (443), and path (<code>/docs/start</code>).
2. The browser checks relevant browser caches and connection state. The operating system may also have cached name data.
3. The application asks the operating system to resolve the hostname, normally through a function such as <code>getaddrinfo()</code>. On Linux, NSS policy in <code>/etc/nsswitch.conf</code> decides whether sources such as <code>/etc/hosts</code>, DNS, or another identity service are consulted and in what order.
4. If a local source does not already answer, the stub resolver sends A and AAAA questions to its configured recursive resolver. That resolver may come from DHCP, NetworkManager, systemd-resolved, or static <code>/etc/resolv.conf</code> configuration.
5. The recursive resolver checks positive and negative caches. A valid cached answer can finish DNS resolution without contacting authoritative servers.
6. On a cache miss, the resolver asks a root server. The root does not return the web address; it returns a referral to authoritative servers for <code>ir.</code>.
7. The resolver asks an <code>ir.</code> server. It receives the NS delegation for <code>realsam.ir.</code> and, when needed, glue addresses that make those name servers reachable.
8. The resolver asks an authoritative server for <code>www.realsam.ir.</code>. It receives the A/AAAA RRset, follows a CNAME chain if one is present, or receives a negative response.
9. A validating resolver checks DNSSEC signatures when the delegation is signed. It caches the result according to TTL and returns it to the client.
10. The client selects an address. Modern clients may race IPv6 and IPv4 attempts instead of waiting for one family to fail completely.
11. Routing chooses the next hop. On the local link, ARP for IPv4 or Neighbor Discovery for IPv6 finds the next-hop link-layer address.
12. For HTTP/1.1 or HTTP/2, the client normally establishes TCP; for HTTP/3 it normally uses QUIC over UDP. DNS has supplied an address, not the application connection.
13. TLS negotiates encryption. The client sends the intended hostname through SNI, verifies that the certificate chain is trusted, and checks that a SAN matches <code>www.realsam.ir</code>.
14. The browser sends an HTTP request containing the path and a Host or <code>:authority</code> value. A web server or reverse proxy uses that name to select the correct virtual host.
15. The server applies routing, authentication, and application logic, then returns a status code, headers, and body.
16. The browser validates and decodes the response, renders it, and repeats the process for required scripts, stylesheets, images, APIs, and other origins.

DNS work normally ends at step 9. A successful <code>dig</code> result therefore does not prove that routing, port 443, TLS, the virtual host, or the application works.

A response can be **NXDOMAIN**, meaning the queried name does not exist, or **NODATA**, meaning the name exists but has no record of the requested type. These have different troubleshooting meanings.

Use different tools to observe different layers:

~~~bash
getent ahosts www.realsam.ir
resolvectl query www.realsam.ir
dig +trace www.realsam.ir A
openssl s_client -connect www.realsam.ir:443 -servername www.realsam.ir
curl --verbose https://www.realsam.ir/
~~~

<!-- LINE-BY-LINE DNS-FLOW -->
**Line-by-line explanation**

| Line | Command | What it proves |
|---:|---|---|
| 1 | <code>getent ahosts www.realsam.ir</code> | Uses the system's NSS path, so it reflects sources such as files and DNS rather than forcing a DNS-only lookup. |
| 2 | <code>resolvectl query www.realsam.ir</code> | Asks systemd-resolved and shows its selected interface, protocol, records, and validation state when that service is in use. |
| 3 | <code>dig +trace www.realsam.ir A</code> | Starts from root referrals and displays the delegation path toward the authoritative A answer; it does not reproduce browser, NSS, or recursive-cache behavior. |
| 4 | <code>openssl s_client -connect www.realsam.ir:443 -servername www.realsam.ir</code> | Opens a TLS connection with SNI so the certificate chain and negotiated TLS details can be inspected. |
| 5 | <code>curl --verbose https://www.realsam.ir/</code> | Shows name lookup, address connection, TLS, HTTP request headers, and the received HTTP response at a client level. |

### DNS messages, transport, and answer sections

Classic DNS uses port 53. Queries commonly begin over UDP; TCP is used for zone transfers and whenever a response or policy requires it. EDNS extends DNS capabilities and permits larger UDP messages. A truncated UDP response sets the TC flag so a client can retry over TCP.

A DNS reply can contain:

| Section | Meaning |
|---|---|
| Question | The owner name, class, and type being requested. |
| Answer | Records that directly answer the question, including a CNAME chain when applicable. |
| Authority | Authoritative NS data, an SOA for a negative answer, or a delegation referral. |
| Additional | Helpful related data such as glue A/AAAA records. |

Important flags include RD (recursion desired), RA (recursion available), AA (authoritative answer), TC (truncated), and AD (the recursive resolver reports DNSSEC-authenticated data). An AD flag is meaningful only when the client trusts that resolver and the path to it.

Encrypted DNS transports such as DNS over TLS and DNS over HTTPS protect the client-to-resolver channel. They do not make unsigned authoritative data authentic; DNSSEC addresses data origin and integrity, not query confidentiality.

### Names, zones, resource records, and RRsets

A fully qualified domain name (FQDN) reaches the DNS root. Zone files show this with a final dot, for example <code>ns1.realsam.ir.</code>. A name without the final dot is relative and may have the current <code>$ORIGIN</code> appended.

A **resource record** has this logical form:

| Field | Meaning | Example |
|---|---|---|
| Owner | The name that owns the data | <code>www</code> or <code>www.realsam.ir.</code> |
| TTL | How many seconds a cache may normally reuse the data | <code>3600</code> |
| Class | The protocol family; Internet DNS normally uses IN | <code>IN</code> |
| Type | The structure and purpose of the record | <code>A</code> |
| RDATA | Type-specific value | <code>203.0.113.20</code> |

Records with the same owner, class, and type form an **RRset**. Authoritative servers return the RRset as a unit. <code>$ORIGIN</code> and <code>$TTL</code> are zone-file directives, not DNS record types. The <code>@</code> owner means the current origin, commonly the zone apex.

### Common DNS record types

DNS is extensible and has more registered types than an LPIC-2 administrator normally memorizes. The following table covers the exam-relevant and commonly operated records:

| Type | Meaning and use | Example and important rule |
|---|---|---|
| SOA | Start of Authority. Marks the zone and stores its primary server, responsible mailbox, serial, refresh, retry, expire, and negative-cache timing. | Every normal zone has one SOA RRset at its apex. Increase the serial after a published change. |
| NS | Names an authoritative server for a zone or delegates a child zone. | <code>realsam.ir. IN NS ns1.realsam.ir.</code> The target must be a hostname, not an IP address. |
| A | Maps an owner name to one IPv4 address. | <code>www IN A 203.0.113.20</code>. Several A records at one owner form one RRset. |
| AAAA | Maps an owner name to one IPv6 address. | <code>www IN AAAA 2001:db8:20::20</code>. The four letters do not mean four addresses. |
| CNAME | States that one owner name is an alias of another canonical name. | <code>portal IN CNAME www.realsam.ir.</code>. The target is a hostname. A CNAME owner normally cannot have other data, and a zone apex needs SOA/NS so it normally cannot be a CNAME. |
| MX | Selects mail exchangers for a domain. Lower preference values are tried first. | <code>@ IN MX 10 mail.realsam.ir.</code>. The target must resolve through A/AAAA and must not be a CNAME. |
| PTR | Points a reverse-DNS owner name to a hostname. It is the normal IP-to-name mapping record. | <code>25 IN PTR mail.realsam.ir.</code> inside the appropriate reverse zone. Creating an A record does not create a PTR automatically. |
| TXT | Stores one or more character strings used by applications and verification policies. | SPF, DKIM public keys, DMARC policy, and ownership verification commonly use TXT. TXT itself does not define one universal meaning. |
| SRV | Locates a named service and protocol using priority, weight, port, and target. | <code>_sip._tcp IN SRV 10 60 5060 sip.realsam.ir.</code>. Lower priority wins; weight distributes equal-priority choices. |
| CAA | States which certificate authorities may issue certificates for a name and can provide an incident-report contact. | <code>@ IN CAA 0 issue "letsencrypt.org"</code>. It is issuance policy, not a certificate. |
| DS | Publishes a child zone's DNSSEC delegation signer data in the parent zone. | It connects the parent's chain of trust to the child's DNSKEY. |
| DNSKEY | Publishes a DNSSEC public key for a zone. | Private key material is not published in DNS. |
| RRSIG | Contains a DNSSEC signature over an RRset. | Validators use DNSKEY and the chain of trust to verify it. |
| NSEC / NSEC3 | Provides authenticated denial of existence for DNSSEC. | It proves that a requested name or type is absent; NSEC3 uses hashed owner names. |
| TLSA | Associates TLS certificate or public-key information with a service endpoint for DANE. | DANE depends on DNSSEC validation. |
| SSHFP | Publishes SSH host-key fingerprints. | A client needs a trustworthy validation policy; an unsigned SSHFP answer is not sufficient proof. |
| NAPTR | Applies ordered rewriting rules, often together with SRV for service discovery. | It is used by selected protocols rather than ordinary web address mapping. |
| SVCB / HTTPS | Publishes modern service-binding information and connection hints. | These newer operational records are useful awareness items but are not a replacement for understanding A/AAAA, CNAME, and normal delegation. |

### SOA fields in plain English

The SOA RDATA fields are easy to confuse:

| Field | Purpose |
|---|---|
| MNAME | The primary authoritative server named by the zone metadata. |
| RNAME | The responsible mailbox with the first unescaped dot representing <code>@</code>. |
| Serial | Zone version compared by secondaries; it must increase. |
| Refresh | How soon a secondary normally checks for a newer serial. |
| Retry | How soon it retries after a failed refresh. |
| Expire | When a secondary stops serving a copy it can no longer refresh. |
| Minimum / negative TTL | Used with the SOA TTL to determine negative-cache lifetime under modern DNS rules. |

The SOA refresh, retry, and expire timers control secondary behavior. They do not set the normal TTL for every A or MX record.

### Record relationships and common mistakes

- A/AAAA are forward mappings; PTR is a separate reverse mapping under different administrative authority.
- NS and MX targets must be hostnames with address records, not raw IP addresses and not CNAME aliases.
- A CNAME redirects one owner name. It does not redirect URLs, paths, ports, or HTTP requests.
- Several TXT strings at one owner may belong to different applications. Preserve their exact quoting and length rules.
- Glue is an address supplied by a parent to break the circular dependency created when an in-bailiwick delegated name server is inside the child it serves.
- A low TTL speeds cache turnover but increases query traffic. Raising a TTL after a stable migration improves cache efficiency.
- A wildcard answers only when a closer matching name does not exist; it is not a search-and-replace rule and does not automatically cover every deeper label.

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
| 1 | <code>named -v</code> | Prints the installed BIND <code>named</code> version and exits. |
| 2 | <code>named-checkconf</code> | Parses <code>named.conf</code> and included configuration files without starting or reloading BIND; it does not load every primary zone file unless requested. |
| 3 | <code>named-checkconf -z</code> | Parses the configuration and test-loads all configured primary zones so zone-file errors are also reported. |
| 4 | <code>rndc status</code> | Authenticates to the BIND control channel and reports status from the running server. |
| 5 | <code>rndc reload</code> | Authenticates to the control channel and asks the running server to reload configuration and changed zones. |
| 6 | <code>dig @127.0.0.1 realsam.ir SOA</code> | Queries the local DNS server directly for the zone's SOA record and prints flags, sections, timing, and responding server. |
| 7 | <code>host www.realsam.ir 127.0.0.1</code> | Asks the local DNS server for a concise address result for the web hostname. |

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
| 7 | <code>options {</code> | Opens BIND's global server-options block. |
| 8 | <code>listen-on port 53 { 127.0.0.1; 10.20.0.53; };</code> | Restricts BIND's IPv4 listening addresses and port. |
| 9 | <code>listen-on-v6 port 53 { ::1; 2001:db8:20::53; };</code> | Restricts BIND's IPv6 listening addresses and port. |
| 10 | <code>recursion yes;</code> | Enables recursive resolution, subject to the following client ACLs. |
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
| 1 | <code>options {</code> | Opens BIND's global server-options block. |
| 2 | <code>recursion no;</code> | Prevents this public authoritative server from performing recursive lookups for clients. |
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
| 4 | <code>sudo rndc reload realsam.ir</code> | Requests administrator privilege and tells the running BIND server to reload only the forward zone after validation succeeds. |

### Reverse DNS (rDNS) and PTR records

#### What reverse DNS is

Normal or **forward DNS** starts with a name and asks for data, commonly an address:

<code>mail.realsam.ir. → A → 203.0.113.25</code>

**Reverse DNS**, commonly shortened to **rDNS**, starts with an IP address and asks for a name:

<code>203.0.113.25 → PTR → mail.realsam.ir.</code>

DNS does not search all A records to reverse an address. It transforms the address into a special owner name and queries a PTR record in a separate reverse namespace:

- IPv4 uses <code>in-addr.arpa.</code>.
- IPv6 uses <code>ip6.arpa.</code>.

A PTR record is a DNS pointer record. In ordinary rDNS it maps the constructed reverse owner to an FQDN. The PTR target should end with a dot in a zone file so it is not accidentally made relative to the reverse zone.

#### Who controls rDNS

Owning <code>realsam.ir</code> does not automatically give control over the reverse zone for an IP address. Forward authority follows the domain delegation; reverse authority follows the IP-address allocation.

For a public address, the ISP, cloud provider, hosting company, or address-block holder normally controls the parent reverse zone. A customer usually does one of these:

1. Sets the PTR value in the provider's control panel or API.
2. Opens a support request asking the provider to set it.
3. Receives a formal delegation of a reverse zone and serves that delegated zone.

Adding <code>203.0.113.25 IN PTR ...</code> to the forward <code>realsam.ir</code> zone has no effect. A PTR must be published at the correct reversed owner under <code>in-addr.arpa</code> or <code>ip6.arpa</code> by a server that is authoritative through the reverse delegation.

The public ranges used in this guide are documentation ranges. They cannot be delegated for a real Internet service. Use them in an isolated lab; use a real provider-assigned address and that provider's rDNS procedure in production.

#### How an IPv4 address becomes a PTR query

For <code>203.0.113.25</code>:

1. Reverse the four octets: <code>25.113.0.203</code>.
2. Append <code>in-addr.arpa.</code>.
3. Query <code>25.113.0.203.in-addr.arpa. PTR</code>.
4. The authoritative reverse zone for the example /24 is <code>113.0.203.in-addr.arpa.</code>.
5. Inside that zone, the owner label <code>25</code> completes the full reverse name.

This byte reversal follows the DNS hierarchy: the broader address authority is on the right, and the individual address label is on the left.

#### Declare the reverse IPv4 zone in BIND

The primary BIND server needs a zone declaration in addition to the reverse zone file:

~~~text
zone "113.0.203.in-addr.arpa" IN {
    type primary;
    file "113.0.203.rev";
    allow-update { none; };
    allow-transfer { key "realsam-xfr"; };
};
~~~

<!-- LINE-BY-LINE RDNS-ZONE-DECLARATION -->
**Line-by-line explanation**

| Line | Configuration | What it does |
|---:|---|---|
| 1 | <code>zone "113.0.203.in-addr.arpa" IN {</code> | Opens the Internet-class reverse zone that represents the documentation network 203.0.113.0/24. |
| 2 | <code>type primary;</code> | Makes this server the editable source of the reverse zone. |
| 3 | <code>file "113.0.203.rev";</code> | Loads the reverse records from this file relative to the distribution's configured zone directory. |
| 4 | <code>allow-update { none; };</code> | Disables unauthenticated dynamic changes to the reverse zone. |
| 5 | <code>allow-transfer { key "realsam-xfr"; };</code> | Allows transfer only when the request is authenticated with the configured TSIG key. |
| 6 | <code>};</code> | Ends the reverse-zone declaration. |

The matching zone file is:

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

<!-- LINE-BY-LINE RDNS-IPV4-FILE -->
**Line-by-line explanation**

| Line | Configuration | What it does |
|---:|---|---|
| 1 | <code>$ORIGIN 113.0.203.in-addr.arpa.</code> | Makes relative owners part of the reverse zone for 203.0.113.0/24. |
| 2 | <code>$TTL 3600</code> | Gives records a default cache lifetime of one hour. |
| 3 | <code>@ IN SOA ns1.realsam.ir. hostmaster.realsam.ir. (</code> | Begins the reverse zone's authority metadata and names its primary server and contact mailbox. |
| 4 | <code>2026081001 1800 900 1209600 300</code> | Sets serial, refresh, retry, expire, and negative-cache values. |
| 5 | <code>)</code> | Ends the multi-line SOA record. |
| 6 | <code>@ IN NS ns1.realsam.ir.</code> | Publishes the first authoritative server for this reverse zone. |
| 7 | <code>@ IN NS ns2.realsam.ir.</code> | Publishes the second authoritative server for this reverse zone. |
| 8 | <code>20 IN PTR www.realsam.ir.</code> | Makes 203.0.113.20 reverse to the web hostname. |
| 9 | <code>25 IN PTR mail.realsam.ir.</code> | Makes 203.0.113.25 reverse to the mail hostname. |
| 10 | <code>30 IN PTR proxy.realsam.ir.</code> | Makes 203.0.113.30 reverse to the proxy hostname. |

Validate and reload the reverse zone exactly as a forward zone:

~~~bash
named-checkconf -z
named-checkzone 113.0.203.in-addr.arpa /var/named/113.0.203.rev
sudo rndc reload 113.0.203.in-addr.arpa
~~~

<!-- LINE-BY-LINE RDNS-VALIDATE -->
**Line-by-line explanation**

| Line | Command | What it does |
|---:|---|---|
| 1 | <code>named-checkconf -z</code> | Parses BIND configuration and attempts to load every primary zone, including the new reverse zone. |
| 2 | <code>named-checkzone 113.0.203.in-addr.arpa /var/named/113.0.203.rev</code> | Validates the reverse file against the exact zone name it must serve. |
| 3 | <code>sudo rndc reload 113.0.203.in-addr.arpa</code> | Requests administrator privilege and asks the running server to reload only this reverse zone. |

#### Forward-confirmed reverse DNS

A useful operational consistency test is forward-confirmed reverse DNS (FCrDNS):

1. Query the PTR for <code>203.0.113.25</code>; it returns <code>mail.realsam.ir.</code>.
2. Query A and AAAA for <code>mail.realsam.ir.</code>.
3. Confirm that one returned address is the original <code>203.0.113.25</code>.

This does not make the host trusted and is not a replacement for application authentication. It shows that forward and reverse administrators published a consistent relationship.

Technically an address can have more than one PTR value, but multiple names create ambiguous logging and verification behavior. A public server, especially an outbound mail server, should normally have one stable, meaningful PTR hostname and a matching forward address.

#### Why mail systems care about PTR

Receiving mail systems commonly treat rDNS as one anti-abuse and reputation signal. A sensible outbound mail identity has:

- <code>mail.realsam.ir. A 203.0.113.25</code>
- <code>25.113.0.203.in-addr.arpa. PTR mail.realsam.ir.</code>
- an SMTP banner and EHLO/HELO name such as <code>mail.realsam.ir</code>
- an MX target that is a real hostname with A/AAAA records
- separate SPF, DKIM, and DMARC policy where appropriate

PTR alone does not authorize mail, encrypt SMTP, or prove message identity. Missing or inconsistent rDNS can nevertheless contribute to rejection or poor reputation because many receivers apply local policy checks.

rDNS is also useful for readable logs, inventory, diagnostics, and some access policies. Do not treat a PTR answer as strong authentication; names can be misleading, cached, or controlled by another administrative party.

#### Query and verify rDNS

~~~bash
dig mail.realsam.ir A
dig -x 203.0.113.25
dig 25.113.0.203.in-addr.arpa PTR
dig @ns1.realsam.ir 25.113.0.203.in-addr.arpa PTR +norecurse
host 203.0.113.25
~~~

<!-- LINE-BY-LINE RDNS-QUERY -->
**Line-by-line explanation**

| Line | Command | What it verifies |
|---:|---|---|
| 1 | <code>dig mail.realsam.ir A</code> | Checks the forward IPv4 mapping used to confirm the PTR target. |
| 2 | <code>dig -x 203.0.113.25</code> | Constructs the reverse owner automatically and asks the configured resolver for PTR data. |
| 3 | <code>dig 25.113.0.203.in-addr.arpa PTR</code> | Sends the same PTR question with the transformed owner written explicitly. |
| 4 | <code>dig @ns1.realsam.ir 25.113.0.203.in-addr.arpa PTR +norecurse</code> | Queries the selected server directly without requesting recursion; a valid public answer should be authoritative if that server is delegated for the reverse zone. |
| 5 | <code>host 203.0.113.25</code> | Performs a concise reverse lookup suitable for a quick human-readable check. |

When the direct authoritative answer is correct but the normal recursive answer is old, inspect TTL and caches. When the direct server is not authoritative, inspect the parent reverse delegation instead of repeatedly editing the local file.

#### IPv6 reverse DNS

IPv6 rDNS uses every hexadecimal nibble of the fully expanded 128-bit address in reverse order under <code>ip6.arpa.</code>. For example, first expand <code>2001:db8:20::25</code> to:

<code>2001:0db8:0020:0000:0000:0000:0000:0025</code>

Then reverse each hexadecimal digit and insert dots:

<code>5.2.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.2.0.0.8.b.d.0.1.0.0.2.ip6.arpa.</code>

Use <code>dig -x 2001:db8:20::25</code> to construct this safely. In real deployments, the address provider must delegate the appropriate nibble-boundary reverse prefix or publish the requested PTR.

#### Prefixes smaller than an IPv4 /24

Octet-reversed IPv4 zones naturally delegate on /8, /16, and /24 boundaries. A customer receiving a smaller range such as /28 cannot independently create a normal child at an octet boundary. RFC 2317 describes classless reverse delegation: the parent reverse zone publishes CNAME records for individual address labels toward a specially named child zone delegated to the customer.

The address provider must participate. Creating an RFC 2317-style child zone locally without the parent's NS and CNAME delegation does not make it reachable from public DNS.

#### Internal addresses, NAT, and split DNS

An organization can serve reverse zones for RFC 1918 addresses to internal clients, such as <code>20.10.in-addr.arpa</code> for parts of 10.20.0.0/16. Keep these private views away from public leakage.

With NAT, public observers see the public source address. Its PTR describes the public address, not every private host behind it. Internal and external rDNS may therefore be different and can be delivered through separate DNS views.

#### rDNS troubleshooting table

| Symptom | Likely layer | Useful check |
|---|---|---|
| Forward A works, but <code>dig -x</code> returns NXDOMAIN | PTR is absent or the reverse owner is wrong | Query the exact reversed owner and identify the authoritative reverse servers. |
| Local server answers, but public resolvers do not | Missing or incorrect parent reverse delegation | Query parent NS data and contact the IP provider. |
| PTR returns a name whose A/AAAA does not return the original IP | Forward and reverse data are inconsistent | Correct the forward record or ask the address holder to correct PTR. |
| Old PTR remains visible | Resolver cache or unchanged zone serial | Query the authoritative server directly, compare SOA serials, and wait for TTL. |
| BIND returns SERVFAIL | Zone load error, DNSSEC failure, or unreachable authority | Run <code>named-checkconf -z</code>, <code>named-checkzone</code>, and inspect logs. |
| BIND returns REFUSED | The server received the query but policy denied it | Inspect <code>allow-query</code>, views, and recursion policy. |
| Mail is rejected despite matching PTR | rDNS is only one reputation signal | Check SMTP identity, SPF, DKIM, DMARC, blocklists, message behavior, and receiver logs. |

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
| 1 | <code>dig realsam.ir SOA</code> | Requests authority metadata and exposes the serial and secondary timing values. |
| 2 | <code>dig realsam.ir NS</code> | Requests the authoritative name-server RRset published for the zone. |
| 3 | <code>dig www.realsam.ir A</code> | Requests the web hostname's IPv4 RRset through the configured recursive resolver. |
| 4 | <code>dig -x 203.0.113.20</code> | Reverses the IPv4 octets, builds the <code>in-addr.arpa</code> owner, and requests its PTR RRset. |
| 5 | <code>dig +trace www.realsam.ir</code> | Performs iterative queries from the root through referrals to show the delegation path and final authoritative data. |
| 6 | <code>dig @ns1.realsam.ir realsam.ir AXFR</code> | Requests a full zone transfer directly from the named server; the request should be refused unless the client is authorized. |

The AXFR command should fail for unauthorized clients.

### Read dig results instead of looking only for an IP

Important response status values include:

| Status | Meaning | First investigation |
|---|---|---|
| NOERROR with answers | The query succeeded and returned the requested data. | Check owner, type, TTL, flags, and responding server. |
| NOERROR with an empty Answer section | The name exists, but this type is absent (NODATA). | Inspect the Authority SOA and query other expected types. |
| NXDOMAIN | The authoritative DNS says the queried name does not exist. | Check spelling, origin, delegation, wildcard expectations, and negative cache. |
| SERVFAIL | The resolver could not construct a valid answer. | Check authoritative reachability, lame delegation, DNSSEC validation, zone loading, and logs. |
| REFUSED | The server understood the request but policy denied it. | Check recursion, query, transfer, update ACLs, and views. |

In a direct authoritative test, look for the AA flag. In a recursive test, RD in the query asks for recursion and RA in the response says the server offers it. The server shown at the bottom of <code>dig</code> proves which address answered; it does not by itself prove that server was authoritative.

Use this order when a public record is wrong:

1. Query each authoritative server directly with <code>@server +norecurse</code>.
2. Compare SOA serials across primary and secondaries.
3. Trace the parent delegation and glue.
4. Query the normal recursive resolver.
5. Check local NSS, hosts files, and application caches.
6. Continue to routing, transport, TLS, and application checks only after name data is correct.

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

DNS hierarchy, root referrals, TLD delegation, glue, stub resolver, recursive resolver, authoritative server, positive and negative caching, NXDOMAIN, NODATA, SERVFAIL, REFUSED, RRsets, zone syntax, SOA, NS, A, AAAA, CNAME, MX, PTR, TXT, SRV, CAA, DNSSEC records, forward zones, reverse zones, rDNS ownership, <code>in-addr.arpa</code>, <code>ip6.arpa</code>, FCrDNS, RFC 2317 awareness, <code>/etc/named.conf</code>, <code>/var/named/</code>, <code>rndc</code>, <code>named-checkconf</code>, <code>named-checkzone</code>, <code>named-compilezone</code>, <code>dig</code>, <code>host</code>, <code>nslookup</code>, masterfile-format, chroot, TSIG, DNSSEC, <code>dnssec-keygen</code>, <code>dnssec-signzone</code>, DANE, dnsmasq, djbdns, and PowerDNS.

## Mini lab

1. Draw the hierarchy from the DNS root through <code>ir</code> and <code>realsam.ir</code> to <code>www.realsam.ir</code>.
2. Build separate recursive and authoritative servers so their trust boundaries are visible.
3. Create a forward zone containing SOA, NS, A, AAAA, CNAME, MX, TXT, SRV, and CAA examples.
4. Explain the owner, TTL, class, type, and RDATA of each record before loading it.
5. Create the reverse declaration and zone for the isolated 203.0.113.0/24 lab.
6. Make <code>203.0.113.25</code> point to <code>mail.realsam.ir</code> and ensure the forward A record returns to the same address.
7. Use <code>dig -x</code>, an explicit PTR query, and a direct <code>+norecurse</code> authoritative query; explain why the answers may differ.
8. Document how a real cloud provider or ISP would publish or delegate the public PTR and why the domain registrar cannot do it.
9. Explain how RFC 2317 permits classless reverse delegation for a range smaller than /24.
10. Configure a secondary, protect transfer with TSIG, and compare SOA serials.
11. Confirm that an untrusted client cannot recurse and an unauthorized client cannot AXFR.
12. Trace <code>www.realsam.ir</code> from root delegation through DNS, routing, TLS, HTTP virtual-host selection, and final response.
13. Deliberately produce NXDOMAIN, NODATA, REFUSED, and a zone-load SERVFAIL in the isolated lab, then diagnose each one.
14. Record validation commands, query evidence, logs, rollback steps, and remaining security risks.

Success means another learner can explain every DNS role and record, reproduce forward and reverse resolution, identify who controls public rDNS, and locate the first failing layer without guessing.
