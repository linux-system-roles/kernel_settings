#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Mary Provencher <mprovenc@redhat.com>
# SPDX-License-Identifier: GPL-2.0-or-later
#
""" Generate kernel settings facts for a system """

import os
import subprocess as sp
from ansible.module_utils.basic import AnsibleModule

UNSTABLE_SYSCTL_FIELDS = ('kernel.hostname', 'kernel.domainname', 'dev', 'kernel.ns_last_pid', 'net.netfilter.nf_conntrack_events')
SYSCTL_DIR = '/proc/sys'

def file_get_contents(filename):
    with open(filename) as f:
        return f.read().rstrip()

def sysctl_walk():
    result = []
    for dirpath, dirs, files in os.walk(SYSCTL_DIR):
        if files:
            for file in files:
                setting_path = dirpath + "/" + file
                if(int(oct(os.stat(setting_path).st_mode)[-3:]) >= 600):
                    formatted_setting = str(setting_path[10:]).replace("/",".")
                    if formatted_setting not in UNSTABLE_SYSCTL_FIELDS:
                        try:
                            val = file_get_contents(setting_path)
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

    result['ansible_facts'] = {"sysctl":sysctl_walk()}

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()