# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Mary Provencher <mprovenc@redhat.com>
# SPDX-License-Identifier: GPL-2.0-or-later
#
""" Unit tests for kernel_report module """

import unittest, sys

try:
    from unittest.mock import patch, mock_open
except ImportError:
    from mock import patch, mock_open

import kernel_report


def dirty_sysctl_side_effect(*args, **kwargs):
    if (args[0] == "/proc/sys/vm/dirty_background_bytes" or
        args[0] == "/proc/sys/vm/dirty_background_ratio" or
        args[0] == "/proc/sys/vm/dirty_bytes" or
        args[0] == "/proc/sys/vm/dirty_ratio"):
        return '0'
    return None

class KernelReportGetFields(unittest.TestCase):
    """test operations involving getting existing values from a template machine"""

    if sys.version_info.major == 3:
        builtin_module_name = 'builtins'
    else:
        builtin_module_name = '__builtin__'

    @patch('{}.open'.format(builtin_module_name), new_callable=mock_open, read_data='1')
    def test_safe_file_get_contents_fails_nonexist_file(self, mock_open):
        mock_open.side_effect = IOError
        rtn = kernel_report.safe_file_get_contents("junk")
        self.assertIsNone(rtn)

    @patch('kernel_report.safe_file_get_contents')
    def test_get_sysctl_dirty_values_not_zero(self, mock_get_file):
        """do various tests of get_sysctl_fields"""
        mock_get_file.side_effect = dirty_sysctl_side_effect
        sysctl = kernel_report.get_sysctl_fields()
        self.assertEqual([], sysctl["kernel_settings_sysctl"])

    @patch('kernel_report.safe_file_get_contents')
    def test_get_sysctl_no_none_values(self, mock_get_file):
        """do various tests of get_sysctl_fields"""
        mock_get_file.return_value = None
        sysctl = kernel_report.get_sysctl_fields()
        self.assertEqual([], sysctl["kernel_settings_sysctl"])

    # test for kernel_settings_other to be empty when the files don't exist

    # test that regex is successful for transparent/defrag fields

    # test that when no cpus exist nothing is returned (tests for other modules as well)


    @patch('kernel_report.safe_file_get_contents')
    @patch('re.findall')
    def test_get_sysfs(self, mock_get_file, mock_re_search):
        kernel_report.get_sysfs_fields()


if __name__ == "__main__":
    unittest.main()
