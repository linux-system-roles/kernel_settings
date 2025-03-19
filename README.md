# Kernel Settings Role

[![ansible-lint.yml](https://github.com/linux-system-roles/kernel_settings/actions/workflows/ansible-lint.yml/badge.svg)](https://github.com/linux-system-roles/kernel_settings/actions/workflows/ansible-lint.yml) [![ansible-test.yml](https://github.com/linux-system-roles/kernel_settings/actions/workflows/ansible-test.yml/badge.svg)](https://github.com/linux-system-roles/kernel_settings/actions/workflows/ansible-test.yml) [![codeql.yml](https://github.com/linux-system-roles/kernel_settings/actions/workflows/codeql.yml/badge.svg)](https://github.com/linux-system-roles/kernel_settings/actions/workflows/codeql.yml) [![codespell.yml](https://github.com/linux-system-roles/kernel_settings/actions/workflows/codespell.yml/badge.svg)](https://github.com/linux-system-roles/kernel_settings/actions/workflows/codespell.yml) [![markdownlint.yml](https://github.com/linux-system-roles/kernel_settings/actions/workflows/markdownlint.yml/badge.svg)](https://github.com/linux-system-roles/kernel_settings/actions/workflows/markdownlint.yml) [![python-unit-test.yml](https://github.com/linux-system-roles/kernel_settings/actions/workflows/python-unit-test.yml/badge.svg)](https://github.com/linux-system-roles/kernel_settings/actions/workflows/python-unit-test.yml) [![shellcheck.yml](https://github.com/linux-system-roles/kernel_settings/actions/workflows/shellcheck.yml/badge.svg)](https://github.com/linux-system-roles/kernel_settings/actions/workflows/shellcheck.yml) [![tft.yml](https://github.com/linux-system-roles/kernel_settings/actions/workflows/tft.yml/badge.svg)](https://github.com/linux-system-roles/kernel_settings/actions/workflows/tft.yml) [![tft_citest_bad.yml](https://github.com/linux-system-roles/kernel_settings/actions/workflows/tft_citest_bad.yml/badge.svg)](https://github.com/linux-system-roles/kernel_settings/actions/workflows/tft_citest_bad.yml) [![woke.yml](https://github.com/linux-system-roles/kernel_settings/actions/workflows/woke.yml/badge.svg)](https://github.com/linux-system-roles/kernel_settings/actions/workflows/woke.yml)

This role is used to modify kernel settings.  For example, on Linux, settings
in `/proc/sys` (using `sysctl`), `/sys/fs`, and some other settings.  It uses
`tuned` for its default provider on Enterprise Linux and derivatives (RHEL and
CentOS) and Fedora.

* `tuned` homepage - <https://github.com/redhat-performance/tuned>

## Requirements

See below

### Collection requirements

If you want to manage `rpm-ostree` systems with this role, you will need to
install additional collections.  Please run the following command line to
install the collection.

```bash
ansible-galaxy collection install -vv -r meta/collection-requirements.yml
```

## Role Variables

The values for some of the various `kernel_settings_GROUP` parameters are a
`list` of `dict` objects.  Each `dict` has the following keys:

* `name` - Usually Required - The name the setting, or the name of a file
  under `/sys` for the `sysfs` group.  `name` is omitted when using
  `replaced`.
* `value` - Usually Required - The value for the setting.  `value` is omitted
  when using `state` or `previous`.  Values must not be [YAML bool
  type](https://yaml.org/type/bool.html). One situation where this might be a
  problem is using `value: on` or other YAML `bool` typed value.  You must
  quote these values, or otherwise pass them as a value of `str` type e.g.
  `value: "on"`.
* `state` - Optional - the value `absent` means to remove a setting with name
  `name` from a group - `name` must be provided
* `previous` - Optional - the only value is `replaced` - this is used to
  specify that the previous values in a group should be replaced with the
  given values.

### kernel_settings_sysctl

A `list` of settings to be applied using `sysctl`.
The settings are given in the format described above.  Note that the settings
are *additive* - by default, each setting is added to the existing settings, or
replaces the setting of the same name if it already exists. If you want to
remove a specific setting, use `state: absent` instead of giving a `value`. If
you want to remove all of the existing `sysctl` settings and replace them with
the given settings, specify `previous: replaced` as one of the values in the
list.  If you want to remove all of the `sysctl` settings, use the `dict` value
`{"state": "empty"}`, instead of a `list`, as the only value for the parameter.
See below for examples.

### kernel_settings_sysfs

A `list` of settings to be applied to `/sys`. The
settings are given in the format described above.  Note that the settings are
*additive* - by default, each setting is added to the existing settings, or
replaces the setting of the same name if it already exists. If you want to
remove a specific setting, use `state: absent` instead of giving a `value`. If
you want to remove all of the existing `sysfs` settings and replace them with
the given settings, specify `previous: replaced` as one of the values in the
list.  If you want to remove all of the `sysfs` settings, use the `dict` value
`{"state": "empty"}`, instead of a `list`, as the only value for the parameter.
See below for examples.

### kernel_settings_systemd_cpu_affinity

To set the value, specify a `string` in
the format specified by
<https://www.freedesktop.org/software/systemd/man/systemd-system.conf.html#CPUAffinity=>
If you want to remove the setting, use the `dict` value `{"state": "absent"}`,
instead of a `string`, as the value for the parameter.

### kernel_settings_transparent_hugepages

To set the value, specify one of the
following `string` values: `always` `madvise` `never`. This is the memory
subsystem transparent hugepages value.  If you want to remove the setting, use
the `dict` value `{"state": "absent"}`, instead of a `string`, as the value for
the parameter.

### kernel_settings_transparent_hugepages_defrag

To set the value, specify one
of the following `string` values: `always` `defer` `defer+madvise` `madvise`
`never`. This is the memory subsystem transparent hugepages fragmentation
handling value.  The actual supported values may be different depending on your
OS.  If you want to remove the setting, use the `dict` value
`{"state": "absent"}`, instead of a `string`, as the value for the parameter.

### kernel_settings_purge

default `false` - If `true`, then the existing
configuration will be completely wiped out and replaced with your given
`kernel_settings_GROUP` settings.

### kernel_settings_reboot_ok

default `false` - If `true`, then if the role
detects that something was changed that requires a reboot to take effect, the
role will reboot the managed host.  If `false`, it is up to you to determine
when to reboot the managed host.  The role will return the variable
`kernel_settings_reboot_required` (see below) with a value of `true` to indicate
that some change has occurred which needs a reboot to take effect.

### kernel_settings_transactional_update_reboot_ok

This variable is used to handle reboots required by transactional updates.
If a transactional update requires a reboot, the role will proceed with the
reboot if `kernel_settings_transactional_update_reboot_ok` is set to `true`. If set
to `false`, the role will notify the user that a reboot is required, allowing
for custom handling of the reboot requirement. If this variable is not set,
the role will fail to ensure the reboot requirement is not overlooked.

### Variables Exported by the Role

The role will export the following variables:

`kernel_settings_reboot_required` - default `false` - if `true`, this means a
change has occurred which will require rebooting the managed host in order to
take effect.  If you want the role to
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
kernel_settings_systemd_cpu_affinity: "1,3,5,7"
kernel_settings_transparent_hugepages: madvise
kernel_settings_transparent_hugepages_defrag: defer
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
`kernel_settings_sysctl`, and adding the specified settings.
If you want to remove a single setting, specify `state: absent` in the
individual setting, instead of a `value`:

```yaml
kernel_settings_sysctl:
  - name: kernel.threads-max
    value: 30000
  - name: vm.max_map_count
    state: absent
```

This will remove the `vm.max_map_count` setting from the
`kernel_settings_sysctl` settings. If you want to remove all of the settings
from a group, specify `state: empty` as a `dict` instead of a `list`:

```yaml
kernel_settings_sysctl:
  state: empty
```

This will have the effect of removing all of the `kernel_settings_sysctl`
settings.

Use `{"state":"absent"}` to remove a scalar valued parameter.  For example, to
remove all of `kernel_settings_systemd_cpu_affinity`,
`kernel_settings_transparent_hugepages`, and
`kernel_settings_transparent_hugepages_defrag` settings, use this:

```yaml
kernel_settings_systemd_cpu_affinity:
  state: absent
kernel_settings_transparent_hugepages:
  state: absent
kernel_settings_transparent_hugepages_defrag:
  state: absent
```

## Example Playbook

```yaml
- name: Manage kernel settings
  hosts: all
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
    kernel_settings_systemd_cpu_affinity: "1,3,5,7"
    kernel_settings_transparent_hugepages: madvise
    kernel_settings_transparent_hugepages_defrag: defer
  roles:
    - linux-system-roles.kernel_settings
```

## Warnings

The `kernel_settings` role will cause other `sysctl` settings to be applied when
using the `tuned` implementation, which is the default. This can happen when you
manually edit `/etc/sysctl.d/` files, or if the `sysctl.d` files are installed
by some system package.  For example, on Fedora, installing the `libreswan`
package provides `/etc/sysctl.d/50-libreswan.conf`.  Using the `kernel_settings`
role will cause this file to be reloaded and reapplied.  If this behavior is not
desired, you will need to edit the `tuned` configuration on the managed hosts in
`/etc/tuned/tuned-main.conf` and set `reapply_sysctl=0`.

The settings you apply with the `kernel_settings` role may conflict with other
settings.  For example, if you manually run the `sysctl` command, or manually
edit `/etc/sysctl.d/` files, or if the `sysctl.d` files are installed by some
system package, they may set the same values you are setting with the
`kernel_settings` role.  For `sysctl` settings, the precedence goes like this:

* `sysctl` files have highest precedence - `/etc/sysctl.conf` and
  `/etc/sysctl.d/*` will override everything
* `kernel_settings` role settings have the next highest precedence
* settings set manually using the `sysctl` command have the lowest precedence

For all other settings such as `sysfs`, the settings from `kernel_settings` role
have the highest precedence.

## rpm-ostree

See README-ostree.md

## License

Some parts related to `tuned` are `GPLv2+`.  These are noted in the headers
of the files.  Everything else is `MIT`, except where noted.  See the file
`LICENSE` for more information.

## Author Information

Rich Megginson (richm on github, rmeggins at my company)

test
