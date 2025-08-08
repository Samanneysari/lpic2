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