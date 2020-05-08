# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Rich Megginson <rmeggins@redhat.com>
# SPDX-License-Identifier: GPLv2+
#
""" Unit tests for kernel_settings module """

import os
import tempfile
import shutil
import unittest
import re
import copy
from configobj import ConfigObj

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

import kernel_settings
import tuned


class KernelSettingsBootloaderCmdline(unittest.TestCase):
    """test bootloader cmdline parsing/formatting/operations"""

    def test_bootloader_cmdline(self):
        """do various tests of bootloader_cmdline_add and bootloader_cmdline_remove"""
        blcmd = kernel_settings.BLCmdLine("")
        self.assertEqual("", str(blcmd))

        blcmd = kernel_settings.BLCmdLine(None)
        self.assertEqual("", str(blcmd))

        blcmd = kernel_settings.BLCmdLine("")
        blcmd.add("foo", "true")
        blcmd.add("bar", None)
        blcmd.add("baz", None)
        self.assertEqual("foo=true bar baz", str(blcmd))

        blcmd = kernel_settings.BLCmdLine(None)
        blcmd.add("foo", "true")
        blcmd.add("bar", None)
        blcmd.add("baz", None)
        self.assertEqual("foo=true bar baz", str(blcmd))

        blcmd = kernel_settings.BLCmdLine("foo=true bar baz")
        blcmd.add("foo", "false")
        self.assertEqual("foo=false bar baz", str(blcmd))

        blcmd = kernel_settings.BLCmdLine("foo=true bar baz")
        blcmd.add("some", "value")
        blcmd.add("another", None)
        blcmd.add("value", "has spaces")
        blcmd.add("foo", "false")
        self.assertEqual(
            "foo=false bar baz some=value another value='has spaces'", str(blcmd)
        )

        blcmd = kernel_settings.BLCmdLine("")
        blcmd.remove("foo")
        self.assertEqual("", str(blcmd))

        blcmd = kernel_settings.BLCmdLine(None)
        blcmd.remove("foo")
        self.assertEqual("", str(blcmd))

        blcmd = kernel_settings.BLCmdLine("foo")
        blcmd.remove("foo")
        self.assertEqual("", str(blcmd))

        blcmd = kernel_settings.BLCmdLine("foo=true")
        blcmd.remove("foo")
        self.assertEqual("", str(blcmd))

        blcmd = kernel_settings.BLCmdLine("foo=true bar baz")
        blcmd.remove("foo")
        self.assertEqual("bar baz", str(blcmd))

        blcmd = kernel_settings.BLCmdLine("foo=true bar baz")
        blcmd.remove("foo")
        blcmd.remove("baz")
        self.assertEqual("bar", str(blcmd))

        blcmd = kernel_settings.BLCmdLine("foo=true bar baz")
        blcmd.remove("baz")
        blcmd.remove("bar")
        self.assertEqual("foo=true", str(blcmd))

        blcmd = kernel_settings.BLCmdLine("foo=true bar baz")
        blcmd.remove("baz")
        blcmd.remove("bar")
        blcmd.remove("foo")
        self.assertEqual("", str(blcmd))

        blcmd = kernel_settings.BLCmdLine("foo=true bar baz")
        blcmd.remove("baz")
        blcmd.remove("bar")
        blcmd.add("another", None)
        blcmd.add("foo", "false")
        self.assertEqual("foo=false another", str(blcmd))


class KernelSettingsInputValidation(unittest.TestCase):
    """test the code that does the input validation"""

    def assertRegex(self, text, expected_regex, msg=None):
        """Fail the test unless the text matches the regular expression."""
        assert re.search(expected_regex, text)

    def test_validate_and_digest_item(self):
        """do various tests of validate_and_digest_item"""
        item = {}
        errlist = kernel_settings.validate_and_digest_item("bogus", item)
        self.assertEqual(len(errlist), 1)
        self.assertEqual(
            errlist[0], "Error: section [bogus] item is missing 'name': {}"
        )
        item = {"name": 1}
        errlist = kernel_settings.validate_and_digest_item("bogus", item)
        self.assertEqual(len(errlist), 1)
        self.assertEqual(
            errlist[0], "Error: section [bogus] item name [1] is not a valid string"
        )
        item = {"name": "name"}
        errlist = kernel_settings.validate_and_digest_item("bogus", item)
        self.assertEqual(len(errlist), 1)
        self.assertEqual(
            errlist[0],
            "Error: section [bogus] item name [name] must have either a "
            "'value' or 'state'",
        )
        item = {"name": "name"}
        errlist = kernel_settings.validate_and_digest_item("bogus", item, True, True)
        self.assertEqual(len(errlist), 0)
        item = {"name": "name", "value": "value", "state": "state"}
        errlist = kernel_settings.validate_and_digest_item("bogus", item)
        self.assertEqual(len(errlist), 1)
        self.assertEqual(
            errlist[0],
            "Error: section [bogus] item name [name] must have only one of "
            "'value' or 'state'",
        )
        item = {"name": "name", "state": 0}
        errlist = kernel_settings.validate_and_digest_item("bogus", item)
        self.assertEqual(len(errlist), 1)
        self.assertEqual(
            errlist[0],
            "Error: section [bogus] item name [name] state value must be "
            "'absent' not [0]",
        )
        item = {"name": "name", "value": ["not a dict"]}
        errlist = kernel_settings.validate_and_digest_item("bogus", item)
        self.assertEqual(len(errlist), 1)
        self.assertEqual(
            errlist[0],
            "Error: section [bogus] item name [name] value [not a dict] is not a dict",
        )
        item = {"name": "name", "value": ["not a dict"]}
        errlist = kernel_settings.validate_and_digest_item("bogus", item)
        self.assertEqual(len(errlist), 1)
        self.assertEqual(
            errlist[0],
            "Error: section [bogus] item name [name] value [not a dict] is not a dict",
        )
        item = {"name": "name", "value": ["not a dict"]}
        errlist = kernel_settings.validate_and_digest_item("bogus", item, False)
        self.assertEqual(len(errlist), 1)
        self.assertEqual(
            errlist[0],
            (
                "Error: section [bogus] item [name] has "
                "unexpected list value ['not a dict']"
            ),
        )
        item = {"name": "name", "value": [{"previous": "invalid"}]}
        errlist = kernel_settings.validate_and_digest_item("bogus", item)
        self.assertEqual(len(errlist), 1)
        self.assertEqual(
            errlist[0],
            (
                "Error: section [bogus] item name [name] has "
                "invalid value for 'previous' [invalid]"
            ),
        )
        item = {"name": "cmdline", "value": "not a list"}
        errlist = kernel_settings.validate_and_digest_item("bootloader", item)
        self.assertEqual(len(errlist), 1)
        self.assertEqual(
            errlist[0],
            (
                "Error: section [bootloader] item [cmdline] must "
                "be a list not [not a list]"
            ),
        )

    def test_validate_and_digest(self):
        """do various tests of validate_and_digest"""
        params = {"section": {"bogus": "dict"}}
        errlist = kernel_settings.validate_and_digest(params)
        self.assertEqual(len(errlist), 1)
        self.assertEqual(
            errlist[0],
            (
                "Error: to remove the section [section] specify "
                "the value {'state': 'empty'}"
            ),
        )
        params = {"section": 0}
        errlist = kernel_settings.validate_and_digest(params)
        self.assertEqual(len(errlist), 1)
        self.assertEqual(
            errlist[0], "Error: section [section] value must be a dict or a list"
        )
        params = {"section": [0]}
        errlist = kernel_settings.validate_and_digest(params)
        self.assertEqual(len(errlist), 1)
        self.assertEqual(
            errlist[0], "Error: section [section] item value [0] is not a dict"
        )
        params = {"section": [{"previous": "bogus"}]}
        errlist = kernel_settings.validate_and_digest(params)
        self.assertEqual(len(errlist), 1)
        self.assertEqual(
            errlist[0],
            "Error: section [section] item has invalid value for 'previous' [bogus]",
        )
        params = {"section": [{"name": "name", "value": "value"}]}
        errlist = kernel_settings.validate_and_digest(params)
        self.assertEqual(len(errlist), 0)
        params = {"section": [{"previous": "replaced"}]}
        errlist = kernel_settings.validate_and_digest(params)
        self.assertEqual(len(errlist), 0)
        self.assertTrue(params["__section_to_replace"]["section"])


class KernelSettingsParamsProfiles(unittest.TestCase):
    """test param to profile conversion and vice versa"""

    def assertRegex(self, text, expected_regex, msg=None):
        """Fail the test unless the text matches the regular expression."""
        assert re.search(expected_regex, text)

    def setUp(self):
        self.test_root_dir = tempfile.mkdtemp(suffix=".lsr")
        os.environ["TEST_ROOT_DIR"] = self.test_root_dir
        self.test_cleanup = kernel_settings.setup_for_testing()
        self.tuned_config = tuned.utils.global_config.GlobalConfig()
        self.logger = Mock()

    def tearDown(self):
        self.test_cleanup()
        shutil.rmtree(self.test_root_dir)
        del os.environ["TEST_ROOT_DIR"]

    def test_load_profile(self):
        """test the code that loads profiles"""
        tuned_app, errmsg = kernel_settings.load_current_profile(
            self.tuned_config, "junk", self.logger
        )
        self.assertIsNone(tuned_app)
        self.assertRegex(errmsg, "Profile does not exist")
        tuned_app, errmsg = kernel_settings.load_current_profile(
            self.tuned_config, "no_profile_file", self.logger
        )
        self.assertIsNone(tuned_app)
        self.assertRegex(errmsg, "Profile does not exist")
        tuned_app, errmsg = kernel_settings.load_current_profile(
            self.tuned_config, "empty_profile_file", self.logger
        )
        self.assertIsNone(tuned_app)
        self.assertRegex(errmsg, "Error loading tuned profile")
        tuned_app, errmsg = kernel_settings.load_current_profile(
            self.tuned_config, "bogus", self.logger
        )
        self.assertIsNone(tuned_app)
        self.assertRegex(errmsg, "Error loading tuned profile")
        tuned_app, _ = kernel_settings.load_current_profile(
            self.tuned_config, "kernel_settings", self.logger
        )
        self.assertEqual("kernel settings", tuned_app.daemon.profile.options["summary"])
        self.assertEqual(0, len(tuned_app.daemon.profile.units))
        tuned_app, _ = kernel_settings.load_current_profile(
            self.tuned_config, "basic_settings", self.logger
        )
        self.assertEqual("kernel settings", tuned_app.daemon.profile.options["summary"])
        units = tuned_app.daemon.profile.units
        self.assertIn("sysctl", units)
        self.assertIn("sysfs", units)
        self.assertIn("vm", units)
        self.assertIn("bootloader", units)
        self.assertEqual(4, len(units["sysctl"].options))
        self.assertEqual(4, len(units["sysfs"].options))
        self.assertEqual(1, len(units["vm"].options))
        self.assertEqual(1, len(units["bootloader"].options))

    def test_apply_params_to_empty_profile(self):
        """test applying params to empty profile"""
        params = {
            "sysctl": [{"name": "fs.epoll.max_user_watches", "value": 785592}],
            "sysfs": [{"name": "/sys/kernel/debug/x86/pti_enabled", "value": 0}],
            "vm": [{"name": "transparent_hugepages", "value": "never"}],
            "bootloader": [
                {
                    "name": "cmdline",
                    "value": [
                        {"name": "spectre_v2", "value": "off"},
                        {"name": "nopti"},
                        {"name": "quiet"},
                        {"name": "splash"},
                    ],
                }
            ],
        }
        tuned_app, _ = kernel_settings.load_current_profile(
            self.tuned_config, "kernel_settings", self.logger
        )
        current_profile = tuned_app.daemon.profile
        errlist = kernel_settings.validate_and_digest(params)
        self.assertEqual(len(errlist), 0)
        changestatus = kernel_settings.apply_params_to_profile(
            params, current_profile, False
        )
        self.assertEqual(kernel_settings.CHANGES, changestatus)
        sysctl = {"fs.epoll.max_user_watches": "785592"}
        self.assertEqual(sysctl, dict(current_profile.units["sysctl"].options))
        sysfs = {"/sys/kernel/debug/x86/pti_enabled": "0"}
        self.assertEqual(sysfs, dict(current_profile.units["sysfs"].options))
        vm = {"transparent_hugepages": "never"}
        self.assertEqual(vm, current_profile.units["vm"].options)
        cmdline = {"cmdline": "spectre_v2=off nopti quiet splash"}
        self.assertEqual(cmdline, dict(current_profile.units["bootloader"].options))
        # test idempotency
        changestatus = kernel_settings.apply_params_to_profile(
            params, current_profile, False
        )
        self.assertEqual(kernel_settings.NOCHANGES, changestatus)

    def test_apply_params_and_ops_to_profile(self):
        """test applying params and operations to a profile"""
        params = {
            "sysctl": [
                {"name": "fs.epoll.max_user_watches", "value": 785592},
                {"name": "kernel.threads-max", "state": "absent"},
                {"name": "fs.file-max", "state": "absent"},
            ],
            "sysfs": [
                {"previous": "replaced"},
                {"name": "/sys/kernel/debug/x86/pti_enabled", "value": 0},
            ],
            "vm": {"state": "empty"},
            "bootloader": [
                {
                    "name": "cmdline",
                    "value": [
                        {"name": "someother", "value": "value"},
                        {"name": "spectre_v2", "value": "off"},
                        {"name": "nopti"},
                        {"name": "quiet", "state": "absent"},
                        {"name": "splash", "state": "absent"},
                    ],
                }
            ],
        }
        paramsorig = copy.deepcopy(params)
        tuned_app, _ = kernel_settings.load_current_profile(
            self.tuned_config, "basic_settings", self.logger
        )
        current_profile = tuned_app.daemon.profile
        errlist = kernel_settings.validate_and_digest(params)
        self.assertEqual(len(errlist), 0)
        changestatus = kernel_settings.apply_params_to_profile(
            params, current_profile, False
        )
        self.assertEqual(kernel_settings.CHANGES, changestatus)
        sysctl = {"fs.epoll.max_user_watches": "785592", "vm.max_map_count": "65530"}
        self.assertEqual(sysctl, dict(current_profile.units["sysctl"].options))
        sysfs = {"/sys/kernel/debug/x86/pti_enabled": "0"}
        self.assertEqual(sysfs, dict(current_profile.units["sysfs"].options))
        self.assertNotIn("vm", current_profile.units)
        cmdline = {"cmdline": "spectre_v2=off nopti someother=value"}
        self.assertEqual(cmdline, dict(current_profile.units["bootloader"].options))
        # idempotency
        errlist = kernel_settings.validate_and_digest(paramsorig)
        self.assertEqual(len(errlist), 0)
        changestatus = kernel_settings.apply_params_to_profile(
            paramsorig, current_profile, False
        )
        self.assertEqual(kernel_settings.NOCHANGES, changestatus)

    def test_apply_params_with_purge(self):
        """test applying params to empty profile"""
        params = {
            "sysctl": [{"name": "fs.epoll.max_user_watches", "value": 785592}],
            "sysfs": [{"name": "/sys/kernel/debug/x86/pti_enabled", "value": 0}],
            "bootloader": [
                {
                    "name": "cmdline",
                    "value": [
                        {"name": "spectre_v2", "value": "off"},
                        {"name": "nopti"},
                        {"name": "quiet"},
                        {"name": "splash"},
                    ],
                }
            ],
        }
        tuned_app, _ = kernel_settings.load_current_profile(
            self.tuned_config, "basic_settings", self.logger
        )
        current_profile = tuned_app.daemon.profile
        errlist = kernel_settings.validate_and_digest(params)
        self.assertEqual(len(errlist), 0)
        changestatus = kernel_settings.apply_params_to_profile(
            params, current_profile, True
        )
        self.assertEqual(kernel_settings.CHANGES, changestatus)
        sysctl = {"fs.epoll.max_user_watches": "785592"}
        self.assertEqual(sysctl, dict(current_profile.units["sysctl"].options))
        sysfs = {"/sys/kernel/debug/x86/pti_enabled": "0"}
        self.assertEqual(sysfs, dict(current_profile.units["sysfs"].options))
        self.assertNotIn("vm", current_profile.units)
        cmdline = {"cmdline": "spectre_v2=off nopti quiet splash"}
        self.assertEqual(cmdline, dict(current_profile.units["bootloader"].options))
        # test idempotency
        changestatus = kernel_settings.apply_params_to_profile(
            params, current_profile, True
        )
        self.assertEqual(kernel_settings.NOCHANGES, changestatus)

    def test_write_profile(self):
        """test applying params and writing new profile"""
        params = {
            "sysctl": [{"name": "fs.epoll.max_user_watches", "value": 785592}],
            "sysfs": [{"name": "/sys/kernel/debug/x86/pti_enabled", "value": 0}],
            "vm": [{"name": "transparent_hugepages", "value": "never"}],
            "bootloader": [
                {
                    "name": "cmdline",
                    "value": [
                        {"name": "spectre_v2", "value": "off"},
                        {"name": "nopti"},
                        {"name": "quiet"},
                        {"name": "splash"},
                    ],
                }
            ],
        }
        errlist = kernel_settings.validate_and_digest(params)
        self.assertEqual(len(errlist), 0)
        tuned_app, _ = kernel_settings.load_current_profile(
            self.tuned_config, "kernel_settings", self.logger
        )
        current_profile = tuned_app.daemon.profile
        changestatus = kernel_settings.apply_params_to_profile(
            params, current_profile, False
        )
        self.assertEqual(kernel_settings.CHANGES, changestatus)
        kernel_settings.write_profile(current_profile)
        fname = os.path.join(
            tuned.consts.LOAD_DIRECTORIES[-1], "kernel_settings", "tuned.conf"
        )
        expected_lines = [
            "# File managed by Ansible - DO NOT EDIT",
            "[main]",
            "summary = kernel settings",
            "[sysctl]",
            "fs.epoll.max_user_watches = 785592",
            "[sysfs]",
            "/sys/kernel/debug/x86/pti_enabled = 0",
            "[vm]",
            "transparent_hugepages = never",
            "[bootloader]",
            "cmdline = spectre_v2=off nopti quiet splash",
        ]
        expected = ConfigObj(expected_lines)
        actual = None
        with open(fname, "r") as ff:
            actual = ConfigObj(ff)
        self.assertEqual(expected, actual)
        self.assertEqual(expected.initial_comment, actual.initial_comment)


if __name__ == "__main__":
    unittest.main()
