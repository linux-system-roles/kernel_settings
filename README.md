# Kernel Settings Role

This role is used to modify kernel settings.  For example, on Linux, settings
in `/proc/sys` (using `sysctl`), `/sys/fs`, bootloader command line, and some
other settings.  It uses `tuned` for its default provider on Enterprise Linux
and derivatives (RHEL and CentOS) and Fedora.

* `tuned` homepage - https://github.com/redhat-performance/tuned

## Requirements

This role requires an operating system which has the `tuned` package and
service (for the default `tuned` provider).

## Role Variables

The values for the various `kernel_settings_GROUP` parameters are a
`list` of `dict` objects.  Each `dict` has the following keys:
* `name` - Usually Required - The name the setting, or the name of a file
  under `/sys` for the `sysfs` group.  `name` is omitted when using
  `replaced`.
* `value` - Usually Required - The value for the setting.  `value` is omitted
  when using `state` or `replaced`.  Bootloader cmdline settings do not
  require a `value`.
* `state` - Optional - possible values:
  ** `absent` - to remove a setting with name `name` from a group - `name`
  must be provided
  ** `empty` - to completely remove a group, specify the value of a group as a
  `dict` instead of a `list` with the following value: `{"state":"empty"}`
* `previous` - Optional - the only value is `replaced` - this is used to
  specify that the previous values in a group should be replaced with the
  given values.

See below for examples.

`kernel_settings_sysctl` - A `list` of settings to be applied using `sysctl`.
The settings are given in the format described above.  Note that the settings
are *additive* - by default, each setting is added to the existing settings,
or replaces the setting of the same name if it already exists. If you want to
remove a specific setting, use `state: absent` instead of giving a `value`. If
you want to remove all of the existing `sysctl` settings and replace them with
the given settings, specify `previous: replaced` as one of the values in the
list.  If you want to remove all of the `sysctl` settings, use `state: empty`
as the only value for the parameter. See below for examples.

`kernel_settings_sysfs` - A `list` of settings to be applied to `/sys`. The
settings are given in the format described above.  Note that the settings are
*additive* - by default, each setting is added to the existing settings, or
replaces the setting of the same name if it already exists. If you want to
remove a specific setting, use `state: absent` instead of giving a `value`. If
you want to remove all of the existing `sysfs` settings and replace them with
the given settings, specify `previous: replaced` as one of the values in the
list.  If you want to remove all of the `sysfs` settings, use `state: empty`
as the only value for the parameter. See below for examples.

`kernel_settings_systemd_cpu_affinity` - A space delimited list of cpu numbers.
See https://www.freedesktop.org/software/systemd/man/systemd-system.conf.html#CPUAffinity=

`kernel_settings_systemd_cpu_affinity_state` - Set this to `absent` to remove
the setting `kernel_settings_systemd_cpu_affinity`, which will be reverted
back to the system default value upon reboot.

`kernel_settings_transparent_hugepages` - One of the following values:
`always` `madvise` `never`. This is the memory subsystem transparent hugepages
value.

`kernel_settings_transparent_hugepages_state` - Set this to `absent` to remove
the setting `kernel_settings_transparent_hugepages`, which will be reverted
back to the system default value upon reboot.

`kernel_settings_transparent_hugepages_defrag` - One of these values: `always`
`defer` `defer+madvise` `madvise` `never`. This is the memory subsystem
transparent hugepages fragmentation handling value.  The actual supported
values may be different depending on your OS.

`kernel_settings_transparent_hugepages_defrag_state` - Set this to `absent` to
remove the setting `kernel_settings_transparent_hugepages_defrag`, which will
be reverted back to the system default value upon reboot.

`kernel_settings_bootloader_cmdline` - A `list` of settings to be applied to
the bootloader command line.  The settings are given in the format described
above.  Note that the settings are *additive* - by default, each setting is
added to the existing settings, or replaces the setting of the same name if it
already exists.  Note that bootloader cmdline settings can be specified with
just a `name` and no `value`.  If you want to remove a specific setting, use
`state: absent` instead of giving a `value`. If you want to remove the
existing cmdline and replace it with the given settings, specify
`previous: replaced` as one of the values in the list.  If you want to remove
the cmdline, use `state: empty` as the only value for the parameter. See below
for examples.

`kernel_settings_purge` - default `false` - If `true`, then the existing
configuration will be completely wiped out and replaced with your given
`kernel_settings_GROUP` settings.

`kernel_settings_reboot_ok` - default `false` - If `true`, then if the role
detects that something was changed that requires a reboot to take effect, the
role will reboot the managed host.  If `false`, it is up to you to determine
when to reboot the managed host.  The role will return the variable
`kernel_settings_reboot_required` (see below) with a value of `true` to indicate
that some change has occurred which needs a reboot to take effect.

### Variables Exported by the Role

The role will export the following variables:

`kernel_settings_reboot_required` - default `false` - if `true`, this means a
change has occurred which will require rebooting the managed host in order to
take effect (e.g. bootloader cmdline settings).  If you want the role to
reboot the managed host, set `kernel_settings_reboot_ok: true`, otherwise, you
will need to handle rebooting the machine.

### Examples of Settings Usage

```yaml
kernel_settings_sysctl:
  - name: fs.epoll.max_user_watches
    value: 785592
  - name: fs.file-max
    value: 379724
kernel_settings_sysfs:
  - name: /sys/kernel/debug/x86/pti_enabled
    value: 0
  - name: /sys/kernel/debug/x86/retp_enabled
    value: 0
  - name: /sys/kernel/debug/x86/ibrs_enabled
    value: 0
kernel_settings_transparent_hugepages: madvise
kernel_settings_transparent_hugepages_defrag: defer
kernel_settings_bootloader_cmdline:
  - name: spectre_v2
    value: "off"
  - name: nopti
```
*NOTE* that the `list` valued settings are **additive**.  That is, they are
applied **in addition to** any current settings.  For example, if you already
had
```yaml
kernel_settings_sysctl:
  - name: kernel.threads-max
    value: 29968
  - name: vm.max_map_count
    value: 65530
```
then after applying the above, you would have
```yaml
kernel_settings_sysctl:
  - name: kernel.threads-max
    value: 29968
  - name: vm.max_map_count
    value: 65530
  - name: fs.epoll.max_user_watches
    value: 785592
  - name: fs.file-max
    value: 379724
```
This allows multiple higher level roles or playbooks to use this role to
provide the kernel settings specific to that component.  For example, if you
are installing a web server and a database server on the same machine, and
they both require setting kernel parameters, the `kernel_settings` role allows
you to set them both.

If you specify multiple settings with the same name in a section, the last
one will be used.

If you want to replace *all* of the settings in a section with your supplied
values, use `previous: replaced` as a single, preferably first element in the
list of settings.  This indicates that the `previous` settings in the system
should be `replaced` with the given settings.  For example:
```yaml
kernel_settings_sysctl:
  - previous: replaced
  - name: kernel.threads-max
    value: 30000
  - name: vm.max_map_count
    value: 50000
```
This will have the effect of removing all of the existing settings for
`sysctl`, and adding the specified settings.
If you want to remove a single setting, specify `state: absent` in the
individual setting, instead of a `value`:
```yaml
kernel_settings_sysctl:
  - name: kernel.threads-max
    value: 30000
  - name: vm.max_map_count
    state: absent
```
This will remove the `vm.max_map_count` setting from the `sysctl` section.
If you want to remove an entire section, specify `state: empty` as a `dict`
instead of a `list`:
```yaml
kernel_settings_sysctl:
  state: empty
```
This will have the effect of removing all of the `sysctl` settings.

The `bootloader` `cmdline` value is a list of values, and you can add or
remove specific values in the list.  By default, it will replace existing
values and add missing values.  Using:
```yaml
kernel_settings_bootloader_cmdline:
  - name: spectre_v2
    value: "off"
  - name: nopti
  - name: quiet
  - name: splash
```
will result in the values `spectre_v2=off nopti quiet splash` being added to,
or replacing, the existing `bootloader` `cmdline` values.  If you want to
remove whatever was there, and replace it with your specified values, use
`previous: replaced` in the value list:
```yaml
kernel_settings_bootloader_cmdline:
  - previous: replaced
  - name: spectre_v2
    value: "off"
  - name: nopti
  - name: quiet
  - name: splash
```
then the values `spectre_v2=off nopti quiet splash` will *replace* the
existing `cmdline` values, if any.  If you want to remove specific values, use
`state: absent` on the settings you want to remove:
```yaml
kernel_settings_bootloader_cmdline:
  - name: spectre_v2
    state: absent
  - name: nopti
    state: absent
```
if the previous value was `spectre_v2=off nopti quiet splash`, the items
`spectre_v2=off` and `nopti` will be removed from the list, and the final
value will be `quiet splash`.

## Dependencies

The `tuned` package is required for the default provider.

## Example Playbook

```yaml
- hosts: all
  vars:
    kernel_settings_sysctl:
      - name: fs.epoll.max_user_watches
        value: 785592
      - name: fs.file-max
        value: 379724
      - name: kernel.threads-max
        state: absent
    kernel_settings_sysfs:
      - name: /sys/kernel/debug/x86/pti_enabled
        value: 0
      - name: /sys/kernel/debug/x86/retp_enabled
        value: 0
      - name: /sys/kernel/debug/x86/ibrs_enabled
        value: 0
    kernel_settings_transparent_hugepages: madvise
    kernel_settings_transparent_hugepages_defrag: defer
    kernel_settings_bootloader_cmdline:
      - name: spectre_v2
        value: "off"
      - name: nopti
      - name: quiet
      - name: splash
  roles:
    - linux-system-roles.kernel_settings
```

## Warnings

The `kernel_settings` role will cause other `sysctl` settings to be applied
when using the `tuned` implementation, which is the default. For example, if
you manually edit `/etc/sysctl.d/` files, or if the `sysctl.d` files are
installed by some system package.  On Fedora, installing the `libreswan`
package provides `/etc/sysctl.d/50-libreswan.conf`.  Using the
`kernel_settings` role will cause this file to be reloaded and reapplied.  If
this behavior is not desired, you will need to edit the `tuned` configuration
on the managed hosts in `/etc/tuned/tuned-main.conf` and set
`reapply_sysctl=0`.

The settings you apply with the `kernel_settings` role may conflict with other
settings.  For example, if you manually run the `sysctl` command, or manually
edit `/etc/sysctl.d/` files, or if the `sysctl.d` files are installed by some
system package, they may set the same values you are setting with the
`kernel_settings` role.  For `sysctl` settings, the precedence goes like this:
* `sysctl` files have highest precedence - `/etc/sysctl.conf` and
  `/etc/sysctl.d/*` will override everything
* `kernel_settings` settings have the next highest precedence
* settings set manually using the `sysctl` command have the lowest precedence

For `bootloader` `cmdline` settings, the settings from `kernel_settings` will
generally take precedence over other bootloader settings.  If you set
bootloader cmdline configuration outside of the `kernel_settings` role, e.g.
using `grubby`, you should review your settings to make sure they do not
conflict.

For all other settings such as `sysfs`, the settings from `kernel_settings`
have the highest precedence.

## License

Some parts related to `tuned` are `GPLv2+`.  These are noted in the headers
of the files.  Everything else is `MIT`, except where noted.  See the file
`LICENSE` for more information.

## Author Information

Rich Megginson (richm on github, rmeggins at my company)
