# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Mary Provencher <mprovenc@redhat.com>
# SPDX-License-Identifier: GPL-2.0-or-later
#
""" Unit tests for kernel_report module """

import unittest
import sys

try:
    from unittest.mock import patch, mock_open
except ImportError:
    from mock import patch, mock_open

import kernel_report
import pyudev


def dirty_sysctl_side_effect(*args, **kwargs):
    if (
        args[0] == "/proc/sys/vm/dirty_background_bytes"
        or args[0] == "/proc/sys/vm/dirty_background_ratio"
        or args[0] == "/proc/sys/vm/dirty_bytes"
        or args[0] == "/proc/sys/vm/dirty_ratio"
    ):
        return "0"
    return None


def regex_side_effect(*args, **kwargs):
    if (
        args[0] == "/sys/kernel/mm/transparent_hugepage/enabled"
        or args[0] == "/sys/kernel/mm/transparent_hugepage/defrag"
    ):
        return "always defer defer+madvise [madvise] never"
    return None


class KernelReportGetFields(unittest.TestCase):
    """test operations involving getting existing values from a template machine"""

    if sys.version_info.major == 3:
        builtin_module_name = "builtins"
    else:
        builtin_module_name = "__builtin__"

    @patch("{}.open".format(builtin_module_name), new_callable=mock_open, read_data="1")
    def test_safe_file_get_contents_fails_nonexist_file(self, mock_open):
        mock_open.side_effect = IOError
        rtn = kernel_report.safe_file_get_contents("junk")
        self.assertIsNone(rtn)

    @patch("kernel_report.safe_file_get_contents")
    def test_get_sysctl_dirty_values_not_zero(self, mock_get_file):
        """do various tests of get_sysctl_fields"""
        mock_get_file.side_effect = dirty_sysctl_side_effect
        sysctl = kernel_report.get_sysctl_fields()
        self.assertEqual([], sysctl["kernel_settings_sysctl"])

    @patch("kernel_report.safe_file_get_contents")
    def test_get_sysctl_no_none_values(self, mock_get_file):
        """do various tests of get_sysctl_fields"""
        mock_get_file.return_value = None
        sysctl = kernel_report.get_sysctl_fields()
        self.assertEqual([], sysctl["kernel_settings_sysctl"])

    @patch("kernel_report.safe_file_get_contents")
    def test_get_sysfs_other_settings_empty(self, mock_get_file):
        """test for kernel_settings_other to be empty when the files don't exist"""
        mock_get_file.return_value = None
        sysfs = kernel_report.get_sysfs_fields()
        self.assertEqual({}, sysfs["kernel_settings_other"])

    @patch("kernel_report.safe_file_get_contents")
    def test_get_sysfs_regex_fields(self, mock_get_file):
        """test that regex is successful for transparent/defrag fields"""
        mock_get_file.side_effect = regex_side_effect
        sysfs = kernel_report.get_sysfs_fields()
        for setting in sysfs["kernel_settings_other"]["kernel_settings_vm"]["settings"]:
            if (
                setting["name"] == "transparent_hugepage"
                or setting["name"] == "transparent_hugepage.defrag"
            ):
                self.assertEqual("madvise", setting["value"])

    @patch("kernel_report.pyudev.Context.list_devices")
    def test_get_sysfs_no_devices(self, mock_list_devices):
        """ensure that when no devices exist kernel_settings_device_specific is empty"""
        mock_list_devices.return_value = pyudev.Context().list_devices(subsystem="")
        sysfs = kernel_report.get_sysfs_fields()
        self.assertEqual({}, sysfs["kernel_settings_device_specific"])


if __name__ == "__main__":
    unittest.main()
