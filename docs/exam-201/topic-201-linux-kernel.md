# Topic 201: Linux Kernel

Objectives: 201.1, 201.2, and 201.3

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

Configuration interfaces and targets include config, menuconfig, xconfig, gconfig, oldconfig, and olddefconfig.

Build targets named by the objectives include all, zImage, bzImage, modules, modules_install, rpm-pkg, binrpm-pkg, and deb-pkg.

Typical build flow:

~~~bash
make menuconfig
make -j"$(nproc)"
sudo make modules_install
sudo make install
~~~

Then create or verify the initramfs and bootloader entry. Commands differ:

~~~bash
sudo dracut --force /boot/initramfs-custom.img KERNEL_VERSION
sudo update-initramfs -c -k KERNEL_VERSION
sudo update-grub
sudo grub2-mkconfig -o /boot/grub2/grub.cfg
~~~

Do not run every distribution-specific command. Choose the commands for the installed system.

Kernel configuration is stored in .config. Module installation updates /lib/modules/kernel-version. depmod builds module dependency files.

### DKMS

DKMS automatically rebuilds external modules when a new kernel is installed.

~~~bash
dkms status
dkms autoinstall
~~~

Use DKMS for supported out-of-tree drivers. Do not treat an unsigned third-party module as trusted software.

## 201.3 Runtime management and troubleshooting

### Inspect modules

~~~bash
lsmod
modinfo module_name
modprobe --show-depends module_name
grep module_name /lib/modules/"$(uname -r)"/modules.dep
~~~

insmod loads one exact module file and does not resolve dependencies. modprobe uses module names, configuration, aliases, and dependencies.

~~~bash
sudo modprobe module_name
sudo modprobe -r module_name
sudo rmmod module_name
~~~

A busy module cannot normally be unloaded. Find users, mounted filesystems, interfaces, or dependent modules before removal.

Persistent settings belong in /etc/modprobe.d/*.conf:

~~~text
alias labnet dummy
options module_name parameter=value
blacklist unwanted_module
~~~

Rebuild initramfs if an early-boot module policy changes.

### Hardware and kernel messages

~~~bash
dmesg --level=err,warn
lspci -k
lsusb
udevadm info /sys/class/net/eth0
udevadm monitor --kernel --udev --property
~~~

udev rules live under /etc/udev/rules.d/. Vendor rules are normally under /usr/lib/udev/rules.d/. Local rules should use a high number such as 90-lab.rules.

Test a rule before depending on it:

~~~bash
sudo udevadm control --reload
sudo udevadm test /sys/class/net/eth0
~~~

### sysctl

sysctl changes runtime kernel parameters.

~~~bash
sysctl net.ipv4.ip_forward
sudo sysctl -w net.ipv4.ip_forward=1
sudo sysctl --system
~~~

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
