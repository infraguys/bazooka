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

import mock

from bazooka.tests import base

from bazooka import correlation


class CorrelationLoggerAdapterTestCase(base.IsolatedClassTestCase):

    def setUp(self):
        super(CorrelationLoggerAdapterTestCase, self).setUp(
            mock.Mock, correlation.CorrelationLoggerAdapter
        )
        logger = mock.Mock()
        self.correlation_id = "fake correlation id"
        self.adapter = correlation.CorrelationLoggerAdapter(
            logger, self.correlation_id
        )

    def test_process(self):
        """Process returns mmessage with correlation ID."""
        msg = "fake message"
        kwargs = mock.Mock()

        res_msg, res_kwargs = self.adapter.process(msg, kwargs)

        self.assertEqual(res_kwargs, kwargs)
        self.assertEqual(
            res_msg, "[correlation_id=fake correlation id] fake message"
        )


class CorrelationLoggerMixinTestCase(base.TestCase):

    def setUp(self):
        super(CorrelationLoggerMixinTestCase, self).setUp()

        class TestedClass(correlation.CorrelationLoggerMixin):

            def __init__(self):
                self._logger = mock.Mock()
                self.correlation_id = mock.Mock()

        self.mixin = TestedClass()

    @mock.patch("bazooka.correlation.CorrelationLoggerAdapter")
    def test_get_logger_returns_adapter(self, CorrelationLoggerAdapter):
        """CorrelationLoggerMixin.get_logger returns adapter"""
        adapter = mock.Mock()

        CorrelationLoggerAdapter.return_value = adapter

        self.assertEqual(self.mixin.get_logger(), adapter)

    @mock.patch("bazooka.correlation.CorrelationLoggerAdapter")
    def test_get_logger_integration_with_adapter(
        self, CorrelationLoggerAdapter
    ):
        """Check integration with CorrelationLoggerAdapter"""
        self.mixin.get_logger()

        CorrelationLoggerAdapter.assert_called_once_with(
            self.mixin._logger, self.mixin.correlation_id
        )
