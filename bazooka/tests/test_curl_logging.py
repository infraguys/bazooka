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

import collections

import mock

from bazooka.tests import base

from bazooka import curl_logging


class BaseMixinTestCase(base.TestCase):
    mixin_class = None

    def setUp(self):
        """BaseMixinTestCase

        Declare TestedClass with CurlLoggingMixin.
        Set SuperClass as a parent for TestClass.
        """

        class SuperClass(object):

            def prepare_request(self, request):
                pass

            def get_logger(self):
                pass

        class TestedClass(self.mixin_class, SuperClass):
            pass

        self.SuperClass = SuperClass
        self.TestedClass = TestedClass

        super(BaseMixinTestCase, self).setUp()

        self.mixin = TestedClass()


class CurlLoggingMixinTestCase(BaseMixinTestCase):
    mixin_class = curl_logging.CurlLoggingMixin

    def test_prepare_request_calls_log_request(self):
        """prepare_requests invokes super method and _log_request."""
        request = mock.MagicMock()

        with mock.patch.object(
            self.SuperClass, "prepare_request"
        ) as prepare_request:
            with mock.patch.object(self.mixin, "_log_request") as log_request:
                prepare_request.return_value = request

                self.assertEqual(self.mixin.prepare_request(request), request)

                prepare_request.assert_called_once_with(request)

                log_request.assert_called_once_with(request)

    def test_hide_sensitive_headers_is_dict(self):
        """_hide_sensitive_headers hide value for private1 and private2."""
        data = {"public1": 1, "public2": 2, "private1": "a", "private2": "b"}

        with mock.patch.object(
            self.mixin, "SENSITIVE_HEADERS", ("PRIVATE1", "PRIVATE2")
        ):
            filtered = self.mixin._hide_sensitive_headers(data)

            self.assertDictEqual(
                filtered,
                {
                    "public1": 1,
                    "public2": 2,
                    "private1": "<private1>",
                    "private2": "<private2>",
                },
            )

    def test_curlify_request(self):
        """CURLification is working."""
        request = mock.MagicMock()
        request.headers = mock.MagicMock()
        request.body = "body"
        request.method = "GET"
        request.url = "http://super"

        headers = collections.OrderedDict([("H1", "1"), ("H2", "2")])

        with mock.patch.object(
            self.mixin, "_hide_sensitive_headers", return_value=headers
        ):
            self.assertEqual(
                self.mixin._curlify_request(request),
                "curl -X 'GET' -H 'H1: 1' -H 'H2: 2' -d 'body' http://super",
            )

    def test_hide_sensitive_headers(self):
        fake_value = "fake_value"

        seq = curl_logging.CurlLoggingMixin.SENSITIVE_HEADERS

        secret_payload = {k: fake_value for k in seq}
        cleaned_secret_payload = self.mixin._hide_sensitive_headers(
            secret_payload
        )

        non_secret_payload = {"%s_non_secret" % k: fake_value for k in seq}
        cleaned_non_secret_payload = self.mixin._hide_sensitive_headers(
            non_secret_payload
        )

        for k, v in cleaned_secret_payload.items():
            self.assertEqual(self.mixin._mask(k), v)

        for v in cleaned_non_secret_payload.values():
            self.assertEqual(v, fake_value)

    def test_hide_sensitive_headers_mask_value(self):
        value = "abc"
        expected_value = "<%s>" % value

        self.assertEqual(self.mixin._mask(value), expected_value)

    def test_log_request_sequence(self):
        """_log_request sequence is valid."""
        request = mock.Mock()

        logger = mock.MagicMock()
        curl_cmd = "curlification"

        with mock.patch.object(
            self.mixin, "get_logger", return_value=logger
        ) as get_logger:

            with mock.patch.object(
                self.mixin, "_curlify_request", return_value=curl_cmd
            ) as curlify_request:

                self.mixin._log_request(request)

                get_logger.assert_called_once_with()
                curlify_request.assert_called_once_with(request)

                logger.info.assert_called_once_with(
                    "HTTP(s) request: %s", curl_cmd
                )


class SensitiveCurlLoggingMixinTestCase(BaseMixinTestCase):
    mixin_class = curl_logging.SensitiveCurlLoggingMixin

    def test_curlify_request(self):
        request = mock.MagicMock()
        request.headers = mock.MagicMock()
        request.body = "very_important_body"
        request.method = "POST"
        request.url = "http://super"

        headers = collections.OrderedDict([("H1", "1"), ("H2", "2")])

        with mock.patch.object(
            self.mixin, "_hide_sensitive_headers", return_value=headers
        ):
            self.assertEqual(
                self.mixin._curlify_request(request),
                "curl -X 'POST' -H 'H1: 1' -H 'H2: 2' -d '%s' "
                "http://super" % self.mixin.SANITIZED_PLUG,
            )
