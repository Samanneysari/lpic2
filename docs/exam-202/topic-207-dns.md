# Topic 207: Domain Name Server

Objectives: 207.1, 207.2, and 207.3

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

A public authoritative server should normally disable recursion:

~~~text
options {
    recursion no;
    allow-query { any; };
};
~~~

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

Create the directory with correct ownership and security labels. On systemd systems, also use:

~~~bash
journalctl -u named
journalctl -u bind9
~~~

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

Older BIND accepts type master. A secondary may use:

~~~text
zone "realsam.ir" IN {
    type secondary;
    file "slaves/realsam.ir.zone";
    primaries { 203.0.113.53 key "realsam-xfr"; };
};
~~~

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

The second SOA name represents hostmaster@realsam.ir; the first dot replaces the at sign. Increase the serial after every change.

The ns1 and ns2 A records are authoritative data in this child zone. Glue is supplied by the parent zone or registrar when a delegated nameserver is inside the delegated domain.

Validate before reload:

~~~bash
named-checkconf -z
named-checkzone realsam.ir /var/named/realsam.ir.zone
named-compilezone -o /tmp/realsam.ir.raw -f text -F raw realsam.ir /var/named/realsam.ir.zone
sudo rndc reload realsam.ir
~~~

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

IPv6 reverse DNS uses nibble-reversed names under ip6.arpa.

### Delegation and root hints

A parent delegates a child with NS records and, when required, glue. Example inside realsam.ir:

~~~dns
lab       IN NS ns1.lab.realsam.ir.
ns1.lab   IN A  203.0.113.60
~~~

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

The AXFR command should fail for unauthorized clients.

## 207.3 Secure DNS

### Run with limited privilege

BIND should drop root privileges after binding low ports. Distribution packages normally supply a dedicated user. Chroot packages or options can isolate filesystem access. A chroot adds containment but does not replace updates, permissions, and access controls.

### TSIG

Generate a shared key on a protected host:

~~~bash
tsig-keygen -a hmac-sha256 realsam-xfr
~~~

Key file:

~~~text
key "realsam-xfr" {
    algorithm hmac-sha256;
    secret "REPLACE_WITH_GENERATED_SECRET";
};
~~~

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
