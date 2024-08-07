#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Rich Megginson <rmeggins@redhat.com>
# SPDX-License-Identifier: GPL-2.0-or-later
#
""" Parse ini or properties file """

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: kernel_settings_get_config

short_description: Parse given ini or properties file and return the data

version_added: "2.13.0"

description:
    - "WARNING: Do not use this module directly! It is only for role internal use."
    - Parse the given ini or properties file and return a dict
    - The dict keys are the section names or DEFAULT
    - The dict values are a list of dicts - each item has a name and a value

options:
    path:
        description: Path to parse
        required: true
        type: str

author:
    - Rich Megginson (@richm)
"""

EXAMPLES = """
- name: Read ini file
  kernel_settings_get_config:
    path: /etc/tuned/kernel_settings/profile.ini
  register: __kernel_settings_result
"""

RETURN = """
data:
  description: dict of data - empty if file not found
  returned: always
  type: dict
"""

try:
    import configobj

    HAS_CONFIGOBJ = True
except ImportError:
    HAS_CONFIGOBJ = False

from ansible.module_utils.basic import AnsibleModule


def run_module():
    """The entry point of the module."""

    module_args = dict(
        path=dict(type="str", required=True),
    )

    result = dict(changed=False)

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    try:
        cobj = configobj.ConfigObj(module.params["path"])
        data = cobj.dict()
        result["data"] = data
    except IOError:
        result["data"] = {}
    module.exit_json(**result)


def main():
    """The main function!"""
    run_module()


if __name__ == "__main__":
    main()
