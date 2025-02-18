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


def fake_retry(*args, **kwargs):
    def wrapper(f):
        return f

    return wrapper


@mock.patch("yretry.network.retry", fake_retry)
def import_sessions():
    """Loads module for testing with mocked decorator."""
    import bazooka.sessions

    moves.reload_module(bazooka.sessions)
    return bazooka.sessions


sessions = import_sessions()


class ReliableSessionTestCase(base.IsolatedClassTestCase):

    def setUp(self):
        class BaseSession(mock.MagicMock):

            def request(self, *args, **kwargs):
                pass

        self.BaseSession = BaseSession

        super(ReliableSessionTestCase, self).setUp(
            BaseSession, sessions.ReliableSession
        )

        self.session = sessions.ReliableSession()

    def test_log_duration_is_disabled_by_default(self):
        self.assertFalse(self.session.log_duration)

    def test_request_pass_throught(self):
        """Check that request method pass throught arguments."""
        method = mock.Mock()
        url = mock.Mock()
        params = mock.Mock()
        data = mock.Mock()
        headers = mock.Mock()
        cookies = mock.Mock()
        files = mock.Mock()
        auth = mock.Mock()
        timeout = mock.Mock()
        allow_redirects = mock.Mock()
        proxies = mock.Mock()
        hooks = mock.Mock()
        stream = mock.Mock()
        verify = mock.Mock()
        cert = mock.Mock()
        json = mock.Mock()

        response = mock.MagicMock()

        with mock.patch.object(
            self.BaseSession, "request", return_value=response
        ):
            self.BaseSession.request.return_value = response

            self.assertEqual(
                self.session.request(
                    method,
                    url,
                    params,
                    data,
                    headers,
                    cookies,
                    files,
                    auth,
                    timeout,
                    allow_redirects,
                    proxies,
                    hooks,
                    stream,
                    verify,
                    cert,
                    json,
                ),
                response,
            )

            self.BaseSession.request.assert_called_once_with(
                method=method,
                url=url,
                params=params,
                data=data,
                headers=headers,
                cookies=cookies,
                files=files,
                auth=auth,
                timeout=timeout,
                allow_redirects=allow_redirects,
                proxies=proxies,
                hooks=hooks,
                stream=stream,
                verify=verify,
                cert=cert,
                json=json,
            )

    def test_request_calls_raise_for_status(self):
        """Check that request method calls raise_for_status."""
        method = mock.Mock()
        url = mock.Mock()

        response = mock.MagicMock()

        with mock.patch.object(
            self.BaseSession, "request", return_value=response
        ):
            self.BaseSession.request.return_value = response

            self.session.request(method, url)

            response.raise_for_status.assert_called_once_with()

    def test_request_calls_log_response_without_request_time(self):
        """Check that request method calls _log_response.

        Request time profiling is disabled by default.

        request_time is None in this case.
        """
        method = mock.Mock()
        url = mock.Mock()

        response = mock.MagicMock()

        with mock.patch.object(
            self.BaseSession, "request", return_value=response
        ):
            with mock.patch.object(
                self.session, "_log_response"
            ) as log_response:
                self.BaseSession.request.return_value = response

                self.session.request(method, url)

                log_response.assert_called_once_with(response, None)

    def test_log_duration_setter(self):
        """[Positive] I can change log_duration flag."""
        current = self.session._log_duration
        self.session.log_duration = not current
        self.assertEqual(self.session._log_duration, not current)

    @mock.patch("time.time")
    def test_request_calls_log_response_with_request_time(self, time):
        """Check that request method calls _log_response.

        Request time profiling is enabled.

        """
        method = mock.Mock()
        url = mock.Mock()

        response = mock.MagicMock()

        time.side_effect = [1, 2]

        self.session.log_duration = True

        with mock.patch.object(
            self.BaseSession, "request", return_value=response
        ):
            with mock.patch.object(
                self.session, "_log_response"
            ) as log_response:
                self.BaseSession.request.return_value = response

                self.session.request(method, url)

                log_response.assert_called_once_with(response, 1)
