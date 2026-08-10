# Topic 201: Linux Kernel

Objectives: 201.1, 201.2, and 201.3

<!-- BEGIN BEGINNER FOUNDATION -->
## Learn the idea before running commands

### What the kernel is

The Linux kernel is the privileged core of the operating system. Applications run in user space and request protected work through system calls. The kernel schedules processes, manages virtual memory, controls devices, implements networking, and provides filesystem access. A distribution combines this kernel with user-space tools, libraries, services, and a package manager.

A kernel image contains built-in code. Other features can be loaded as **modules** when needed. A module is kernel code, usually a device driver or protocol feature, that can be inserted and removed without rebuilding the complete kernel. The running kernel and its modules must be compatible.

### Important locations

- /boot stores kernel images, initramfs images, and bootloader data.
- /lib/modules/RELEASE stores modules for one kernel release.
- /proc exposes live kernel and process information as a virtual filesystem.
- /sys exposes devices, drivers, and kernel objects.
- /etc/modprobe.d stores persistent module options and blacklist rules.
- /proc/sys exposes tunable kernel parameters; persistent settings normally belong in /etc/sysctl.conf or /etc/sysctl.d/.

### Built-in code, modules, and parameters

Built-in code is always present after boot. A module is loaded only when requested directly or when device discovery finds a matching alias. The lsmod command shows loaded modules, modinfo describes a module, and modprobe loads a module together with its dependencies. The insmod command inserts one file directly and does not resolve dependencies, so modprobe is normally safer.

Kernel parameters supplied by the bootloader affect early startup. Runtime sysctl values affect a running kernel. Module parameters affect a particular module. These mechanisms are related but not interchangeable.

### Safe workflow

1. Record the running kernel release and architecture.
2. Confirm whether the needed feature is built in or provided as a module.
3. Read the distribution documentation before replacing a packaged kernel.
4. Keep a known-working kernel and boot entry.
5. Validate bootloader configuration and initramfs after changes.
6. Reboot only with console or recovery access available.
7. Verify the new kernel, modules, hardware, and logs after boot.

Building a kernel is an exam skill, but production systems normally prefer signed distribution packages because they receive security maintenance and integrate with the boot process.
<!-- END BEGINNER FOUNDATION -->

The kernel manages CPU time, memory, devices, filesystems, networking, and system calls. A kernel module adds a feature without rebuilding the complete kernel.

## 201.1 Kernel components

Common locations:

- /usr/src/linux/ or /usr/src/linux-version/: kernel source
- /boot/: kernel images, initramfs files, and bootloader data
- /lib/modules/kernel-version/: modules for one kernel
- /proc/: runtime kernel and process information
- /sys/: devices, drivers, and kernel objects

zImage and bzImage are compressed kernel image formats. bzImage means big zImage; it does not mean bzip2 compression. Modern kernel packages commonly use an image named vmlinuz.

~~~bash
uname -a
uname -r
ls -l /boot
find /lib/modules/"$(uname -r)" -maxdepth 2 -type f | head
~~~

<!-- LINE-BY-LINE 1 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>uname -a</code> | Prints kernel release, architecture, or other system identity data. |
| 2 | <code>uname -r</code> | Prints kernel release, architecture, or other system identity data. |
| 3 | <code>ls -l /boot</code> | Lists the requested files and metadata. |
| 4 | <code>find /lib/modules/"$(uname -r)" -maxdepth 2 -type f \| head</code> | Selects matching files or directories and runs the requested safe action on them. The pipe sends standard output from the command on the left to standard input of the command on the right. |

Stable and long-term kernels receive maintenance for different periods. Distribution kernels may include backported fixes, so a lower version number does not automatically mean an unpatched system.

## 201.2 Compile a Linux kernel

Compiling a kernel is a lab activity. Keep a known-good kernel installed and confirm console access.

### Preparation

~~~bash
cd /usr/src/linux
make mrproper
cp /boot/config-"$(uname -r)" .config
make oldconfig
~~~

<!-- LINE-BY-LINE 2 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>cd /usr/src/linux</code> | Changes the shell's working directory. |
| 2 | <code>make mrproper</code> | Runs a target from the project's Makefile, such as compilation, installation, or cleanup. |
| 3 | <code>cp /boot/config-"$(uname -r)" .config</code> | Copies the named file; the shown use preserves a backup or creates a working copy. |
| 4 | <code>make oldconfig</code> | Runs a target from the project's Makefile, such as compilation, installation, or cleanup. |

Configuration interfaces and targets include config, menuconfig, xconfig, gconfig, oldconfig, and olddefconfig.

Build targets named by the objectives include all, zImage, bzImage, modules, modules_install, rpm-pkg, binrpm-pkg, and deb-pkg.

Typical build flow:

~~~bash
make menuconfig
make -j"$(nproc)"
sudo make modules_install
sudo make install
~~~

<!-- LINE-BY-LINE 3 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>make menuconfig</code> | Runs a target from the project's Makefile, such as compilation, installation, or cleanup. |
| 2 | <code>make -j"$(nproc)"</code> | Runs a target from the project's Makefile, such as compilation, installation, or cleanup. |
| 3 | <code>sudo make modules_install</code> | sudo requests administrator privileges for this operation. Runs a target from the project's Makefile, such as compilation, installation, or cleanup. |
| 4 | <code>sudo make install</code> | sudo requests administrator privileges for this operation. Runs a target from the project's Makefile, such as compilation, installation, or cleanup. |

Then create or verify the initramfs and bootloader entry. Commands differ:

~~~bash
sudo dracut --force /boot/initramfs-custom.img KERNEL_VERSION
sudo update-initramfs -c -k KERNEL_VERSION
sudo update-grub
sudo grub2-mkconfig -o /boot/grub2/grub.cfg
~~~

<!-- LINE-BY-LINE 4 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo dracut --force /boot/initramfs-custom.img KERNEL_VERSION</code> | sudo requests administrator privileges for this operation. Builds or inspects an initramfs image on distributions that use dracut. |
| 2 | <code>sudo update-initramfs -c -k KERNEL_VERSION</code> | sudo requests administrator privileges for this operation. Creates or updates initramfs images on Debian-family systems. |
| 3 | <code>sudo update-grub</code> | sudo requests administrator privileges for this operation. Regenerates the GRUB menu through the Debian-family wrapper. |
| 4 | <code>sudo grub2-mkconfig -o /boot/grub2/grub.cfg</code> | sudo requests administrator privileges for this operation. Generates a GRUB 2 configuration from supported source files. |

Do not run every distribution-specific command. Choose the commands for the installed system.

Kernel configuration is stored in .config. Module installation updates /lib/modules/kernel-version. depmod builds module dependency files.

### DKMS

DKMS automatically rebuilds external modules when a new kernel is installed.

~~~bash
dkms status
dkms autoinstall
~~~

<!-- LINE-BY-LINE 5 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>dkms status</code> | Builds and manages external modules for installed kernel releases. |
| 2 | <code>dkms autoinstall</code> | Builds and manages external modules for installed kernel releases. |

Use DKMS for supported out-of-tree drivers. Do not treat an unsigned third-party module as trusted software.

## 201.3 Runtime management and troubleshooting

### Inspect modules

~~~bash
lsmod
modinfo module_name
modprobe --show-depends module_name
grep module_name /lib/modules/"$(uname -r)"/modules.dep
~~~

<!-- LINE-BY-LINE 6 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>lsmod</code> | Lists modules currently loaded into the kernel. |
| 2 | <code>modinfo module_name</code> | Shows a module's metadata, aliases, dependencies, and parameters. |
| 3 | <code>modprobe --show-depends module_name</code> | Loads or removes a module while resolving dependencies. |
| 4 | <code>grep module_name /lib/modules/"$(uname -r)"/modules.dep</code> | Selects lines that match the requested text or expression. |

insmod loads one exact module file and does not resolve dependencies. modprobe uses module names, configuration, aliases, and dependencies.

~~~bash
sudo modprobe module_name
sudo modprobe -r module_name
sudo rmmod module_name
~~~

<!-- LINE-BY-LINE 7 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo modprobe module_name</code> | sudo requests administrator privileges for this operation. Loads or removes a module while resolving dependencies. |
| 2 | <code>sudo modprobe -r module_name</code> | sudo requests administrator privileges for this operation. Loads or removes a module while resolving dependencies. |
| 3 | <code>sudo rmmod module_name</code> | sudo requests administrator privileges for this operation. Removes a module only when nothing is using it. |

A busy module cannot normally be unloaded. Find users, mounted filesystems, interfaces, or dependent modules before removal.

Persistent settings belong in /etc/modprobe.d/*.conf:

~~~text
alias labnet dummy
options module_name parameter=value
blacklist unwanted_module
~~~

<!-- LINE-BY-LINE 8 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>alias labnet dummy</code> | Creates a modprobe alias so the first name requests the module named after it. |
| 2 | <code>options module_name parameter=value</code> | Assigns the shown parameter value whenever modprobe loads this module. |
| 3 | <code>blacklist unwanted_module</code> | Stops automatic loading through normal modprobe alias resolution; it is not an absolute security boundary. |

Rebuild initramfs if an early-boot module policy changes.

### Hardware and kernel messages

~~~bash
dmesg --level=err,warn
lspci -k
lsusb
udevadm info /sys/class/net/eth0
udevadm monitor --kernel --udev --property
~~~

<!-- LINE-BY-LINE 9 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>dmesg --level=err,warn</code> | Displays messages from the kernel ring buffer. |
| 2 | <code>lspci -k</code> | Lists PCI devices; -k also shows the kernel driver and candidate modules for each device. |
| 3 | <code>lsusb</code> | Lists USB buses and attached USB devices. |
| 4 | <code>udevadm info /sys/class/net/eth0</code> | Queries device properties or controls and tests udev event processing. |
| 5 | <code>udevadm monitor --kernel --udev --property</code> | Queries device properties or controls and tests udev event processing. |

udev rules live under /etc/udev/rules.d/. Vendor rules are normally under /usr/lib/udev/rules.d/. Local rules should use a high number such as 90-lab.rules.

Test a rule before depending on it:

~~~bash
sudo udevadm control --reload
sudo udevadm test /sys/class/net/eth0
~~~

<!-- LINE-BY-LINE 10 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sudo udevadm control --reload</code> | sudo requests administrator privileges for this operation. Queries device properties or controls and tests udev event processing. |
| 2 | <code>sudo udevadm test /sys/class/net/eth0</code> | sudo requests administrator privileges for this operation. Queries device properties or controls and tests udev event processing. |

### sysctl

sysctl changes runtime kernel parameters.

~~~bash
sysctl net.ipv4.ip_forward
sudo sysctl -w net.ipv4.ip_forward=1
sudo sysctl --system
~~~

<!-- LINE-BY-LINE 11 -->
**Line-by-line explanation**

| Line | Command or configuration | What it does |
|---:|---|---|
| 1 | <code>sysctl net.ipv4.ip_forward</code> | Reads or changes a live kernel parameter under /proc/sys. |
| 2 | <code>sudo sysctl -w net.ipv4.ip_forward=1</code> | sudo requests administrator privileges for this operation. Reads or changes a live kernel parameter under /proc/sys. |
| 3 | <code>sudo sysctl --system</code> | sudo requests administrator privileges for this operation. Reads or changes a live kernel parameter under /proc/sys. |

Persistent settings belong in /etc/sysctl.conf or /etc/sysctl.d/*.conf. Do not enable forwarding without firewall and routing design.

### Boot failure after a new kernel

1. Choose the previous kernel from GRUB.
2. Read journal and dmesg.
3. Confirm the matching /lib/modules directory exists.
4. Confirm initramfs contains the required storage and filesystem drivers.
5. Check DKMS status and module signatures.
6. Correct the configuration before removing the known-good kernel.

## Exam command checklist

make and its kernel targets, gzip, bzip2, xz, mkinitrd, mkinitramfs, dracut, depmod, dkms, rmmod, modinfo, dmesg, lspci, lsdev, lsmod, modprobe, insmod, uname, lsusb, sysctl, udevadm, /proc/sys/kernel/, /etc/udev/, and /etc/sysctl.d/.

## Mini lab

Create a test VM snapshot. Load the dummy network module, inspect it, create a modprobe alias, read its sysfs object, monitor udev events, and unload it. Do not compile or replace the host kernel outside a disposable VM.
