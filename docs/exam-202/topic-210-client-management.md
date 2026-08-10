# Topic 210: Network Client Management

Objectives: 210.1, 210.2, 210.3, and 210.4

## 210.1 DHCP

DHCPv4 normally uses UDP 67 on the server and UDP 68 on the client. The DORA flow is Discover, Offer, Request, and Acknowledge.

### Safe DHCPv4 example

~~~dhcp
authoritative;
default-lease-time 3600;
max-lease-time 86400;

option domain-name "realsam.ir";
option domain-name-servers 10.20.0.53;

subnet 10.20.0.0 netmask 255.255.255.0 {
    option routers 10.20.0.1;
    option broadcast-address 10.20.0.255;
    range 10.20.0.100 10.20.0.200;
}

host printer1 {
    hardware ethernet 02:00:00:00:20:20;
    fixed-address 10.20.0.20;
    option host-name "printer1";
}
~~~

Keep fixed addresses outside the dynamic range. Do not use .local as a normal unicast DNS suffix.

Validate and inspect:

~~~bash
sudo dhcpd -t -cf /etc/dhcp/dhcpd.conf
sudo systemctl reload dhcpd
sudo journalctl -u dhcpd
sudo less /var/lib/dhcpd/dhcpd.leases
arp -an
~~~

Service and lease paths can differ. Bind the daemon only to intended interfaces using the distribution service configuration.

### BOOTP and network boot

A host can receive boot-server information:

~~~dhcp
host installer {
    hardware ethernet 02:00:00:00:30:30;
    fixed-address 10.20.0.30;
    next-server 10.20.0.10;
    filename "pxelinux.0";
}
~~~

### DHCP relay

Broadcast discovery normally does not cross routers. A relay listens on the client network and forwards requests to a server.

~~~bash
sudo dhcrelay -i eth1 10.20.0.53
~~~

Use the packaged service configuration for persistence and restrict relay interfaces.

### DHCPv6 and Router Advertisements

DHCPv6 can provide addresses and options. IPv6 Router Advertisements provide default-router and prefix information. DHCPv6 does not replace RA for the normal default route.

radvd example:

~~~text
interface eth0 {
    AdvSendAdvert on;
    prefix 2001:db8:20::/64 {
        AdvOnLink on;
        AdvAutonomous on;
    };
};
~~~

Validate the installed radvd version and protect the interface with IPv6 firewall policy.

## 210.2 PAM authentication

PAM separates applications from authentication methods. Files are under /etc/pam.d/ or the older /etc/pam.conf.

A rule contains:

~~~text
type  control  module-path  module-arguments
~~~

Types:

- auth: prove identity
- account: decide whether access is allowed
- password: change credentials
- session: setup and cleanup

Common controls are required, requisite, sufficient, and optional. Order matters.

Important modules:

- pam_unix: local passwords
- pam_cracklib or pam_pwquality: password quality
- pam_limits: resource limits
- pam_listfile: list-based access
- pam_sss: SSSD authentication

Never edit a remote-login PAM stack without a root console and a second tested session. A syntax or order mistake can lock out all users.

Local identity files:

~~~bash
getent passwd alice
sudo getent shadow alice
grep '^passwd:' /etc/nsswitch.conf
~~~

/etc/shadow must not be world-readable.

### SSSD

SSSD can provide identity and authentication from LDAP or Active Directory.

~~~ini
[sssd]
services = nss, pam
domains = realsam

[domain/realsam]
id_provider = ldap
auth_provider = ldap
ldap_uri = ldaps://ldap.realsam.ir
ldap_search_base = dc=realsam,dc=ir
cache_credentials = true
~~~

Protect /etc/sssd/sssd.conf with mode 0600.

~~~bash
sudo sssctl config-check
sudo systemctl restart sssd
getent passwd directory-user
id directory-user
~~~

## 210.3 LDAP client usage

LDAP entries use Distinguished Names.

Example LDIF:

~~~ldif
dn: uid=alice,ou=People,dc=realsam,dc=ir
objectClass: inetOrgPerson
uid: alice
cn: Alice Realsam
sn: Realsam
mail: alice@realsam.ir
~~~

Search:

~~~bash
ldapsearch -x -H ldaps://ldap.realsam.ir \
  -b dc=realsam,dc=ir "(uid=alice)"
~~~

Add, modify, delete, and change password:

~~~bash
ldapadd -x -H ldaps://ldap.realsam.ir -D "cn=admin,dc=realsam,dc=ir" -W -f alice.ldif
ldapmodify -x -H ldaps://ldap.realsam.ir -D "cn=admin,dc=realsam,dc=ir" -W -f change.ldif
ldapdelete -x -H ldaps://ldap.realsam.ir -D "cn=admin,dc=realsam,dc=ir" -W "uid=alice,ou=People,dc=realsam,dc=ir"
ldappasswd -x -H ldaps://ldap.realsam.ir -D "cn=admin,dc=realsam,dc=ir" -W "uid=alice,ou=People,dc=realsam,dc=ir"
~~~

Use TLS and certificate validation. Avoid placing bind passwords on the command line.

## 210.4 OpenLDAP server

slapd is the server. Modern OpenLDAP uses directory-based dynamic configuration under cn=config, often stored in /etc/ldap/slapd.d/ or /etc/openldap/slapd.d/.

Directory tree example:

~~~text
dc=realsam,dc=ir
├── ou=People
├── ou=Groups
└── ou=Services
~~~

Key ideas:

- schema defines allowed attributes and object classes
- OIDs globally identify schema elements
- objectClass defines entry behavior
- ACLs control who can read or write
- changetype operations include add, modify, delete, and modrdn
- White Pages means directory information about people and organizations

Offline database tools:

~~~bash
sudo slapcat -n 0
sudo slapcat -b dc=realsam,dc=ir
sudo slapadd -b dc=realsam,dc=ir -l backup.ldif
sudo slapindex -b dc=realsam,dc=ir
~~~

Stop slapd before offline writes and fix ownership afterward according to distribution documentation. Data is commonly under /var/lib/ldap/.

Test configuration and logs:

~~~bash
slaptest -u
journalctl -u slapd
ldapsearch -x -H ldap://127.0.0.1 -b dc=realsam,dc=ir -s base
~~~

### Access-control idea

Allow users to change their own password, allow an administrator to manage entries, and deny anonymous access to password hashes. Exact ACL syntax and order must be tested because the first matching access rule controls the result.

Use StartTLS or LDAPS with a trusted certificate. Restrict management access and back up both data and cn=config.

## Exam checklist

dhcpd.conf, dhcpd.leases, DHCP logs, arp, dhcpd, radvd, radvd.conf, /etc/pam.d/, pam.conf, passwd, shadow, nsswitch.conf, pam_unix, pam_cracklib, pam_limits, pam_listfile, pam_sss, sssd.conf, ldapsearch, ldappasswd, ldapadd, ldapdelete, slapd, slapd-config, LDIF, slapadd, slapcat, slapindex, /var/lib/ldap/, and loglevel.

## Mini lab

Configure DHCP with a dynamic pool, fixed host, and relay. Observe a lease. Configure a test PAM service, query LDAP, add and modify one LDIF entry, and back up an OpenLDAP database and cn=config.
