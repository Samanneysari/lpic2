# Topic 200: Capacity Planning

Objectives: 200.1 and 200.2

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

The exam may mention netstat and iptraf. Modern systems normally use ss and iproute2, but know both names.

Map client usage with interface counters, firewall counters, flow monitoring, proxy logs, or application logs. Check both bandwidth and packet rate.

~~~bash
sudo iptables -L -n -v
sudo ip6tables -L -n -v
sudo nft list ruleset
~~~

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

Document the sample interval, retention period, expected peak, warning threshold, and emergency threshold. Capacity work should produce a decision such as adding storage, tuning retention, scaling out, or scheduling an upgrade.

## Exam command checklist

iostat, iotop, vmstat, netstat, ss, iptraf, pstree, ps, w, lsof, top, htop, uptime, sar, swap, blocked processes, blocks in, and blocks out.

## Mini lab

1. Start a controlled CPU or I/O workload in a test VM.
2. Observe it with top, vmstat, iostat, and pidstat.
3. Find the process with ps and lsof.
4. Save ten samples.
5. Write one paragraph explaining the bottleneck and one safe recommendation.
