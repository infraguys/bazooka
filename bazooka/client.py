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

import logging

from requests import auth as req_auth

from bazooka import correlation
from bazooka import curl_logging
from bazooka import sessions

DEFAULT_TIMEOUT = 300


class MicroserviceSession(
    correlation.CorrelationLoggerMixin,
    curl_logging.CurlLoggingMixin,
    sessions.ReliableSession,
):

    def __init__(
        self,
        auth,
        verify_ssl,
        correlation_id=None,
        correlation_id_header_name="correlationid",
        log_duration=True,
    ):
        super(MicroserviceSession, self).__init__()
        self.log_duration = log_duration
        self.auth = auth
        # Rewrite default requests.session.Session 'verify' value.
        self.verify = verify_ssl
        self._correlation_id = correlation_id
        self.headers[correlation_id_header_name] = self.correlation_id
        self._logger = logging.getLogger(__name__)

    @property
    def correlation_id(self):
        return self._correlation_id

    def _log_response(self, response, request_time=None):
        """Write to log HTTP status code."""
        logger = self.get_logger()
        if request_time is None:
            logger.info(
                "Response: from %s with status code %s %s: %s",
                response.url,
                response.status_code,
                response.reason,
                response.text,
            )
        else:
            logger.info(
                "Response(%s s): from %s with status code %s %s: %s",
                request_time,
                response.url,
                response.status_code,
                response.reason,
                response.text,
            )


class SensitiveMicroserviceSession(
    curl_logging.SensitiveCurlLoggingMixin, MicroserviceSession
):
    pass


class Client(object):
    """Warning! Client raises exceptions

    Standard behaviour of requests client - returns response object.

    Current client raises appropriate exception if response status
    code isn't 2xx

    Client uses 'retries' library to make retries.

    To intialize client you need to pass request auth object or None. See
    documentation for requests.auth.

    Example:
        from requests import auth
        from bazooka import client

        requests = client.BaseClient(
            auth.HTTPBasicAuth('username', 'password'))
        print requests.get('http://localhost:5003').json()

    Request time profiling is enabled by default.
    """

    SESSION = MicroserviceSession

    def __init__(
        self,
        auth=None,
        verify_ssl=True,
        allow_redirects=True,
        correlation_id=None,
        correlation_id_header_name="correlationid",
        log_duration=True,
        default_timeout=DEFAULT_TIMEOUT,
        session=None,
    ):
        super(Client, self).__init__()
        self._auth = auth
        self._verify_ssl = verify_ssl
        self._allow_redirects = allow_redirects
        self._correlation_id = correlation_id
        self._correlation_id_header_name = correlation_id_header_name
        self._log_duration = log_duration
        self._default_timeout = default_timeout
        if session:
            self.SESSION = session

    @property
    def correlation_id(self):
        return self._correlation_id

    @correlation_id.setter
    def correlation_id(self, val):
        self._correlation_id = val

    @property
    def log_duration(self):
        return self._log_duration

    @log_duration.setter
    def log_duration(self, log_duration):
        self._log_duration = log_duration

    def request(self, method, url, **kwargs):
        """See documentation for requests.api.request."""
        with self.SESSION(
            self._auth,
            self._verify_ssl,
            self._correlation_id,
            self._correlation_id_header_name,
            self._log_duration,
        ) as session:
            kwargs.setdefault("timeout", self._default_timeout)
            return session.request(method=method, url=url, **kwargs)

    def get(self, url, params=None, **kwargs):
        """See documentation for requests.api.get."""
        kwargs.setdefault("allow_redirects", self._allow_redirects)
        return self.request("get", url, params=params, **kwargs)

    def options(self, url, **kwargs):
        """See documentation for requests.api.options."""
        kwargs.setdefault("allow_redirects", self._allow_redirects)
        return self.request("options", url, **kwargs)

    def head(self, url, **kwargs):
        """See documentation for requests.api.head."""
        kwargs.setdefault("allow_redirects", False)
        return self.request("head", url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        """See documentation for requests.api.post."""
        return self.request("post", url, data=data, json=json, **kwargs)

    def put(self, url, data=None, **kwargs):
        """See documentation for requests.api.put."""
        return self.request("put", url, data=data, **kwargs)

    def patch(self, url, data=None, **kwargs):
        """See documentation for requests.api.patch."""
        return self.request("patch", url, data=data, **kwargs)

    def delete(self, url, **kwargs):
        """See documentation for requests.api.delete."""
        return self.request("delete", url, **kwargs)


class BasicAuthClient(Client):
    """HTTP client use basic auth token to authentication

    To intialize client you need to pass a username and a password

    Example:
        from bazooka import BasicAuthClient

        requests = client.BasicAuthClient('efrolov', 'mypassword')
        print requests.get('http://localhost:5003').json()

    """

    def __init__(
        self,
        username,
        password,
        verify_ssl=True,
        allow_redirects=True,
        correlation_id=None,
        correlation_id_header_name="correlationid",
        log_duration=True,
        default_timeout=DEFAULT_TIMEOUT,
    ):
        super(BasicAuthClient, self).__init__(
            req_auth.HTTPBasicAuth(username=username, password=password),
            verify_ssl=verify_ssl,
            allow_redirects=allow_redirects,
            correlation_id=correlation_id,
            correlation_id_header_name=correlation_id_header_name,
            log_duration=log_duration,
            default_timeout=default_timeout,
        )
