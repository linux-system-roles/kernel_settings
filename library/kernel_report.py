#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Mary Provencher <mprovenc@redhat.com>
# SPDX-License-Identifier: GPL-2.0-or-later
#
""" Generate kernel settings facts for a system """

import re
import pyudev
from ansible.module_utils.basic import AnsibleModule

UNSTABLE_SYSCTL_FIELDS = ['kernel\.hostname', 'kernel\.domainname', 'dev', 'kernel\.ns_last_pid', 'net\.netfilter\.nf_conntrack_events', 'vm\.drop_caches']
UNSTABLE_SYSFS_FIELDS = ['kernel\.debug', 'devices']
SYSCTL_DIR = '/proc/sys'
SYSFS_DIR = '/sys'

def safe_file_get_contents(filename):
    try:
        with open(filename) as f:
            return f.read().rstrip()
    except FileNotFoundError as e:
        print('safe_file_get_contents: suppressed exception FileNotFoundError with content \'%s\'' %  e)

def get_sysfs_fields():
    result = {}
    result["kernel_settings_transparent_hugepages"] = re.findall(r'\[(\w+)\]', safe_file_get_contents('/sys/kernel/mm/transparent_hugepage/enabled'))[0]
    result["kernel_settings_transparent_hugepages_defrag"] = re.findall(r'\[(\w+)\]', safe_file_get_contents('/sys/kernel/mm/transparent_hugepage/defrag'))[0]

    # will collect a list of cpus associated to the template machine, but only use settings from the first one
    cpus = pyudev.Context().list_devices(subsystem="cpu")
    num_cpus = 0
    
    for cpu in cpus:
        num_cpus += 1
        if 'kernel_settings_cpu_governor' not in result:
            result["kernel_settings_cpu_governor"] = safe_file_get_contents('%s/cpufreq/scaling_governor' % cpu.sys_path)
            result["kernel_settings_sampling_down_factor"] = safe_file_get_contents('/sys/devices/system/cpu/cpufreq/%s/sampling_down_factor' % result['kernel_settings_cpu_governor'])
    
    print("get_sysfs_fields: found %d cpus associated to the template machine" % num_cpus)

    result["kernel_settings_cpu_min_perf_pct"] = safe_file_get_contents("/sys/devices/system/cpu/intel_pstate/min_perf_pct")
    result["kernel_settings_cpu_max_perf_pct"] = safe_file_get_contents("/sys/devices/system/cpu/intel_pstate/max_perf_pct")
    result["kernel_settings_cpu_no_turbo"] = safe_file_get_contents("/sys/devices/system/cpu/intel_pstate/no_turbo")

    # will collect a list of blocks associated to the template machine, but only use settings from the first one
    blocks = pyudev.Context().list_devices(subsystem="block")
    num_blocks = 0

    for block in blocks:
        num_blocks += 1
        if 'kernel_settings_disk_elevator' not in result:
            result["kernel_settings_disk_elevator"] = re.findall(r'\[(\w+)\]', safe_file_get_contents("%s/queue/scheduler" % block.sys_path))[0]
            result["kernel_settings_disk_read_ahead_kb"] = int(safe_file_get_contents("%s/queue/read_ahead_kb" % block.sys_path))
            result["kernel_settings_disk_scheduler_quantum"] = safe_file_get_contents("%s/queue/iosched/quantum" % block.sys_path)
    
    print("get_sysfs_fields: found %d blocks associated to the template machine" % num_blocks)

    result["kernel_settings_avc_cache_threshold"] = int(safe_file_get_contents("/sys/fs/selinux/avc/cache_threshold"))
    result["kernel_settings_nf_conntrack_hashsize"] = int(safe_file_get_contents("/sys/module/nf_conntrack/parameters/hashsize"))
    
    # will collect a list of modules associated to the template machine, but only use settings from the first one
    num_modules = 0
    devices = pyudev.Context().list_devices(subsystem="sound").match_sys_name("card*")

    for device in devices:
        module_name = device.parent.driver
        if module_name in ["snd_hda_intel", "snd_ac97_codec"]:
            num_modules += 1
            result["kernel_settings_audio_timeout"] = safe_file_get_contents("/sys/module/%s/parameters/power_save" % module_name)
            result["kernel_settings_audio_reset_controller"] = safe_file_get_contents("/sys/module/%s/parameters/power_save_controller" % module_name)

    print("get_sysfs_fields: found %d sound modules associated to the template machine" % num_modules)

    # will collect a list of scsis associated to the template machine, but only use settings from the first one
    num_scsis = 0
    scsis = pyudev.Context().list_devices(subsystem="scsi")

    for scsi in scsis:
        num_scsis += 1
        if "kernel_settings_scsi_host_alpm" not in result:
            result["kernel_settings_scsi_host_alpm"] = safe_file_get_contents("%s/link_power_management_policy" % scsi.sys_path)

    print("get_sysfs_fields: found %d scsis associated to the template machine" % num_scsis)

    # will collect a list of graphics cards associated to the template machine, but only use settings from the first one
    num_gcards = 0
    gcards = pyudev.Context().list_devices(subsystem="drm").match_sys_name("card*").match_property("DEVTYPE", "drm_minor")

    for gcard in gcards:
        num_gcards += 1
        method = safe_file_get_contents("%s/device/power_method" % gcard.sys_path)
        if "kernel_settings_video_radeon_powersave" not in result:
            if method == "profile":
                result["kernel_settings_video_radeon_powersave"] = safe_file_get_contents("%s/device/power_profile" % gcard.sys_path)
            elif method == "dynpm":
                result["kernel_settings_video_radeon_powersave"] = "dynpm"
            elif method == "dpm":
                result["kernel_settings_video_radeon_powersave"] = "dpm-%s" % safe_file_get_contents("%s/device/power_dpm_state" % gcard.sys_path)
    
    print("get_sysfs_fields: found %d gcards associated to the template machine" % num_gcards)

    # will collect a list of usb interfaces associated to the template machine, but only use settings from the first one
    num_usbs = 0
    usbs = pyudev.Context().list_devices(subsystem="usb")

    for usb in usbs:
        num_usbs += 1
        if "kernel_settings_usb_autosuspend" not in result:
            result["kernel_settings_usb_autosuspend"] = int(safe_file_get_contents("%s/power/autosuspend" % usb.sys_path))

    print("get_sysfs_fields: found %d usbs associated to the template machine" % num_usbs)

    other_sysfs = []
    ksm_dict = {"name": "/sys/kernel/mm/ksm/run"}
    ksm_dict["value"] = safe_file_get_contents("/sys/kernel/mm/ksm/run")
    other_sysfs.append(ksm_dict)

    ktimer_dict = {"name": "/sys/kernel/ktimer_lockless_check"}
    ktimer_dict["value"] = safe_file_get_contents("/sys/kernel/ktimer_lockless_check")
    other_sysfs.append(ktimer_dict)

    result["kernel_settings_sysfs"] = other_sysfs

    return result

def run_module():
    module_args = dict()

    result = dict(
        changed=False,
        ansible_facts=dict(),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    result['ansible_facts'] = get_sysfs_fields()

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()