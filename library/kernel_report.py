#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Mary Provencher <mprovenc@redhat.com>
# SPDX-License-Identifier: GPL-2.0-or-later
#
""" Generate kernel settings facts for a system """

import re
import pyudev
from ansible.module_utils.basic import AnsibleModule

SYSCTL_FIELDS = ['fs.aio-max-nr', 
                'fs.file-max', 
                'fs.inotify.max_user_watches', 
                'kernel.hung_task_timeout_secs',
                'kernel.nmi_watchdog',
                'kernel.numa_balancing',
                'kernel.panic_on_oops',
                'kernel.pid_max',
                'kernel.printk',
                'kernel.sched_autogroup_enabled',
                'kernel.sched_latency_ns',
                'kernel.sched_migration_cost_ns',
                'kernel.sched_min_granularity_ns',
                'kernel.sched_rt_runtime_us',
                'kernel.sched_wakeup_granularity_ns',
                'kernel.sem',
                'kernel.shmall',
                'kernel.shmmax',
                'kernel.shmmni',
                'kernel.timer_migration',
                'net.core.busy_poll',
                'net.core.busy_read',
                'net.core.rmem_default',
                'net.core.rmem_max',
                'net.core.wmem_default',
                'net.core.wmem_max',
                'net.ipv4.ip_local_port_range',
                'net.ipv4.tcp_fastopen',
                'net.ipv4.tcp_rmem',
                'net.ipv4.tcp_timestamps',
                'net.ipv4.tcp_window_scaling',
                'net.ipv4.tcp_wmem',
                'net.ipv4.udp_mem',
                'net.netfilter.nf_conntrack_max',
                'vm.dirty_background_bytes',
                'vm.dirty_background_ratio',
                'vm.dirty_bytes',
                'vm.dirty_expire_centisecs',
                'vm.dirty_ratio',
                'vm.dirty_writeback_centisecs',
                'vm.hugepages_treat_as_movable',
                'vm.laptop_mode',
                'vm.max_map_count',
                'vm.min_free_kbytes',
                'vm.stat_interval',
                'vm.swappiness',
                'vm.zone_reclaim_mode']


def safe_file_get_contents(filename):
    try:
        with open(filename) as f:
            return f.read().rstrip()
    except FileNotFoundError as e:
        print('safe_file_get_contents: suppressed exception FileNotFoundError with content \'%s\'' %  e)

def get_sysctl_fields():
    sysctl = []
    for setting in SYSCTL_FIELDS:
        temp_dict = {"name": setting}
        temp_dict["value"] = safe_file_get_contents("/proc/sys/%s" % setting.replace(".","/"))
        if temp_dict["value"]:
            if (setting == "vm.dirty_background_bytes" or setting == "vm.dirty_background_ratio" or setting == "vm.dirty_ratio" or setting == "vm.dirty_bytes") and temp_dict["value"] == "0":
                continue
            else:
                sysctl.append(temp_dict)

    return {"kernel_settings_sysctl": sysctl}

def get_sysfs_fields():
    result = {}

    # these are the settings not specific to any particular device
    result["kernel_settings_transparent_hugepages"] = re.findall(r'\[(\w+)\]', safe_file_get_contents('/sys/kernel/mm/transparent_hugepage/enabled'))[0]
    result["kernel_settings_transparent_hugepages_defrag"] = re.findall(r'\[(\w+)\]', safe_file_get_contents('/sys/kernel/mm/transparent_hugepage/defrag'))[0]
    result["kernel_settings_cpu_min_perf_pct"] = safe_file_get_contents("/sys/devices/system/cpu/intel_pstate/min_perf_pct")
    result["kernel_settings_cpu_max_perf_pct"] = safe_file_get_contents("/sys/devices/system/cpu/intel_pstate/max_perf_pct")
    result["kernel_settings_cpu_no_turbo"] = safe_file_get_contents("/sys/devices/system/cpu/intel_pstate/no_turbo")
    result["kernel_settings_avc_cache_threshold"] = safe_file_get_contents("/sys/fs/selinux/avc/cache_threshold")
    result["kernel_settings_nf_conntrack_hashsize"] = safe_file_get_contents("/sys/module/nf_conntrack/parameters/hashsize")

    kernel_settings_device_specific = {}

    # will collect a list of cpus associated to the template machine, but only use settings from the first one
    cpus = pyudev.Context().list_devices(subsystem="cpu")
    num_cpus = 0
    
    kernel_settings_device_specific["kernel_settings_cpu_governor"] = []
    kernel_settings_device_specific["kernel_settings_sampling_down_factor"] = []
    for cpu in cpus:
        num_cpus += 1
        kernel_settings_device_specific["kernel_settings_cpu_governor"].append({'device':cpu.sys_path, 'value':safe_file_get_contents('%s/cpufreq/scaling_governor' % cpu.sys_path)})
        kernel_settings_device_specific["kernel_settings_sampling_down_factor"].append({'device':cpu.sys_path, 'value':safe_file_get_contents('/sys/devices/system/cpu/cpufreq/%s/sampling_down_factor' % kernel_settings_device_specific['kernel_settings_cpu_governor'][-1])})
    
    print("get_sysfs_fields: found %d cpus associated to the template machine" % num_cpus)

    # will collect a list of blocks associated to the template machine, but only use settings from the first one
    blocks = pyudev.Context().list_devices(subsystem="block")
    num_blocks = 0

    kernel_settings_device_specific["kernel_settings_disk_elevator"] =[]
    kernel_settings_device_specific["kernel_settings_disk_read_ahead_kb"] = []
    kernel_settings_device_specific["kernel_settings_disk_scheduler_quantum"] = []

    for block in blocks:
        num_blocks += 1
        schedulers = safe_file_get_contents("%s/queue/scheduler" % block.sys_path)
        if schedulers:
            settings = re.findall(r'\[(\w+)\]', schedulers)
            if settings:
                kernel_settings_device_specific["kernel_settings_disk_elevator"].append({'device':block.sys_path, 'value':settings[0]})
            kernel_settings_device_specific["kernel_settings_disk_read_ahead_kb"].append({'device':block.sys_path, 'value':safe_file_get_contents("%s/queue/read_ahead_kb" % block.sys_path)})
            kernel_settings_device_specific["kernel_settings_disk_scheduler_quantum"].append({'device':block.sys_path, 'value':safe_file_get_contents("%s/queue/iosched/quantum" % block.sys_path)})
    
    print("get_sysfs_fields: found %d blocks associated to the template machine" % num_blocks)
    
    # will collect a list of sound cards associated to the template machine, but only use settings from the first one
    num_sound_cards = 0
    sound_cards = pyudev.Context().list_devices(subsystem="sound").match_sys_name("card*")

    kernel_settings_device_specific["kernel_settings_audio_timeout"] = []
    kernel_settings_device_specific["kernel_settings_audio_reset_controller"] = []

    for sound_card in sound_cards:
        module_name = sound_card.parent.driver
        if module_name in ["snd_hda_intel", "snd_ac97_codec"]:
            num_sound_cards += 1
            kernel_settings_device_specific["kernel_settings_audio_timeout"].append({'device':sound_card.sys_path, 'value':safe_file_get_contents("/sys/module/%s/parameters/power_save" % module_name)})
            kernel_settings_device_specific["kernel_settings_audio_reset_controller"].append({'device':sound_card.sys_path, 'value':safe_file_get_contents("/sys/module/%s/parameters/power_save_controller" % module_name)})

    print("get_sysfs_fields: found %d sound modules associated to the template machine" % num_sound_cards)

    # will collect a list of scsis associated to the template machine, but only use settings from the first one
    num_scsis = 0
    scsis = pyudev.Context().list_devices(subsystem="scsi")

    kernel_settings_device_specific["kernel_settings_scsi_host_alpm"] = []

    for scsi in scsis:
        num_scsis += 1
        kernel_settings_device_specific["kernel_settings_scsi_host_alpm"].append({'device':scsi.sys_path, 'value':safe_file_get_contents("%s/link_power_management_policy" % scsi.sys_path)}) 

    print("get_sysfs_fields: found %d scsis associated to the template machine" % num_scsis)

    # will collect a list of graphics cards associated to the template machine, but only use settings from the first one
    num_gcards = 0
    gcards = pyudev.Context().list_devices(subsystem="drm").match_sys_name("card*").match_property("DEVTYPE", "drm_minor")

    kernel_settings_device_specific["kernel_settings_video_radeon_powersave"] = []

    for gcard in gcards:
        num_gcards += 1
        method = safe_file_get_contents("%s/device/power_method" % gcard.sys_path)
        if method == "profile":
            kernel_settings_device_specific["kernel_settings_video_radeon_powersave"].append({'device':gcard.sys_path, 'value':safe_file_get_contents("%s/device/power_profile" % gcard.sys_path)}) 
        elif method == "dynpm":
            kernel_settings_device_specific["kernel_settings_video_radeon_powersave"].append({'device':gcard.sys_path, 'value':'dynpm'})
        elif method == "dpm":
            kernel_settings_device_specific["kernel_settings_video_radeon_powersave"].append({'device':gcard.sys_path, 'value':"dpm-%s" % safe_file_get_contents("%s/device/power_dpm_state" % gcard.sys_path)})

    print("get_sysfs_fields: found %d gcards associated to the template machine" % num_gcards)

    # will collect a list of usb interfaces associated to the template machine, but only use settings from the first one
    num_usbs = 0
    usbs = pyudev.Context().list_devices(subsystem="usb")

    kernel_settings_device_specific["kernel_settings_usb_autosuspend"] = []

    for usb in usbs:
        num_usbs += 1
        kernel_settings_device_specific["kernel_settings_usb_autosuspend"].append({'device':usb.sys_path,'value':safe_file_get_contents("%s/power/autosuspend" % usb.sys_path)})

    result["kernel_settings_device_specific"] = kernel_settings_device_specific

    print("get_sysfs_fields: found %d usbs associated to the template machine" % num_usbs)

    other_sysfs = []
    ksm_dict = {"name": "/sys/kernel/mm/ksm/run"}
    ksm_dict["value"] = safe_file_get_contents("/sys/kernel/mm/ksm/run")
    if ksm_dict["value"]:
        other_sysfs.append(ksm_dict)

    ktimer_dict = {"name": "/sys/kernel/ktimer_lockless_check"}
    ktimer_dict["value"] = safe_file_get_contents("/sys/kernel/ktimer_lockless_check")
    if ktimer_dict["value"]:
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

    result['ansible_facts'] = {**get_sysfs_fields(), **get_sysctl_fields()}

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()