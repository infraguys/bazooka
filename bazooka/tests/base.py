#!/usr/bin/env python
# Copyright (c) Alexey Zasimov <zasimov@gmail.com>
# Copyright (c) Eugene Frolov <eugene@frolov.net.ru>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys

if sys.version_info[:2] >= (2, 7):
    import unittest
else:
    import unittest2 as unittest

import mock


class TestCase(unittest.TestCase):
    pass


class IsolatedClassTestCase(TestCase):
    """Test class with fake base class."""

    def setUp(self, base_class, tested_class):
        super(IsolatedClassTestCase, self).setUp()
        self.base_class_patcher = mock.patch.object(
            tested_class, "__bases__", (base_class,)
        )
        self.base_class_patcher.start()
        self.base_class_patcher.is_local = True

    def tearDown(self):
        self.base_class_patcher.stop()
        super(IsolatedClassTestCase, self).tearDown()
