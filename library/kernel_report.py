#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Mary Provencher <mprovenc@redhat.com>
# SPDX-License-Identifier: GPL-2.0-or-later
#
""" Generate kernel settings facts for a system """

import os
import re
import subprocess as sp
from ansible.module_utils.basic import AnsibleModule

UNSTABLE_SYSCTL_FIELDS = ['kernel\.hostname', 'kernel\.domainname', 'dev', 'kernel\.ns_last_pid', 'net\.netfilter\.nf_conntrack_events', 'vm\.drop_caches']
UNSTABLE_SYSFS_FIELDS = ['kernel\.debug', 'devices']
SYSCTL_DIR = '/proc/sys'
SYSFS_DIR = '/sys'

def file_get_contents(filename):
    with open(filename) as f:
        return f.read().rstrip()

def settings_walk(dir, unstable):
    result = []
    combined_unstable = "(" + ")|(".join(unstable) + ")"
    for dirpath, dirs, files in os.walk(dir):
        if files:
            for file in files:
                setting_path = dirpath + "/" + file
                if(int(oct(os.stat(setting_path).st_mode)[-3:]) >= 644):
                    formatted_setting = str(setting_path[len(dir)+1:]).replace("/",".")
                    if re.match(combined_unstable,formatted_setting) is None:
                        try:
                            val = file_get_contents(setting_path)
                            if val:
                                result.append({'name': formatted_setting, "value": val})
                        except OSError as e:
                            # read errors occur on some of the 'stable_secret' files
                            pass
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

    # result['ansible_facts'] = {"sysctl":settings_walk(SYSCTL_DIR, UNSTABLE_SYSCTL_FIELDS)}
    result['ansible_facts'] = {"sysctl":settings_walk(SYSCTL_DIR, UNSTABLE_SYSCTL_FIELDS), "sysfs":settings_walk(SYSFS_DIR, UNSTABLE_SYSFS_FIELDS)}

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()