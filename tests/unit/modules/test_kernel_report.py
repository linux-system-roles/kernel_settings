# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Mary Provencher <mprovenc@redhat.com>
# SPDX-License-Identifier: GPL-2.0-or-later
#
""" Unit tests for kernel_report module """

import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import kernel_report


class KernelReportGetFields(unittest.TestCase):
    """test operations involving getting existing values from a template machine"""

    @patch('kernel_report.safe_file_get_contents')
    def test_get_sysctl(self, mock):
        """do various tests of get_sysctl_fields"""
        kernel_report.get_sysctl_fields()


if __name__ == "__main__":
    unittest.main()
