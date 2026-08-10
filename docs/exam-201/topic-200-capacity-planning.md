# Topic 200: Capacity Planning

Objectives: 200.1 and 200.2

<!-- BEGIN BEGINNER FOUNDATION -->
## Learn the idea before running commands

### What capacity planning means

Capacity planning is the practice of measuring how a system uses CPU time, memory, storage, and network resources, then deciding whether the system can handle its present and future workload. It is not the same as guessing that a server needs more RAM. A good administrator first collects evidence, finds the resource that is limiting the workload, and changes only what the evidence supports.

Performance problems are usually about one of four things:

- **Utilization:** how much of a resource is busy.
- **Saturation:** how much work is waiting because a resource is busy.
- **Errors:** failed operations, dropped packets, or hardware problems.
- **Latency:** how long an operation takes to finish.

A server can show low CPU utilization and still be slow because processes are waiting for disk, NFS, DNS, a database, or a remote API. Linux load average is therefore not a CPU percentage. It includes tasks ready to run and tasks blocked in uninterruptible sleep.

### A simple mental model

A process needs CPU time to execute, memory to keep its working data, storage to read or write persistent data, and the network to communicate. If any layer becomes slow, the layers above it may wait. For example, an Apache process can appear idle while it waits for a database response.

Memory also needs careful interpretation. Linux intentionally uses otherwise free RAM for page cache. The "available" value is generally more useful than the "free" value. Swap being used is not automatically a fault; continuous swap-in and swap-out activity is the stronger sign of memory pressure.

### The correct troubleshooting order

1. Write down the exact symptom and the time it happened.
2. Reproduce it safely if possible.
3. Compare current values with a normal baseline for the same server.
4. Decide whether CPU, memory, storage, network, or an external dependency is limiting progress.
5. Identify the affected process and inspect its logs and open resources.
6. Change one item only.
7. Measure again and keep the before-and-after evidence.

Capacity forecasting uses repeated samples, not one snapshot. Record peak use, normal use, growth rate, retention, and a safety margin. The goal is a concrete decision such as expanding a filesystem, changing log retention, adding a worker, or scheduling a hardware upgrade.
<!-- END BEGINNER FOUNDATION -->

Capacity planning answers two questions:

1. Why is the system slow now?
2. When will the current resources stop being enough?

Always measure before changing a configuration.

## 200.1 Measure and troubleshoot resource usage

### Start with a baseline

A single high value is not always a problem. Compare current data with the normal behavior of the same server.

~~~bash
uptime
w
free -h
df -h
df -i
ps aux --sort=-%cpu | head
ps aux --sort=-%mem | head
~~~

<!-- LINE-BY-LINE 1 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>uptime</code> | Shows uptime, logged-in user count, and 1, 5, and 15 minute load averages. |
| 2 | <code>w</code> | Shows logged-in users and the processes they are running. |
| 3 | <code>free -h</code> | Reports RAM and swap use; human-readable output is requested where shown. |
| 4 | <code>df -h</code> | Reports filesystem space or inode use for the selected filesystems. |
| 5 | <code>df -i</code> | Reports filesystem space or inode use for the selected filesystems. |
| 6 | <code>ps aux --sort=-%cpu \| head</code> | Prints a process snapshot with the requested columns and sorting. The pipe sends standard output from the command on the left to standard input of the command on the right. |
| 7 | <code>ps aux --sort=-%mem \| head</code> | Prints a process snapshot with the requested columns and sorting. The pipe sends standard output from the command on the left to standard input of the command on the right. |

Load average is not CPU percentage. It counts runnable tasks and tasks blocked in uninterruptible sleep, commonly disk I/O.

### CPU and memory tools

| Tool | Main use |
|---|---|
| top, htop | Live CPU, memory, load, and processes |
| ps, pstree | Process snapshots and parent-child relationships |
| vmstat | CPU states, memory, paging, processes, and block I/O |
| sar | Historical CPU, memory, disk, and network statistics |
| uptime, w | Load average and logged-in users |
| lsof | Open files, devices, and sockets |

~~~bash
vmstat 1 10
sar -u 1 10
sar -r 1 10
pidstat 1
lsof -p PID
~~~

<!-- LINE-BY-LINE 2 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>vmstat 1 10</code> | Samples runnable tasks, memory, paging, block I/O, and CPU states. |
| 2 | <code>sar -u 1 10</code> | Reads or samples system-activity history collected by sysstat. |
| 3 | <code>sar -r 1 10</code> | Reads or samples system-activity history collected by sysstat. |
| 4 | <code>pidstat 1</code> | Reports CPU, memory, or I/O use for individual processes. |
| 5 | <code>lsof -p PID</code> | Lists open files, devices, and sockets held by processes. |

Important vmstat fields:

- r: tasks waiting for CPU
- b: tasks blocked on I/O
- si and so: swap input and output
- bi and bo: blocks read and written
- us, sy, id, wa: user, system, idle, and I/O wait CPU time

Constant swap traffic is more important than swap merely being used.

### Disk I/O

~~~bash
iostat -xz 1 10
iotop -oPa
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
~~~

<!-- LINE-BY-LINE 3 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>iostat -xz 1 10</code> | Reports CPU and block-device throughput, utilization, queue, and latency statistics. |
| 2 | <code>iotop -oPa</code> | Shows which processes are generating storage I/O. |
| 3 | <code>lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS</code> | Displays block devices and their parent-child relationships. |

Look for high latency, a consistently busy device, blocked processes, or one process causing most I/O. Device utilization must be interpreted with device type and workload; an NVMe device and a rotating disk behave differently.

### Network and socket usage

~~~bash
ip -s link
ss -s
ss -lntup
sar -n DEV 1 10
lsof -i
tcpdump -ni any host 10.20.0.25
~~~

<!-- LINE-BY-LINE 4 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>ip -s link</code> | Inspects or changes interfaces, addresses, neighbors, routes, and virtual links in the running kernel. |
| 2 | <code>ss -s</code> | Displays listening or connected sockets and summary counters. |
| 3 | <code>ss -lntup</code> | Displays listening or connected sockets and summary counters. |
| 4 | <code>sar -n DEV 1 10</code> | Reads or samples system-activity history collected by sysstat. |
| 5 | <code>lsof -i</code> | Lists open files, devices, and sockets held by processes. |
| 6 | <code>tcpdump -ni any host 10.20.0.25</code> | Captures packets on the selected interface using the shown filter; captures can contain sensitive data. |

The exam may mention netstat and iptraf. Modern systems normally use ss and iproute2, but know both names.

Map client usage with interface counters, firewall counters, flow monitoring, proxy logs, or application logs. Check both bandwidth and packet rate.

~~~bash
sudo iptables -L -n -v
sudo ip6tables -L -n -v
sudo nft list ruleset
~~~

<!-- LINE-BY-LINE 5 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo iptables -L -n -v</code> | sudo requests administrator privileges for this operation. Inspects or changes the legacy IPv4 netfilter rules. |
| 2 | <code>sudo ip6tables -L -n -v</code> | sudo requests administrator privileges for this operation. Inspects or changes the legacy IPv6 netfilter rules. |
| 3 | <code>sudo nft list ruleset</code> | sudo requests administrator privileges for this operation. Inspects or changes the nftables ruleset. |

### Correlate symptoms

| Symptom | Likely checks |
|---|---|
| High load, low CPU use | Disk I/O, blocked tasks, NFS, locks |
| High system CPU | Interrupts, drivers, firewall, many system calls |
| Slow application, normal host | Application logs, database, DNS, remote dependency |
| Memory almost full | Check available memory and cache before assuming failure |
| Swap activity | Working set larger than RAM or memory pressure |
| Packet loss | Interface errors, duplex, congestion, MTU, firewall |
| Disk full | df -h, df -i, deleted open files with lsof +L1 |

A useful troubleshooting order is: reproduce, record time, measure, isolate a resource, identify the process, inspect logs, change one item, and measure again.

## 200.2 Predict future resource needs

Collect the same metrics at regular intervals. A graph is more useful than isolated command output.

Examples of monitoring systems named by the objectives include Icinga 2, Nagios, collectd, MRTG, and Cacti.

Track:

- CPU utilization and load
- available memory and swap activity
- filesystem space and inode use
- disk latency and throughput
- network throughput, errors, and drops
- application response time
- request, user, and job counts

### Simple growth calculation

If a filesystem grows by 3 GB per day and has 90 GB free, the simple breakpoint is 30 days. Real growth may be seasonal, so keep a safety margin.

~~~bash
date
df -P /srv
sar -u
sar -n DEV
~~~

<!-- LINE-BY-LINE 6 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>date</code> | Prints the current date and time so measurements can be correlated. |
| 2 | <code>df -P /srv</code> | Reports filesystem space or inode use for the selected filesystems. |
| 3 | <code>sar -u</code> | Reads or samples system-activity history collected by sysstat. |
| 4 | <code>sar -n DEV</code> | Reads or samples system-activity history collected by sysstat. |

Document the sample interval, retention period, expected peak, warning threshold, and emergency threshold. Capacity work should produce a decision such as adding storage, tuning retention, scaling out, or scheduling an upgrade.

## Exam command checklist

iostat, iotop, vmstat, netstat, ss, iptraf, pstree, ps, w, lsof, top, htop, uptime, sar, swap, blocked processes, blocks in, and blocks out.

## Mini lab

1. Start a controlled CPU or I/O workload in a test VM.
2. Observe it with top, vmstat, iostat, and pidstat.
3. Find the process with ps and lsof.
4. Save ten samples.
5. Write one paragraph explaining the bottleneck and one safe recommendation.
