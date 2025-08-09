# Chapter 1: The DHCP Protocol and Server Setup
## DHCP Definition and Application

DHCP stands for Dynamic Host Configuration Protocol. It is a critical network service that operates on a 

Client-Server model. Its primary application is to automatically assign network configuration settings to client devices, eliminating the need for manual configuration.

When a new device connects to a network, the DHCP client on the device communicates with a DHCP server to automatically obtain essential information such as its IP address, subnet mask, default gateway, and DNS servers.

The DHCP protocol is a more advanced successor to an older protocol named 

bootp, which was originally developed at Casanova University to serve diskless client workstations.

## DHCP Server Installation
To set up a DHCP server on a Red Hat-based Linux system, you must first check if the necessary software package is installed and, if not, install it.

### 1. Check for Installed Packages:
To see if any DHCP-related packages are already on the system, use the following commands:

 List all installed packages
```
rpm -qa
```

Filter the output for packages containing the word "dhcp"
```
rpm -qa | grep dhcp
```


### 2. Install the dhcp-server Package:
If the server package is not present, install it using the dnf package manager:
```
sudo dnf install dhcp-server
```

## DHCP Server Configuration
The main configuration file for the DHCP server is located at 
```
vim /etc/dhcp/dhcpd.conf
```
In this file, we define the address pools (also known as scopes) and the rules for address allocation.

### Example Configuration File
Define an Address Pool | Scope
```

subnet 192.168.1.0 netmask 255.255.255.0 {
        range 192.168.1.55 192.168.1.65;
        option routers 192.168.1.1;
        option domain-name-servers 8.8.8.8;
        option domain-name "mftplus.local";
}
```

**`subnet 192.168.1.0 netmask 255.255.255.0 { ... }`**: This line begins a configuration block for the 192.168.1.0 network with the netmask 255.255.255.0. The DHCP server will only serve clients within this specific network.

**`range 192.168.1.55 192.168.1.65;`**: This directive defines the pool of leasable IP addresses. The server is only authorized to assign IPs between 192.168.1.55 and 192.168.1.65 to clients.


**`option routers 192.168.1.1;`**: This option sets the default gateway address for the clients.


**`option domain-name-servers 8.8.8.8;`**: This option specifies the DNS server address(es) for the clients.


**`option domain-name "mftplus.local";`**: This option defines the local domain search name for the clients.

## Service Management and Troubleshooting
After applying the configuration, you must manage the service and ensure it is operating correctly.

Service and Firewall Management Commands

Restarts the DHCP service to apply any new configurations.
```
systemctl restart dhcpd
```

This is the primary troubleshooting command used to view logs and potential errors for the dhcpd service.
```
journalctl -xeu dhcpd
```

Checks the current status of the system's firewall service.
```
systemctl status firewalld.service
```
This command adds a permanent rule to the firewall to allow traffic for the DHCP service.
```
firewall-cmd --add-service=dhcp --permanent
```

Reloads the firewall rules to apply the new changes immediately.
```
firewall-cmd --reload
```

 This command displays the contents of the leases file, which contains a list of all assigned IP addresses and their corresponding client details.
```
less /var/lib/dhcpd/dhcpd.leases
```

## Address Reservation
This feature allows an administrator to assign a permanent, static IP address to a specific device based on its unique MAC (Media Access Control) address.

1. Edit the configuration file:
```
vim /etc/dhcp/dhcpd.conf
```


2. Add a host block:
```
host TEST1 {
        hardware ethernet 00:0C:29:83:5C:BC;
        fixed-address 192.168.1.77;
}
```


**`host TEST1`**: Defines a configuration block for a specific host named TEST1.


**`hardware ethernet ...;`**: Specifies the MAC address of the target device.


**`fixed-address ...;`**: Specifies the static IP address that should always be assigned to this device.

3. Apply the changes:
```
systemctl restart dhcpd
```

## Protocol Mechanism (DORA)
The communication between a DHCP client and server follows a four-step process known as 

DORA.


**`Discover`**: The client sends a broadcast dhcp discover message on the network to find a DHCP server.


**`Offer`**: Any DHCP server that receives the discover message responds with a dhcp offer message, proposing an IP address to the client.


**`Request`**: The client chooses one of the offers and sends a dhcp request message, formally requesting the offered IP address.


**`Acknowledge (ACK)`**: The server finalizes the allocation with a dhcp ack message, confirming the lease and providing any remaining configuration details.

Other message types, such as dhcp nack (to reject a request) and dhcp inform, are also part of the protocol.

Sending Logs to a Central Server (RSYSLOG)
For better log management in a large network, the DHCP server's logs can be directed to a central rsyslog server.

1. Edit the configuration file:
```
vim /etc/dhcp/dhcpd.conf
```


2. Add the log-facility directive:
```
log-facility local3;
```

This directive instructs the DHCP service to tag its log messages with a specific "facility" named local3. The system's rsyslog service can then be configured to handle all messages with this tag in a special way, such as forwarding them to a remote log server.



# Chapter 2: The Domain Name System (DNS)
## DNS Definition and Application

DNS stands for the Domain Name System. It is considered a critical service for the internet and computer networks. The primary function of DNS is name resolution, which is the process of translating human-readable domain names (like www.example.com) into machine-readable IP addresses (like 93.184.216.34).

The core purpose of DNS is to act as a global, distributed phonebook for the internet. Humans are better at remembering names, while computers communicate using numbers (IP addresses). DNS bridges this gap, making the internet user-friendly.


**`Forward Lookup`**: Translating a Fully Qualified Domain Name (FQDN) to an IP address.


**`Reverse Lookup`**: Translating an IP address back to an FQDN.

Without DNS, users would need to memorize the numerical IP addresses for every website and service they want to access, which would make navigating the modern internet practically impossible. The original, widely-used software for implementing DNS is BIND (Berkeley Internet Name Daemon), which was developed at the University of California, Berkeley.

## The DNS Hierarchy: Server Roles
The DNS system is a hierarchical and distributed database. This hierarchy is composed of several types of servers, each with a specific role. The resolution process typically flows from the Root servers down to the Authoritative servers.

### 1. Root DNS Servers
A Root DNS Server is one of the servers at the highest level of the DNS hierarchy. There are only 13 logical root server clusters in the world, which are responsible for directing traffic to the appropriate Top-Level Domain servers. They do not know the IP address of www.example.com, but they know where to find the servers that manage the .com domain.

### 2. Top-Level Domain (TLD) Servers
A Top-Level Domain (TLD) Server is responsible for managing all domain names that share a common top-level domain, such as .com, .org, .net, or country-specific domains like .ir. When queried, a TLD server does not provide the final IP address but instead directs the request to the authoritative name servers responsible for that specific domain.

### 3. Authoritative Name Servers
An Authoritative Name Server is the final authority for a specific domain (e.g., itpolicy.ir). This is the server that holds the actual zone file containing all the DNS records (A, MX, CNAME, etc.) for that domain. When an authoritative server receives a query for a record within its zone, it provides a definitive, "authoritative" answer.

## The Purpose of Using Multiple Name Servers
In nearly all standard configurations, you will see multiple name servers defined for a single domain (e.g., 

ns1.itpolicy.ir, ns2.itpolicy.ir, ns3.itpolicy.ir). This is done for two critical reasons:

**`Redundancy and High Availability`**: If one name server fails, goes offline for maintenance, or becomes unreachable, the other name servers can continue to answer DNS queries for the domain. This prevents a single point of failure and ensures the domain's services (like its website and email) remain accessible.

**`Load Balancing`**: By having multiple servers, the incoming DNS query traffic can be distributed among them. This prevents any single server from becoming overloaded with requests, improving response times and overall performance, especially for high-traffic domains.

## The DNS Resolution Cycle: A Step-by-Step Guide
The process of translating a domain name into an IP address is a multi-step, hierarchical journey. Let's walk through the complete cycle using a request for the domain www.yahoo.com as an example.

### Key Roles in the Resolution Process
Client: Your computer or device that initiates the request.

**`Recursive Resolver`**: A server (often provided by your ISP or a public service like Google's 8.8.8.8) that performs the entire lookup process on behalf of the client.

**`Root Server`**: The highest level in the DNS hierarchy.

**`Top-Level Domain (TLD) Server`**: The server responsible for a specific TLD, like .com.

**`Authoritative Name Server`**: The server with the definitive and final records for a specific domain, like yahoo.com.


### 1.The Initial Query
A user's computer needs to find the IP address for www.yahoo.com. It sends a query to its configured Recursive Resolver. The resolver first checks its local cache to see if it already has the answer. If not, it begins the full resolution process.

### 2.Querying the Root Server
The Recursive Resolver, starting from the top, sends a query to a Root Server, asking: "Who manages the .com TLD?"

### 3.The Root Server's Referral
The Root Server doesn't know the IP for www.yahoo.com, but it knows who is responsible for the .com domains. It responds with a list of the TLD servers for .com.

### 4.Querying the TLD Server
The resolver then sends a new query to one of the .com TLD servers, asking: "Who are the authoritative name servers for the yahoo.com domain?"

### 5.The TLD Server's Referral
The .com TLD server checks its records and responds with the names of the Authoritative Name Servers for yahoo.com (e.g., ns1.yahoo.com and ns2.yahoo.com).

### 6.The Final Query to the Authority
The resolver now sends its final query to one of yahoo.com's Authoritative Name Servers, asking the definitive question: "What is the IP address (the 'A' record) for www.yahoo.com?"

### 7.The Authoritative Answer
The Authoritative Name Server looks into its zone file, finds the correct record, and returns the final IP address for www.yahoo.com back to the resolver.

### 8.The Response to the Client
The Recursive Resolver now has the answer. It sends the IP address back to the user's computer. The resolver also caches this information for a specific amount of time (determined by the record's TTL), allowing it to answer any future requests for www.yahoo.com instantly without repeating this entire journey.

## DNS Zone
A DNS Zone is a specific part of the internet's domain name system that is managed as a single unit. In simple terms, it's a domain that you have administrative control over, such as itpolicy.ir.

### Zone File
The Zone File is the actual text file stored on a DNS server. This file contains all the technical data and DNS records for a specific zone. When you need to make changes to your domain, you edit this file.

### aster and Slave Servers
For reliability, a domain should always have more than one DNS server. These servers operate in master and slave roles.

**`Master Server`**: This is the main, primary server for a zone. It holds the original, editable version of the zone file. All changes to the zone must be made on this server.

**`Slave Server`**: This is a secondary or backup server. It holds a read-only copy of the master's zone file. It automatically gets updates from the master server through a process called a zone transfer. The purpose of a slave server is to provide redundancy (if the master fails) and load balancing (to help answer queries).

### Zone Records
Zone records are the individual lines of information inside a zone file. Each record is an instruction that defines how a part of your domain should work. Here is a list of the most common and important record types:

**`SOA (Start of Authority)`**: The first record in a zone file. It defines the main properties of the zone, such as the master name server, the administrator's email, and timers for how the zone should be updated.

**`NS (Name Server)`**: Specifies the official name servers for a zone. Every zone must have at least two NS records for redundancy.

**`A (Address)`**: The most common record. It maps a hostname to an IPv4 address (e.g., 92.114.19.118).

**`AAAA (Quad A)`**: Similar to the A record, but maps a hostname to an IPv6 address.

**`CNAME (Canonical Name)`**: Creates an alias or nickname. It points a hostname to another hostname. For example, ftp.example.com could be a CNAME pointing to server1.example.com.

**`MX (Mail Exchanger)`**: Specifies the mail servers responsible for receiving emails for the domain. These records have a priority number to determine the order in which mail servers should be tried.

**`PTR (Pointer)`**: Performs the opposite of an A record (a reverse lookup). It maps an IP address back to a hostname. This is widely used for security checks, especially by mail servers.

**`TXT (Text)`**: Holds plain text information. It is commonly used for security policies like SPF (Sender Policy Framework) to prevent email spoofing and for verifying domain ownership.

**`SRV (Service)`**: Locates a specific network service. It points to the hostname and port number where a service (like VoIP or LDAP) can be found.

**`CAA (Certification Authority Authorization)`**: A security record that specifies which Certificate Authorities (CAs) are permitted to issue SSL certificates for the domain.

### DNS Recursion
Recursion is a process where a DNS server does all the hard work to find a complete answer for a client. If the server doesn't know the answer, it will query other DNS servers across the internet (Root, TLD, etc.) on the client's behalf and will only return the final, definitive answer.

### DNS Forwarding
Forwarding is an alternative to recursion. A DNS server configured for forwarding will, upon receiving a query it cannot answer itself, simply pass the query to another, pre-configured DNS server (a forwarder, such as Google's 8.8.8.8). It then waits for the forwarder to do the work and send back the answer.

### The recursion Directive: yes vs. no
This is a setting in the DNS server's configuration file that controls its behavior.

**`recursion yes;`**: This setting allows the server to perform recursion for its clients. This should be enabled on servers intended to provide DNS resolution for a trusted network (like an office LAN or an ISP's customers).

**`recursion no;`**: This setting disables recursion. The server will only provide answers for zones it is directly authoritative for (its own master or slave zones). This is a critical security setting for any public-facing authoritative server, as it prevents the server from being used in DDoS reflection attacks.

## BIND Configuration (/etc/named.conf)
The main configuration file for the BIND DNS server is /etc/named.conf. This file tells the server what zones it is responsible for and sets its global behavior.

Initial named.conf Settings
When you first set up a BIND server, there are a few important lines in the options block you need to check and modify.

### 1. The listen-on Directive
This directive controls which IP addresses the BIND server will accept DNS queries on.
```
listen-on port 53 { 127.0.0.1; 92.114.19.118; }; 
```

By default, BIND might only listen on 127.0.0.1 (localhost). To make your DNS server accessible to other computers on the network, you must add its network IP address here. In this example, the server will now accept queries on both its localhost address and its public address, 
```
92.114.19.118.
```

### 2. The allow-query Directive
This directive sets a global rule for who is allowed to send queries to your server.
```
allow-query     { localhost; any; }; 
```
This example allows queries from localhost (the server itself) and from any other IP address. This is a common setting for a public DNS server.

### Configuring Forwarders
If you are setting up an internal DNS server that needs to resolve external domains for your clients, you would configure forwarders.

```
  forwarders {
                217.218.155.155; [cite: 7]
                217.218.127.127; 
  };

  forward only; 
```
The 

**`forwarders`** block lists the IP addresses of the public DNS servers you want to forward queries to.

The 

**`forward only`**; directive tells your server to only use the forwarders and not to try performing recursion on its own if the forwarders do not respond.

### Defining a Master Zone
To tell BIND that it is the main, authoritative server for a domain, you must define a master zone.

Example Configuration
Here is the configuration for a master zone based on your class notes:
```
zone "itpolicy.ir" IN {
        type master; 
        file "itpolicy.ir.db"; 
        allow-update { none; }; 
        allow-query { any; }; 
};
```


**`zone "itpolicy.ir" IN { ... }`**: This line declares the start of a configuration block for the domain "itpolicy.ir".

**`type master;`**: This defines the server's role for this zone as the master (or primary). This means it holds the original, editable copy of the zone's data.


**`file "itpolicy.ir.db";`**: This specifies the name of the zone file that contains all the DNS records for this domain. This file is usually located in BIND's working directory, such as 

/var/named/.

**`allow-update { none; };`**: This is a security directive that controls Dynamic DNS (DDNS). Setting it to 

none disables automatic updates to the zone file, meaning all changes must be made manually by the system administrator.

**`allow-query { any; };`**: This specifies who is allowed to ask this server questions about the itpolicy.ir zone. The value any makes the zone information publicly accessible.

### Defining a Slave Zone (Example)
A slave server provides redundancy and load balancing. Its configuration is similar, but its type is different, and it must know the master's IP address. The following is a standard example of how a slave zone would be configured.
```
zone "itpolicy.ir" IN {
        type slave;
        file "slaves/itpolicy.ir.db";
        masters { 92.114.19.118; };
};
```

**`zone "itpolicy.ir" IN { ... }`**: The zone name is identical to the master's zone.

**`type slave;`**: This defines the server's role as a slave (or secondary). This means it will get its zone data from another server.

**`file "slaves/itpolicy.ir.db";`**: This specifies where the server should save the copy of the zone file it downloads. It is good practice to store slave zone files in a separate subdirectory.

**`masters { 92.114.19.118; };`**: This is the most important line for a slave zone. It tells the slave server the IP address of the master server from which it should request the zone information. In this case, it will request the data for itpolicy.ir from the server at 92.114.19.118


## A Complete Zone File Example
The Zone File: /var/named/itpolicy.ir.db
Here is a complete example of what the zone file for itpolicy.ir could look like.

DNS Zone file
```

; Sets a Default Time-To-Live for the entire zone
$TTL 1h

; Start of Authority (SOA) Record
@   IN  SOA ns1.itpolicy.ir. kheirkhah.itpolicy.ir. (
        7               ; Serial Number
        1800            ; Refresh Interval (30 minutes)
        900             ; Retry Interval (15 minutes)
        2W              ; Expire Time (2 weeks)
        600             ; Minimum TTL / Negative Caching TTL (10 minutes)
)

; Name Server (NS) Records
@   IN  NS  ns1.itpolicy.ir.
@   IN  NS  ns2.itpolicy.ir.
@   IN  NS  ns3.itpolicy.ir.

; Glue Records for Name Servers
ns1 IN  A   92.114.19.118
ns2 IN  A   185.147.163.55
ns3 IN  A   94.182.178.235

; Mail Exchanger (MX) Records
@   IN  MX  10  mail.itpolicy.ir.
@   IN  MX  15  mail2.itpolicy.ir.

; A Records for Mail Servers
mail    IN  A   1.0.0.5
mail2   IN  A   1.0.0.6

; Host and Application Records
; A record for the main domain (apex)
@       IN  A       1.0.0.2

; Web server that hosts the main site
srv2    IN  A       1.0.0.2
        IN  AAAA    2001:db8::2 ; IPv6 address for srv2

; CNAME record for www to point to the main web server
www     IN  CNAME   srv2.itpolicy.ir.

; Another host in the network
Asbeabi IN  A       6.6.6.6

; Service (SRV) Record for a SIP service
_sip._tcp   IN  SRV 10 60 5060 srv2.itpolicy.ir.

; Policy and Security (TXT) Records
; SPF record to prevent email spoofing
@       IN  TXT "v=spf1 mx -all"
```
### The $TTL Directive
**`$TTL 1h`**: This directive sets a default TTL (Time-To-Live) for the entire zone file. Any record that does not have its own specific TTL will use this value (1 hour). This is a modern best practice.

### The SOA Record
**`@ IN SOA ...`**: The Start of Authority record is the most important record. It defines the primary properties of the zone.

**`@`**: A shortcut that means the domain name itself (itpolicy.ir).

**`ns1.itpolicy.ir.`**: The primary Master Name Server for this zone.

**`kheirkhah.itpolicy.ir.`**: The email address of the zone administrator (the @ symbol is replaced with a dot).

**`7 (Serial)`**: The version number of the zone file. You must increase this number every time you make a change.

**`1800 (Refresh)`**: How often slave servers should check for a new version (in seconds).

**`900 (Retry)`**: How long a slave server should wait before trying to contact the master again if the first attempt fails.

**`2W (Expire)`**: If a slave server cannot contact the master for this long (2 weeks), it will stop considering its data valid.

**`600 (Minimum TTL)`**: Used as the TTL for negative caching (how long other servers remember that a record does not exist).

### Name Server (NS) and Glue Records
**`@ IN NS ...`**: These three lines declare the official Name Servers for the itpolicy.ir domain.

**`ns1 IN A ...`**: These are the Glue Records. They provide the IP addresses for the name servers themselves, which is necessary to prevent circular lookups.

### Mail Exchanger (MX) Records
**`@ IN MX ...`**: These records specify which servers are responsible for receiving email for the itpolicy.ir domain.

**`10 and 15`**: These are priority numbers. Mail will first be sent to the server with the lowest priority (mail.itpolicy.ir.). If that server is unavailable, it will try the next one (mail2.itpolicy.ir.).

**`mail IN A ...`**: These are the standard A records that provide the IP addresses for the mail servers listed in the MX records.

### Host and Application Records
**`@ IN A 1.0.0.2`**: This important record maps the main domain name (itpolicy.ir, without www) to an IP address. This allows users to reach your site by typing just itpolicy.ir.

**`srv2 IN A ... and IN AAAA ...`**: These records define the main web server, srv2.itpolicy.ir. It has both an IPv4 (A) and an IPv6 (AAAA) address.

**`www IN CNAME srv2.itpolicy.ir.`**: This is an alias. It makes www.itpolicy.ir point to the actual server name, srv2.itpolicy.ir. This is useful because if you ever change the IP of your web server, you only need to update the records for srv2, and the www alias will automatically follow.

**`Asbeabi IN A ...`**: This is a simple A record for another host on the network.

### Service (SRV) Record
**`_sip._tcp IN SRV ...`**: This record is used to locate a specific service. This example says that the SIP service over the TCP protocol can be found on port 5060 at the target host srv2.itpolicy.ir.. The numbers 10 (priority) and 60 (weight) are used for selecting between multiple servers providing the same service.

### Policy and Security (TXT) Records
**`@ IN TXT "v=spf1 mx -all"`**: This is an example of a TXT record used for a security policy. This specific line is an SPF (Sender Policy Framework) record. It helps prevent email spoofing by declaring that only the servers listed in this domain's MX records are allowed to send email on behalf of itpolicy.ir

## BIND Configuration Validation Tools
Before restarting the BIND service after making changes, it is a critical best practice to validate your configuration files to prevent errors and downtime.
```
named-checkconf
```

This command is used to check the main BIND configuration file (/etc/named.conf) for syntax errors. It checks for issues like missing semicolons (;), incorrect brackets ({}), or misspelled keywords. It does not check if your zone files are correct; it only checks the main configuration file's structure. If the command produces no output, it means the file syntax is correct.

```
named-checkzone
```

This command is used to check a specific zone file for correctness and integrity. It checks the syntax of all resource records within the file to ensure they are valid.

Command Example:
```
named-checkzone itpolicy.ir /var/named/itpolicy.ir.db 
```

## Zone Transfer Mechanisms
A zone transfer is the process a slave DNS server uses to copy the zone records from its master server to keep its own copy up-to-date.

### AXFR (All Zone Transfer)
This stands for All Zone Transfer. An AXFR is a request from a slave server to a master server to send the 

entire copy of the zone file. This typically happens the first time a slave connects to a master or if the slave's data has become too old and out of sync.

### IXFR (Incremental Zone Transfer)
This stands for Incremental Zone Transfer. An IXFR is a more efficient method where a slave server requests 

only the changes that have been made to the zone since its last update. The server compares its own serial number with the master's serial number to determine which records need to be transferred. This saves bandwidth and is much faster than a full transfer.

## The notify Mechanism

Notify is a feature where a master server proactively informs its slave servers immediately after its zone file has been updated. When the master sends a 

notify message, the slave servers know to immediately request a zone transfer (usually an IXFR), rather than waiting for their scheduled Refresh Interval to expire. This ensures that changes are replicated across all servers very quickly.

## The SRV (Service) Record
The SRV record is a type of DNS Resource Record used to locate a specific network service on a domain. It is more detailed than an A or MX record, as it specifies not only the hostname but also the port number, priority, and weight for a service.

### Structure of an SRV Record
An SRV record contains the following components:


**`Service`**: Specifies the service the record is for (e.g., _ldap, _kerberos). It always starts with an underscore.


**`Protocol`**: Specifies the protocol used (e.g., _tcp, _udp).


**`Priority`**: Determines the preference of the server (a lower number is better and will be tried first).


**`Weight`**: Used for load balancing when multiple servers have the same priority (a higher weight is better and receives more traffic).


**`Port`**: The port number the service listens on (e.g., 389 for LDAP, 88 for Kerberos).


**`Target`**: The hostname of the server providing the service


## Reverse Lookup Zones
A Reverse Lookup Zone is a special type of DNS zone used to perform a reverse name lookup. Its function is to map an IP address back to its corresponding FQDN (Fully Qualified Domain Name). This is the opposite of a forward lookup, which maps an FQDN to an IP address.

### Why Are Reverse Zones Used?
While forward lookups are essential for everyday internet use like Browse websites, reverse lookups are primarily used for verification, security, and logging. Key use cases include:

**`Email Server Verification`**: Many mail servers are configured to reject emails from an IP address that does not have a valid reverse DNS record (a PTR record). This helps to verify the sender's identity and combat spam.

**`Network Troubleshooting`**: Reverse lookups help administrators identify which device is using a specific IP address on their network.

**`Logging`**: Logs are much easier for humans to read when they contain hostnames instead of just IP addresses (e.g., webserver01.itpolicy.ir is more informative than 192.168.0.3).

### Difference Between Forward and Reverse Lookup Zones
| Forward Lookup Zone                        | Reverse Lookup Zone                                |
|-------------------------------------------|----------------------------------------------------|
| **Question:** What is the IP address for www.itpolicy.ir? | **Question:** What is the hostname for the IP address 192.168.0.3? |
| **Mapping:** FQDN → IP                    | **Mapping:** IP → FQDN                             |
| **Main Record Type:** A or AAAA           | **Main Record Type:** PTR                          |


### Creating the Reverse Zone Name
Reverse lookup zones for IPv4 use a special domain called in-addr.arpa. To create the zone name, you must take the network portion of your IP address range and reverse the order of the octets.

Example: To create a reverse zone for the 192.168.0.0/24 network:

1. Take the network portion: 192.168.0

2. Reverse the octets: 0.168.192

3. Append the .in-addr.arpa suffix.

4. Resulting Zone Name: 0.168.192.in-addr.arpa 

### Configuration in named.conf
You define a reverse zone in /etc/named.conf just like a forward zone, but using the special reversed name.

```
zone "0.168.192.in-addr.arpa" IN {
        type master;
        file "0.168.192.in-addr.arpa";
        allow-update { none; };
        allow-transfer { none; };
};
```

This block tells BIND that it is the master server for the reverse zone corresponding to the 

192.168.0.0/24 network and that the records are located in the file named 0.168.192.in-addr.arpa.

### The Reverse Zone File
The reverse zone file is where the actual IP-to-hostname mappings are defined using PTR (Pointer) records.

Example Zone File: /var/named/0.168.192.in-addr.arpa
```
@       IN      SOA     ns1.itpolicy.ir. kheirkhah.gmail.com. (
        1;
        1800;
        900;
        3W;
        300;
)
[cite: 30]

@       IN      NS      ns1.itpolicy.ir. [cite: 31]

; PTR Records
1       IN      PTR     pc1.alaki.com. [cite: 32]
2       IN      PTR     ct.tehran.ir. [cite: 33]
3       IN      PTR     www.itpolicy.ir. [cite: 34]
4       IN      PTR     mail.mftplus.com. [cite: 35]
5       IN      PTR     pc6.ahwaz.net. [cite: 36]
6       IN      PTR     mail.yahoo.net. [cite: 37]

```
# Chapter 3: Web Servers and Apache (httpd)
## Definition of a Web Server
A web server is a software program that runs on a server and its primary function is to process incoming network requests from clients over the HTTP (Hypertext Transfer Protocol) and HTTPS (HTTP Secure) protocols. It acts as the intermediary between the server's files and the client's web browser. When a client requests a resource, such as an HTML page or an image, the web server locates that resource and sends it back to the client.

Well-known web server software includes 

Apache, Nginx, IIS (Microsoft's Internet Information Services), and Tomcat.

### Why Web Servers Are Used
A web server is used to publish a website and make it accessible to users on the internet. Without a web server, a website would just be a collection of files on a computer, with no way for anyone else to access them. The web server listens for requests 24/7, retrieves the requested files (like HTML, CSS, JavaScript, and images), and delivers them to the user's browser, allowing the website to be viewed.

### Static vs. Dynamic Content
**`Static Content`**: This refers to any content that is delivered to the user's browser exactly as it is stored on the server. The content does not change based on user interaction. Examples include HTML files, CSS files, JavaScript files, and images.

**`Dynamic Content`**: This refers to content that is generated on-the-fly by the server before being sent to the user. This often involves scripting languages (like PHP) and database interaction. The content can be personalized for each user, such as a shopping cart or a user profile page.

### Apache (httpd) Initial Setup
This section covers the basic installation and initial configuration of the Apache HTTP Server, which is provided by the httpd package on Red Hat-based systems.

Installation and Service Management
The first step is to install the software package and ensure the service is running and enabled to start on boot.

```
# Install the httpd package
dnf install httpd -y

# Check the status of the service
systemctl status httpd.service

# Start the service for the current session
systemctl start httpd

# Enable the service to start automatically on boot
systemctl enable httpd
```

### Firewall Configuration
For the web server to be accessible from the internet, you must allow HTTP traffic through the system's firewall.
```
# Add a permanent rule to allow the standard http service (port 80)
firewall-cmd --add-service=http --permanent

# Reload the firewall to apply the new rule immediately
firewall-cmd --reload
```


### Disabling the Default Welcome Page
By default, Apache displays a welcome page. It is a best practice to disable this page before configuring your own websites.
```
mv /etc/httpd/conf.d/welcome.conf /etc/httpd/conf.d/welcome
```


Explanation: Apache loads all configuration files in the /etc/httpd/conf.d/ directory that end with the .conf extension. By renaming the file, we remove this extension, which prevents Apache from loading it and displaying the default page.

## Introduction to Virtual Hosting
Definition of Virtual Hosting
Virtual Hosting is a feature of Apache that allows a single server to host multiple, independent websites. Even though these websites are running on the same machine, they appear as separate sites to the end-user. This is the core technology that makes shared web hosting possible.

### Methods of Separating Sites
There are three primary methods Apache can use to differentiate between the websites it is hosting:

**`IP-Based Virtual Hosting`**: In this method, each website has its own unique IP address. When a request comes in, Apache uses the destination IP address of the request to determine which website to serve.

**`Port-Based Virtual Hosting`**: In this method, multiple websites share the same IP address, but each website listens on a different port number. For example, http://example.com:80 could serve one site, while http://example.com:8080 serves another.

**`Name-Based (FQDN) Virtual Hosting`**: This is the most common and efficient method. Multiple websites share the same IP address and port (usually port 80 for HTTP). Apache uses the hostname provided by the client in the Host Header of the HTTP request to determine which website to serve.

## Practical Apache Configuration

### Changing the Default Listening Port
To configure Apache to listen on a port other than the default of 80, you need to edit the main Apache configuration file.

The Listen directive specifies the ports that Apache will bind to. You can add new Listen directives to make Apache listen on multiple ports simultaneously.

```
File to Edit: /etc/httpd/conf/httpd.conf 
```

Directive to Add/Modify: To make Apache listen on port 8080, you would add the following line to the configuration file:
```
Apache

Listen 8080
```

After adding this line and configuring a virtual host for that port, you must also open the new port in the firewall (
```
firewall-cmd --add-port=8080/tcp --permanent) 
```
and restart the httpd service. 

## Step-by-Step Guide: Setting Up a Name-Based Virtual Host
This guide details the complete process for hosting a website, www.itpolicy.ir, using the name-based virtual hosting method.

### Step 1: Create the Virtual Host Configuration File
First, you need to create a new configuration file specifically for your new website inside the /etc/httpd/conf.d/ directory. Keeping each site in its own file is a best practice for organization.

```
sudo vim /etc/httpd/conf.d/itpolicy.ir.conf
```

### Step 2: Add the Virtual Host Configuration
Next, add the following content to the new file. This block of directives tells Apache how to handle requests for www.itpolicy.ir.
```
<VirtualHost 92.114.19.118:80>
    ServerName www.itpolicy.ir
    ServerAlias itpolicy.ir
    DocumentRoot /var/www/itpolicy_ir
    DirectoryIndex index.html
</VirtualHost>
```

Directive Explanations:

**`<VirtualHost 92.114.19.118:80>`**: Defines a virtual host that listens on the specific IP 92.114.19.118 and port 80.

**`ServerName www.itpolicy.ir`**: This is the primary domain name for this website. It's the most important directive for name-based hosting.

**`ServerAlias itpolicy.ir`**: Specifies any other names that this site should respond to, such as the domain without the www.

**`DocumentRoot /var/www/itpolicy_ir`**: This is the path to the directory where the website's files (HTML, CSS, images) are stored.

**`DirectoryIndex index.html`**: Specifies the default file to serve when a user accesses a directory.

### Step 3: Create the Website's Directory and Content
Now, you must create the directory that you specified as the DocumentRoot and place your website's files inside it.

```
# Create the document root directory
sudo mkdir -p /var/www/itpolicy_ir/

# Create a simple index file for testing
sudo vim /var/www/itpolicy_ir/index.html
```


You should add some basic HTML content to the index.html file, for example: hello world

### Step 4: Apply the New Apache Configuration
For the changes to take effect, you must restart the Apache service. This forces it to re-read its configuration files, including the new itpolicy.ir.conf file you created.
```
sudo systemctl restart httpd
```

### Step 5: Configure the DNS Record
The final and crucial step is to ensure that your domain name points to your web server's IP address. This is done in your domain's DNS zone file. You must add A records to map the hostname to the IP address specified in your <VirtualHost> block.
```
www           60      IN      A       92.114.19.118
itpolicy.ir.          IN      A       92.114.19.118
```

## Apache User Directories (UserDir)

The User Directory feature (enabled by the mod_userdir module) allows each user on the Linux system to host a personal website in a specific subdirectory within their own home directory. This is a convenient way to provide personal web space for multiple users on a single server, often used in educational or development environments.

When enabled, a user's site is typically accessible via a URL like http://your-server-ip/~username.

### Step 1: Configure the userdir.conf File
You must first enable the feature in its dedicated configuration file.
```
sudo vim /etc/httpd/conf.d/userdir.conf 
```
Configuration Changes:


* Line 17: Find the line UserDir disabled and change it to UserDir enabled. 


* Line 24: Ensure the line UserDir public_html is present and not commented out.  This tells Apache that the web content for each user is located in a directory named public_html inside their home directory.

### Step 2: Create a User and Their Web Directory
Next, create a system user and the public_html directory for them.
```
# Create a new system user named 'pouria'
sudo useradd pouria

# Create the public_html directory inside their home directory
sudo mkdir -p /home/pouria/public_html 
```

### Step 3: Set Correct Permissions (Critical Step)
The Apache process (which runs as the apache user) needs permission to access the user's home directory and read the files inside public_html. Incorrect permissions are the most common cause of "403 Forbidden" errors.
```
sudo chmod -R 755 /home/pouria 
```

* Explanation: This command sets the permissions for the user's home directory to 755 (read and execute for everyone), which allows the Apache service to enter the directory and serve its content.

### Step 4: Create Content
Create a simple test page inside the user's web directory.
```
sudo vim /home/pouria/public_html/index.html 
```
* Content: Add some basic HTML, for example: <h1>Pouria's Home Page</h1>.

### Step 5: Apply Changes
Finally, restart Apache to apply the new configuration.
```
sudo systemctl restart httpd 
```

Your user's personal site should now be accessible.

## Basic Authentication
Basic Authentication is a simple and straightforward method to password-protect a specific website or directory on your server. When a user tries to access the protected area, their browser will display a pop-up dialog asking for a username and password. This is useful for restricting access to administrative areas or private content.

* Note: Basic Authentication is not encrypted over a standard HTTP connection and should always be used with HTTPS to be secure.

### Step 1: Create a Password File with htpasswd
This utility is used to create and manage the file that stores the usernames and encrypted passwords.
```
# Create a NEW password file and add the first user 'kheirkhah'
sudo htpasswd -c /etc/httpd/conf/.htpasswd kheirkhah

# Add a SECOND user 'pouria' to the EXISTING file
sudo htpasswd /etc/httpd/conf/.htpasswd pouria
```

Explanation:

**`htpasswd`**: The command-line tool.

**`-c`**: The create flag. IMPORTANT: Only use this flag for the very first user. Using it again will overwrite the file and delete all existing users.

**`/etc/httpd/conf/.htpasswd`**: The path where the password file will be stored.

**`kheirkhah / pouria`**: The usernames. You will be prompted to enter a password for each user.

### Step 2: Configure Apache to Protect a Directory
Now, you must tell Apache which directory to protect and where to find the password file. This is done by adding a Directory block to your site's virtual host configuration file.
```
sudo vim /etc/httpd/conf.d/kheirkhah.conf 
```

Configuration to Add:
```
<Directory /var/www/kheirkhah>
    AuthType Basic
    AuthName "Basic Authentication"
    AuthUserFile /etc/httpd/conf/.htpasswd
    require valid-user
</Directory>
```

Directive Explanations:

**`<Directory /var/www/kheirkhah>`**: Specifies that these rules apply only to the /var/www/kheirkhah directory.

**`AuthType Basic`**: Sets the authentication method to "Basic".

**`AuthName "Basic Authentication"`**: This is the text that will appear in the login prompt of the browser.

**`AuthUserFile /etc/httpd/conf/.htpasswd`**: Tells Apache the exact path to the password file you created in Step 1.

**`require valid-user`**: This is the authorization rule. It means that any user who is listed in the AuthUserFile is allowed to access the directory after successfully entering their password.

### Step 3: Apply Changes
Restart Apache for the new security rules to take effect.
```
sudo systemctl restart httpd 
```

Now, when you try to access the site hosted in /var/www/kheirkhah, you will be prompted for a username and password.


# Securing Apache with SSL/TLS (HTTPS)
This chapter explains how to encrypt the communication between your web server and your users' browsers.

## Section 1: Understanding the Concepts of SSL/TLS
The Problem: HTTP is Not Secure
By default, the web uses the HTTP protocol.

http -> Clear Text -> sniff: All data sent over HTTP is in clear text, meaning it is not encrypted. Anyone on the network between the client and the server can intercept (or sniff) this traffic and read everything, including usernames, passwords, and other sensitive information.

### The Solution: HTTPS
To solve this, we use HTTPS (HTTP Secure), which uses the SSL/TLS protocol to create a secure connection.

https -> encrypt -> decrypt: With HTTPS, all data is encrypted at the source (e.g., the user's browser) and can only be decrypted by the intended destination (the web server).

### Asymmetric Keys
This encryption is made possible by an Asymmetric Pair Key. This is a pair of mathematically linked keys generated by the server:

**`Public Key`**: This key is shared publicly with anyone who connects to the server. It can be used to encrypt data, but it cannot be used to decrypt it.

**`Private Key`**: This key is kept secret and secure on the server. It is the only key that can decrypt data that was encrypted with its corresponding public key.

### The Role of a Certificate Authority (CA)
A browser needs to trust that the public key it received actually belongs to the correct website. This trust is established by a Certificate Authority (CA).

**`CA Server`**: A trusted third-party organization that verifies a website's identity.

**`CSR (Certificate Signing Request)`**: To get a certificate, the server administrator generates a CSR. This is a file containing the server's public key and identity information (like its domain name).

**`The Process`**: The CSR is sent to the CA. The CA verifies that you own the domain, then uses its own private key to digitally "sign" your CSR. The result is a trusted SSL certificate that you can install on your server.

## Section 2: Method 1 - The Automated Way with Let's Encrypt
Let's Encrypt is a free and trusted CA. The certbot tool automates the entire process of getting and installing a Let's Encrypt certificate on Apache.

### Step 1: Prepare the System
First, you need the EPEL repository, which contains the certbot package.
```
sudo dnf install epel-release -y
sudo dnf update -y
```

### Step 2: Install Certbot
Install certbot and the specific plugin for Apache.
```
sudo dnf install certbot mod_ssl python3-certbot-apache -y
```
**`certbot`**: The main tool.

**`mod_ssl`**: The Apache module required for SSL.

**`python3-certbot-apache`**: The plugin that allows certbot to automatically configure Apache.

### Step 3: Obtain and Install the Certificate
Run the certbot command with the Apache plugin and specify your domains.
```
sudo certbot --apache -d www.itpolicy.ir -d itpolicy.ir
```

certbot will automatically handle the verification process and modify your Apache configuration files to install the certificate and enable HTTPS.

### Step 4: Update the Firewall
You must allow HTTPS traffic (which uses port 443) through your firewall.
```
sudo firewall-cmd --add-service=https --permanent
sudo firewall-cmd --reload
```

## Section 3: Method 2 - The Manual Way with OpenSSL
This method is used for creating your own certificates for testing (Self-Signed) or for generating a CSR for a commercial CA.

### A) Creating and Installing a Self-Signed Certificate
A Self-Signed Certificate is a certificate signed by your own private key instead of a trusted CA. Browsers will show a security warning for these certificates, so they should only be used for internal testing or development.

#### Step 1: Generate the Self-Signed Certificate and Private Key
This single openssl command creates both the private key and the certificate.
```
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/pki/tls/private/k1.key -out /etc/pki/tls/certs/c1.crt
```

This command will create a new 2048-bit RSA private key (k1.key) and a certificate (c1.crt) that is valid for 365 days.

#### Step 2: Configure Apache to Use the Certificate
You need to configure two virtual hosts: one to redirect HTTP to HTTPS, and one to serve the HTTPS site.
```
vim /etc/httpd/conf.d/kheirkhah11.conf
```
Configuration:
```
# This virtual host redirects all HTTP traffic to HTTPS
<VirtualHost 92.114.19.118:80>
    DocumentRoot /var/www/kheirkhah
    DirectoryIndex index.html

    RewriteEngine On
    RewriteCond %{HTTPS} !=on
    RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
</VirtualHost>

# This virtual host serves the site over HTTPS on port 443
<VirtualHost *:443>
    DocumentRoot /var/www/kheirkhah
    DirectoryIndex index.html

    # Enable the SSL Engine
    SSLEngine on

    # Path to the certificate and key files
    SSLCertificateKeyFile /etc/pki/tls/private/k1.key
    SSLCertificateFile /etc/pki/tls/certs/c1.crt
</VirtualHost>
```
### B) Generating a CSR for a Commercial CA
If you buy a certificate from a commercial CA, you first need to generate a private key and a CSR.

#### Step 1: Generate the Private Key and CSR
```
sudo openssl req -newkey rsa:2048 -keyout mftplus_ir.key -out mftplus_ir.csr -nodes
```
This command will create two files:

**`mftplus_ir.key`**: Your new private key. Keep this secret!

**`mftplus_ir.csr`**: Your Certificate Signing Request. You will copy the content of this file and give it to the CA.

#### Step 2: Install the Certificate from the CA
Once the CA has verified your identity and sent you the certificate files, you will configure them in your Apache virtual host for port 443. This often includes an "intermediate" certificate provided by the CA.

Example Directives:
```
SSLCertificateFile      /etc/ssl/ssl.crt/mftplus2026.ir.crt
SSLCertificateKeyFile   /etc/ssl/ssl.key/mftplus2026_ir.key
SSLCertificateChainFile /etc/ssl/ssl.key/Intermediate2026.cer
```



