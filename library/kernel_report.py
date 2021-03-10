#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Mary Provencher <mprovenc@redhat.com>
# SPDX-License-Identifier: GPL-2.0-or-later
#
""" Generate kernel settings facts for a system """

import subprocess as sp
from ansible.module_utils.basic import AnsibleModule

def add_dict_level(dct, lvls, val):
    """
    Function that recursively adds levels to a dictionary. Takes an existing dictionary, a list of nested levels,
    and a value to be assigned to the deepest level.
    """
    key = lvls[0].rstrip()
    if len(lvls) == 1:
        dct[key] = val.lstrip()
    else:
        dct[key] = add_dict_level(dct[key] if key in dct else {}, lvls[1:], val)
    return dct

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

    procfs_output = sp.run(['sh', 'utils/sysctlwalk.sh'], stdout=sp.PIPE).stdout.decode("utf-8")[:-2]
    facts_as_dict = dict()

    for substring in procfs_output.split('\n'):
        keyval = substring.split('=')
        facts_as_dict = add_dict_level(facts_as_dict, keyval[0].split('/')[1:], keyval[1])

    result['ansible_facts'] = facts_as_dict

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()