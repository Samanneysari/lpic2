# Topic 210: Network Client Management

Objectives: 210.1, 210.2, 210.3, and 210.4

<!-- BEGIN BEGINNER FOUNDATION -->
## Learn the idea before running commands

### What network client management covers

This topic joins three services that help client systems operate consistently: DHCP supplies network settings, PAM controls authentication policy for local services, and LDAP provides a directory that many systems can query.

### DHCP and the DORA exchange

A new IPv4 client normally follows four messages:

1. **Discover:** the client broadcasts to find a server.
2. **Offer:** a server proposes an address and options.
3. **Request:** the client requests one offered lease.
4. **Acknowledge:** the server confirms the lease.

A subnet declaration defines the address range and options such as router, DNS server, and lease time. A host reservation maps a known client identifier, commonly a MAC address, to a fixed address. A DHCP relay forwards requests between a client network and a server on another network.

DHCP must match the real subnet. Two uncontrolled servers can give conflicting answers, and an incorrect router or DNS option can disconnect every renewing client.

### PAM and NSS

PAM is a stack of authentication modules used by programs such as sshd, login, and sudo. The calling application selects a PAM service file. Each line has a management group, a control rule, a module, and module arguments. Order and control flags matter; a mistaken rule can lock out administrators.

NSS decides where libc looks for users, groups, hosts, and other databases. PAM answers “may this authentication or account action succeed?” while NSS answers “where is this identity or name found?” They often work together but are not the same system.

### LDAP and OpenLDAP

LDAP stores entries in a hierarchical Directory Information Tree. Every entry has a distinguished name, object classes, and attributes. A schema defines allowed object classes and attributes. Search scope can be base, one level, or subtree.

OpenLDAP uses slapd as the server. Modern installations commonly store live configuration under cn=config, while the exam also expects awareness of traditional slapd.conf. Use TLS for credentials and restrict anonymous access and write permissions.

### From a login name to an LDAP-backed session

A typical Linux login using SSSD and LDAP follows this path:

1. A service such as <code>sshd</code> starts the PAM stack named by its PAM service configuration.
2. An NSS lookup asks where the username and group information can be found.
3. NSS contacts SSSD according to <code>/etc/nsswitch.conf</code>.
4. SSSD checks its cache and, when required, queries LDAP for identity attributes.
5. PAM asks the configured SSSD PAM module to authenticate and perform account checks.
6. SSSD contacts the directory through the configured protected channel and evaluates provider policy.
7. PAM control flags combine the module result with other required, requisite, sufficient, or optional modules.
8. If identity, authentication, and account policy succeed, the application creates the session.

DNS discovery, TLS trust, time synchronization, directory reachability, LDAP search base, UID/GID mapping, PAM order, and account policy can fail independently. Keep a tested local recovery account and an existing root session while changing this chain.

### Safe implementation sequence

Build DHCP in an isolated lab, validate before service start, and inspect leases. For PAM or LDAP identity changes, keep an existing root console session open, test with a separate session, and retain a known local emergency account.
<!-- END BEGINNER FOUNDATION -->

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

<!-- LINE-BY-LINE 1 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>authoritative;</code> | Declares that this DHCP server is authoritative for its configured subnets, allowing it to reject invalid leases quickly. |
| 2 | <code>default-lease-time 3600;</code> | Sets the normal DHCP lease duration in seconds. |
| 3 | <code>max-lease-time 86400;</code> | Sets the longest lease duration this DHCP server will grant. |
| 5 | <code>option domain-name "realsam.ir";</code> | Sends realsam.ir as the client's DNS search domain. |
| 6 | <code>option domain-name-servers 10.20.0.53;</code> | Sends the listed DNS resolver address to DHCP clients. |
| 8 | <code>subnet 10.20.0.0 netmask 255.255.255.0 {</code> | Opens the DHCP scope for the stated IPv4 network and netmask. |
| 9 | <code>option routers 10.20.0.1;</code> | Sends the default-gateway address to clients in this scope. |
| 10 | <code>option broadcast-address 10.20.0.255;</code> | Sends the IPv4 broadcast address for this subnet. |
| 11 | <code>range 10.20.0.100 10.20.0.200;</code> | Defines the first and last dynamically assignable address in this DHCP pool. |
| 12 | <code>}</code> | Closes the configuration or multi-line value opened above. |
| 14 | <code>host printer1 {</code> | Opens a fixed DHCP host reservation with the shown label. |
| 15 | <code>hardware ethernet 02:00:00:00:20:20;</code> | Matches the reservation to this client MAC address. |
| 16 | <code>fixed-address 10.20.0.20;</code> | Reserves the shown IPv4 address for the matched host. |
| 17 | <code>option host-name "printer1";</code> | Sends the shown host name to this reserved client. |
| 18 | <code>}</code> | Closes the configuration or multi-line value opened above. |

Keep fixed addresses outside the dynamic range. Do not use .local as a normal unicast DNS suffix.

Validate and inspect:

~~~bash
sudo dhcpd -t -cf /etc/dhcp/dhcpd.conf
sudo systemctl reload dhcpd
sudo journalctl -u dhcpd
sudo less /var/lib/dhcpd/dhcpd.leases
arp -an
~~~

<!-- LINE-BY-LINE 2 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo dhcpd -t -cf /etc/dhcp/dhcpd.conf</code> | sudo requests administrator privileges for this operation. Runs ISC DHCP or validates the configuration and lease context without starting it. |
| 2 | <code>sudo systemctl reload dhcpd</code> | sudo requests administrator privileges for this operation. Inspects or changes systemd units, targets, enablement, or system state. |
| 3 | <code>sudo journalctl -u dhcpd</code> | sudo requests administrator privileges for this operation. Reads structured systemd journal records with the shown unit or time filter. |
| 4 | <code>sudo less /var/lib/dhcpd/dhcpd.leases</code> | sudo requests administrator privileges for this operation. Opens a file in a pager for safe inspection. |
| 5 | <code>arp -an</code> | Displays or changes the legacy IPv4 neighbor cache; ip neigh is the modern replacement. |

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

<!-- LINE-BY-LINE 3 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>host installer {</code> | Opens a fixed DHCP host reservation with the shown label. |
| 2 | <code>hardware ethernet 02:00:00:00:30:30;</code> | Matches the reservation to this client MAC address. |
| 3 | <code>fixed-address 10.20.0.30;</code> | Reserves the shown IPv4 address for the matched host. |
| 4 | <code>next-server 10.20.0.10;</code> | Tells the PXE client which server supplies its boot file. |
| 5 | <code>filename "pxelinux.0";</code> | Names the network boot program the PXE client should request. |
| 6 | <code>}</code> | Closes the configuration or multi-line value opened above. |

### DHCP relay

Broadcast discovery normally does not cross routers. A relay listens on the client network and forwards requests to a server.

~~~bash
sudo dhcrelay -i eth1 10.20.0.53
~~~

<!-- LINE-BY-LINE 4 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo dhcrelay -i eth1 10.20.0.53</code> | sudo requests administrator privileges for this operation. Forwards DHCP messages between client networks and the server. |

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

<!-- LINE-BY-LINE 5 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>interface eth0 {</code> | Opens an IPv6 router-advertisement policy for this interface. |
| 2 | <code>AdvSendAdvert on;</code> | Enables periodic IPv6 Router Advertisements on this interface. |
| 3 | <code>prefix 2001:db8:20::/64 {</code> | Opens advertisement options for this IPv6 prefix. |
| 4 | <code>AdvOnLink on;</code> | Marks the advertised prefix as directly reachable on this link. |
| 5 | <code>AdvAutonomous on;</code> | Allows clients to form IPv6 addresses from this prefix with SLAAC. |
| 6 | <code>};</code> | Closes the configuration or multi-line value opened above. |
| 7 | <code>};</code> | Closes the configuration or multi-line value opened above. |

Validate the installed radvd version and protect the interface with IPv6 firewall policy.

## 210.2 PAM authentication

PAM separates applications from authentication methods. Files are under /etc/pam.d/ or the older /etc/pam.conf.

A rule contains:

~~~text
type  control  module-path  module-arguments
~~~

<!-- LINE-BY-LINE 6 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>type  control  module-path  module-arguments</code> | Shows the four fields of a PAM rule: management group, control action, module path, and module arguments. |

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

<!-- LINE-BY-LINE 7 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>getent passwd alice</code> | Queries an NSS database such as hosts, passwd, or group. |
| 2 | <code>sudo getent shadow alice</code> | sudo requests administrator privileges for this operation. Queries an NSS database such as hosts, passwd, or group. |
| 3 | <code>grep '^passwd:' /etc/nsswitch.conf</code> | Selects lines that match the requested text or expression. |

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

<!-- LINE-BY-LINE 8 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>[sssd]</code> | Opens the named INI-style configuration section. |
| 2 | <code>services = nss, pam</code> | Enables the NSS and PAM responders in SSSD. |
| 3 | <code>domains = realsam</code> | Activates the named SSSD domain section. |
| 5 | <code>[domain/realsam]</code> | Opens the named INI-style configuration section. |
| 6 | <code>id_provider = ldap</code> | Obtains user and group identity data from LDAP. |
| 7 | <code>auth_provider = ldap</code> | Uses LDAP as the authentication provider for this SSSD domain. |
| 8 | <code>ldap_uri = ldaps://ldap.realsam.ir</code> | Connects SSSD to ldap.realsam.ir using LDAP protected by TLS. |
| 9 | <code>ldap_search_base = dc=realsam,dc=ir</code> | Sets the base distinguished name under which SSSD searches for identities. |
| 10 | <code>cache_credentials = true</code> | Allows SSSD to cache credential verifiers for controlled offline authentication. |

Protect /etc/sssd/sssd.conf with mode 0600.

~~~bash
sudo sssctl config-check
sudo systemctl restart sssd
getent passwd directory-user
id directory-user
~~~

<!-- LINE-BY-LINE 9 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo sssctl config-check</code> | sudo requests administrator privileges for this operation. Checks and diagnoses SSSD configuration, domains, and cached identities. |
| 2 | <code>sudo systemctl restart sssd</code> | sudo requests administrator privileges for this operation. Inspects or changes systemd units, targets, enablement, or system state. |
| 3 | <code>getent passwd directory-user</code> | Queries an NSS database such as hosts, passwd, or group. |
| 4 | <code>id directory-user</code> | Shows the resolved user ID, group ID, and supplementary groups. |

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

<!-- LINE-BY-LINE 10 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>dn: uid=alice,ou=People,dc=realsam,dc=ir</code> | Sets the LDAP attribute dn to the value shown after the colon. |
| 2 | <code>objectClass: inetOrgPerson</code> | Sets the LDAP attribute objectClass to the value shown after the colon. |
| 3 | <code>uid: alice</code> | Sets the LDAP attribute uid to the value shown after the colon. |
| 4 | <code>cn: Alice Realsam</code> | Sets the LDAP attribute cn to the value shown after the colon. |
| 5 | <code>sn: Realsam</code> | Sets the LDAP attribute sn to the value shown after the colon. |
| 6 | <code>mail: alice@realsam.ir</code> | Sets the LDAP attribute mail to the value shown after the colon. |

Search:

~~~bash
ldapsearch -x -H ldaps://ldap.realsam.ir \
  -b dc=realsam,dc=ir "(uid=alice)"
~~~

<!-- LINE-BY-LINE 11 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>ldapsearch -x -H ldaps://ldap.realsam.ir \</code> | Binds to LDAP and searches with the supplied base, scope, filter, and attributes. The final backslash continues this logical command on the next physical line. |
| 2 | <code>-b dc=realsam,dc=ir "(uid=alice)"</code> | This physical line adds the shown option or argument to the command started on the previous line. |

Add, modify, delete, and change password:

~~~bash
ldapadd -x -H ldaps://ldap.realsam.ir -D "cn=admin,dc=realsam,dc=ir" -W -f alice.ldif
ldapmodify -x -H ldaps://ldap.realsam.ir -D "cn=admin,dc=realsam,dc=ir" -W -f change.ldif
ldapdelete -x -H ldaps://ldap.realsam.ir -D "cn=admin,dc=realsam,dc=ir" -W "uid=alice,ou=People,dc=realsam,dc=ir"
ldappasswd -x -H ldaps://ldap.realsam.ir -D "cn=admin,dc=realsam,dc=ir" -W "uid=alice,ou=People,dc=realsam,dc=ir"
~~~

<!-- LINE-BY-LINE 12 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>ldapadd -x -H ldaps://ldap.realsam.ir -D "cn=admin,dc=realsam,dc=ir" -W -f alice.ldif</code> | Adds LDIF entries to LDAP after the selected authentication. |
| 2 | <code>ldapmodify -x -H ldaps://ldap.realsam.ir -D "cn=admin,dc=realsam,dc=ir" -W -f change.ldif</code> | Applies LDIF modifications to existing directory entries. |
| 3 | <code>ldapdelete -x -H ldaps://ldap.realsam.ir -D "cn=admin,dc=realsam,dc=ir" -W "uid=alice,ou=People,dc=realsam,dc=ir"</code> | Deletes the named LDAP entry after authentication. |
| 4 | <code>ldappasswd -x -H ldaps://ldap.realsam.ir -D "cn=admin,dc=realsam,dc=ir" -W "uid=alice,ou=People,dc=realsam,dc=ir"</code> | Changes an LDAP password using the password-modify operation. |

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

<!-- LINE-BY-LINE 13 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>dc=realsam,dc=ir</code> | Shows the directory suffix that represents the realsam.ir namespace. |
| 2 | <code>├── ou=People</code> | Shows an organizational-unit branch under the directory suffix; this is a diagram line, not a command. |
| 3 | <code>├── ou=Groups</code> | Shows an organizational-unit branch under the directory suffix; this is a diagram line, not a command. |
| 4 | <code>└── ou=Services</code> | Shows an organizational-unit branch under the directory suffix; this is a diagram line, not a command. |

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

<!-- LINE-BY-LINE 14 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo slapcat -n 0</code> | sudo requests administrator privileges for this operation. Exports an OpenLDAP database as LDIF for inspection or backup. |
| 2 | <code>sudo slapcat -b dc=realsam,dc=ir</code> | sudo requests administrator privileges for this operation. Exports an OpenLDAP database as LDIF for inspection or backup. |
| 3 | <code>sudo slapadd -b dc=realsam,dc=ir -l backup.ldif</code> | sudo requests administrator privileges for this operation. Imports LDIF directly into an offline OpenLDAP database. |
| 4 | <code>sudo slapindex -b dc=realsam,dc=ir</code> | sudo requests administrator privileges for this operation. Rebuilds OpenLDAP database indexes while following the supported service-state procedure. |

Stop slapd before offline writes and fix ownership afterward according to distribution documentation. Data is commonly under /var/lib/ldap/.

Test configuration and logs:

~~~bash
slaptest -u
journalctl -u slapd
ldapsearch -x -H ldap://127.0.0.1 -b dc=realsam,dc=ir -s base
~~~

<!-- LINE-BY-LINE 15 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>slaptest -u</code> | Validates OpenLDAP server configuration. |
| 2 | <code>journalctl -u slapd</code> | Reads structured systemd journal records with the shown unit or time filter. |
| 3 | <code>ldapsearch -x -H ldap://127.0.0.1 -b dc=realsam,dc=ir -s base</code> | Binds to LDAP and searches with the supplied base, scope, filter, and attributes. |

### Access-control idea

Allow users to change their own password, allow an administrator to manage entries, and deny anonymous access to password hashes. Exact ACL syntax and order must be tested because the first matching access rule controls the result.

Use StartTLS or LDAPS with a trusted certificate. Restrict management access and back up both data and cn=config.

## Exam checklist

dhcpd.conf, dhcpd.leases, DHCP logs, arp, dhcpd, radvd, radvd.conf, /etc/pam.d/, pam.conf, passwd, shadow, nsswitch.conf, pam_unix, pam_cracklib, pam_limits, pam_listfile, pam_sss, sssd.conf, ldapsearch, ldappasswd, ldapadd, ldapdelete, slapd, slapd-config, LDIF, slapadd, slapcat, slapindex, /var/lib/ldap/, and loglevel.

## Mini lab

Configure DHCP with a dynamic pool, fixed host, and relay. Observe a lease. Configure a test PAM service, query LDAP, add and modify one LDIF entry, and back up an OpenLDAP database and cn=config.
