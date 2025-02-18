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
from six import moves

from bazooka.tests import base

from bazooka import client
from bazooka import sessions


class MicroserviceSessionInitializationTestCase(base.TestCase):

    def test_verify_ssl_flag(self):
        """[Positive] MicroserviceSession rewrites verify flag."""
        auth = mock.Mock()
        verify_ssl = mock.Mock()
        # XXX(Alexey Zasimov): Restore ReliableSession after mock.
        #                      IsolatedClassTestCases doesn't work correctly.
        moves.reload_module(client)
        session = client.MicroserviceSession(auth=auth, verify_ssl=verify_ssl)
        self.assertEqual(session.verify, verify_ssl)

    def test_correlation_id_in_headers(self):
        """[Positive] Correlation id  in headers."""
        auth = mock.Mock()
        verify_ssl = mock.Mock()
        correlation_id = mock.Mock()
        correlation_id_header_name = mock.Mock()
        # XXX(Alexey Zasimov): Restore ReliableSession after mock.
        #                      IsolatedClassTestCases doesn't work correctly.
        moves.reload_module(client)
        session = client.MicroserviceSession(
            auth=auth,
            verify_ssl=verify_ssl,
            correlation_id=correlation_id,
            correlation_id_header_name=correlation_id_header_name,
        )

        self.assertEqual(
            session.headers[correlation_id_header_name], correlation_id
        )

    def test_log_duration_is_set(self):
        """[Positive] I can set log duration flag for MicroserviceSession."""
        auth = mock.Mock()
        verify_ssl = mock.Mock()
        correlation_id = mock.Mock()
        correlation_id_header_name = mock.Mock()

        # XXX(Alexey Zasimov): Restore ReliableSession after mock.
        #                      IsolatedClassTestCases doesn't work correctly.
        moves.reload_module(client)

        session = client.MicroserviceSession(
            auth=auth,
            verify_ssl=verify_ssl,
            correlation_id=correlation_id,
            correlation_id_header_name=correlation_id_header_name,
            log_duration=True,
        )

        self.assertTrue(session.log_duration)


class SensitiveMicroserviceSessionInitializationTestCase(base.TestCase):

    def test_curl_mixin_override(self):
        auth = mock.Mock()
        verify_ssl = mock.Mock()
        correlation_id = mock.Mock()
        correlation_id_header_name = mock.Mock()
        # XXX(Alexey Zasimov): Restore ReliableSession after mock.
        #                      IsolatedClassTestCases doesn't work correctly.
        moves.reload_module(client)
        session = client.SensitiveMicroserviceSession(
            auth=auth,
            verify_ssl=verify_ssl,
            correlation_id=correlation_id,
            correlation_id_header_name=correlation_id_header_name,
        )

        self.assertEqual(session._sanitize_body("123"), session.SANITIZED_PLUG)


class MicroserviceSessionTestCase(base.TestCase):

    def setUp(self):
        super(MicroserviceSessionTestCase, self).setUp()
        auth = mock.Mock()
        verify_ssl = mock.Mock()
        self.session = client.MicroserviceSession(
            auth=auth, verify_ssl=verify_ssl
        )

    def test_log_response_without_request_time(self):
        """[Positive] Logging for response works."""
        logger = mock.MagicMock()

        response = mock.MagicMock()
        response.url = "fake url"
        response.status_code = "fake status code"
        response.reason = "fake reason"
        response.text = "fake response"

        with mock.patch.object(
            self.session, "get_logger", return_value=logger
        ):
            self.assertIsNone(self.session._log_response(response))

            logger.info.assert_called_once_with(
                "Response: from %s with status code %s %s: %s",
                response.url,
                response.status_code,
                response.reason,
                response.text,
            )

    def test_log_response_with_request_time(self):
        """[Positive] Logging for response works (+ request time)."""
        logger = mock.MagicMock()

        request_time = 79.87

        response = mock.MagicMock()
        response.url = "fake url"
        response.status_code = "fake status code"
        response.reason = "fake reason"
        response.text = "fake response"

        with mock.patch.object(
            self.session, "get_logger", return_value=logger
        ):
            self.assertIsNone(
                self.session._log_response(response, request_time)
            )

            logger.info.assert_called_once_with(
                "Response(%s s): from %s with status code %s %s: %s",
                request_time,
                response.url,
                response.status_code,
                response.reason,
                response.text,
            )


class ClientTestCase(base.TestCase):

    def setUp(self):
        super(ClientTestCase, self).setUp()

        self.basic_auth_token = mock.Mock()
        self.auth_user_token = mock.Mock()

        self.auth = mock.Mock()

        self.verify_ssl = mock.Mock()
        self.allow_redirects = mock.Mock()
        self.correlation_id = mock.Mock()
        self.correlation_id_header_name = mock.Mock()
        self.log_duration = mock.Mock()

        self.client = client.Client(
            auth=self.auth,
            verify_ssl=self.verify_ssl,
            allow_redirects=self.allow_redirects,
            correlation_id=self.correlation_id,
            correlation_id_header_name=self.correlation_id_header_name,
            log_duration=self.log_duration,
        )

    def test_session_initialization(self):
        """[Positive] session is initialized with valid parameters."""

        with mock.patch.object(self.client, "SESSION"):
            self.client.request("FAKEMETHOD", "FAKE_URL")

            self.client.SESSION.assert_called_once_with(
                self.auth,
                self.verify_ssl,
                self.correlation_id,
                self.correlation_id_header_name,
                self.log_duration,
            )

    def test_get_calls_request(self):
        """get method calls request with valid arguments."""

        url = mock.Mock()
        params = mock.Mock()
        kwargs = {"fake": 1}

        response = mock.Mock()

        with mock.patch.object(self.client, "request") as request:
            request.return_value = response

            self.assertEqual(self.client.get(url, params, **kwargs), response)

            request.assert_called_once_with(
                "get",
                url,
                params=params,
                allow_redirects=self.allow_redirects,
                fake=1,
            )

    def test_options_calls_request(self):
        """options method calls request with valid arguments."""

        url = mock.Mock()
        kwargs = {"fake": 1}

        response = mock.Mock()

        with mock.patch.object(self.client, "request") as request:
            request.return_value = response

            self.assertEqual(self.client.options(url, **kwargs), response)

            request.assert_called_once_with(
                "options", url, allow_redirects=self.allow_redirects, fake=1
            )

    def test_head_calls_request(self):
        """head method calls request with valid arguments."""

        url = mock.Mock()
        kwargs = {"fake": 1}

        response = mock.Mock()

        with mock.patch.object(self.client, "request") as request:
            request.return_value = response

            self.assertEqual(self.client.head(url, **kwargs), response)

            request.assert_called_once_with(
                "head", url, allow_redirects=False, fake=1
            )

    def test_post_calls_request(self):
        """get method calls request with valid arguments."""

        url = mock.Mock()
        data = mock.Mock()
        json = mock.Mock()
        kwargs = {"fake": 1}

        response = mock.Mock()

        with mock.patch.object(self.client, "request") as request:
            request.return_value = response

            self.assertEqual(
                self.client.post(url, data, json, **kwargs), response
            )

            request.assert_called_once_with(
                "post", url, data=data, json=json, fake=1
            )

    def test_put_calls_request(self):
        """get method calls request with valid arguments."""

        url = mock.Mock()
        data = mock.Mock()
        kwargs = {"fake": 1}

        response = mock.Mock()

        with mock.patch.object(self.client, "request") as request:
            request.return_value = response

            self.assertEqual(self.client.put(url, data, **kwargs), response)

            request.assert_called_once_with("put", url, data=data, fake=1)

    def test_delete_calls_request(self):
        """delete method calls request with valid arguments."""

        url = mock.Mock()
        kwargs = {"fake": 1}

        response = mock.Mock()

        with mock.patch.object(self.client, "request") as request:
            request.return_value = response

            self.assertEqual(self.client.delete(url, **kwargs), response)

            request.assert_called_once_with("delete", url, fake=1)

    def test_request_with_default_timeout(self):
        """request method calls with valid defsault timeout."""

        url = mock.Mock()
        timeouts = [45, 60, None]

        moves.reload_module(client)
        for timeout in timeouts:
            kwargs = {"default_timeout": timeout} if timeout else {}
            http_client = client.Client(**kwargs)

            session_cls = sessions.ReliableSession
            with mock.patch.object(session_cls, "request") as request:
                http_client.request("get", url)
                expected = timeout or client.DEFAULT_TIMEOUT
                request.assert_called_once_with(
                    method="get", url=url, timeout=expected
                )


class MicroserviceClientTestCase(base.TestCase):

    def test_client_instantiation(self):
        """[Positive] is super called correct (Client class)."""

        auth = mock.Mock()

        cli = client.Client(
            auth=auth,
            verify_ssl="verify_ssl",
            allow_redirects="allow_redirects",
            correlation_id="correlation_id",
            correlation_id_header_name="correlation_id_header_name",
            log_duration="log_duration",
        )

        self.assertIs(cli._auth, auth)
        self.assertIs(cli._verify_ssl, "verify_ssl")
        self.assertIs(cli._allow_redirects, "allow_redirects")
        self.assertIs(cli._correlation_id, "correlation_id")
        self.assertIs(
            cli._correlation_id_header_name, "correlation_id_header_name"
        )
        self.assertIs(cli._log_duration, "log_duration")


class SensitiveMicroserviceClientTestCase(base.TestCase):

    def test_client_instantiation(self):
        """[Positive] is super called correct (Client class)."""

        auth = mock.Mock()

        cli = client.Client(
            auth=auth,
            verify_ssl="verify_ssl",
            allow_redirects="allow_redirects",
            correlation_id="correlation_id",
            correlation_id_header_name="correlation_id_header_name",
            log_duration="log_duration",
            session=client.SensitiveMicroserviceSession,
        )

        self.assertIs(cli._auth, auth)
        self.assertIs(cli._verify_ssl, "verify_ssl")
        self.assertIs(cli._allow_redirects, "allow_redirects")
        self.assertIs(cli._correlation_id, "correlation_id")
        self.assertIs(
            cli._correlation_id_header_name, "correlation_id_header_name"
        )
        self.assertIs(cli._log_duration, "log_duration")
        self.assertIs(cli.SESSION, client.SensitiveMicroserviceSession)


class BasicAuthClientTestCase(base.TestCase):

    @mock.patch("requests.auth.HTTPBasicAuth")
    def test_client_instantiation(self, auth_mock):
        """[Positive] is super called correct (BasicAuthClient class)."""

        cli = client.BasicAuthClient(
            username="username",
            password="password",
            verify_ssl="verify_ssl",
            allow_redirects="allow_redirects",
            correlation_id="correlation_id",
            correlation_id_header_name="correlation_id_header_name",
            log_duration="log_duration",
        )

        auth_mock.assert_called_once_with(
            username="username", password="password"
        )
        self.assertIs(cli._auth, auth_mock())
        self.assertIs(cli._verify_ssl, "verify_ssl")
        self.assertIs(cli._allow_redirects, "allow_redirects")
        self.assertIs(cli._correlation_id, "correlation_id")
        self.assertIs(
            cli._correlation_id_header_name, "correlation_id_header_name"
        )
        self.assertIs(cli._log_duration, "log_duration")
