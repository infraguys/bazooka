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

from typing import Any, Dict, Mapping, Set, cast

from requests import PreparedRequest, Request


class CurlLoggingMixin(object):
    """Mixin adds request logging in curl format (for each request)

    Formatted request will be logged with INFO level.

    Values of SENSITIVE_HEADERS will be wiped out from logs.

    Mixin can be used with request.sessions.Session class because it
    overloads prepare_request method to add curl-like logging.
    """

    # Should be uppercase
    SENSITIVE_HEADERS: Set[str] = {
        "TOKEN",
        "AUTHORIZATION",
        "BASICAUTH",
        "X-API-KEY",
        "X-AUTH-TOKEN",
        "X-SERVICE-TOKEN",
        "COOKIE",
    }

    def prepare_request(self, request: Request) -> PreparedRequest:
        prepared_request = cast(Any, super(CurlLoggingMixin, self)).prepare_request(
            request
        )
        self._log_request(prepared_request)
        return prepared_request

    @staticmethod
    def _mask(value: Any) -> str:
        return "<%s>" % value

    def _hide_sensitive_headers(self, data: Mapping[str, Any]) -> Dict[str, Any]:
        sanitized_headers = dict(data)

        for param in sanitized_headers:
            if str(param).upper() in self.SENSITIVE_HEADERS:
                sanitized_headers[param] = self._mask(param)

        return sanitized_headers

    def _sanitize_body(self, body: Any) -> Any:
        return body

    def _curlify_request(self, request: PreparedRequest) -> str:
        """OpenStack approach for human-readable requests logging."""
        parameters: Dict[str, Any] = {}
        headers = self._hide_sensitive_headers(dict(request.headers))

        parameters["headers"] = " ".join(
            ["-H '%s: %s'" % (k, v) for k, v in headers.items()]
        )

        parameters["data"] = (
            ("-d '%s'" % self._sanitize_body(request.body))
            if request.body is not None
            else ""
        )

        parameters["method"] = "-X '%s'" % request.method
        parameters["url"] = request.url

        return "curl %(method)s %(headers)s %(data)s %(url)s" % parameters

    def _log_request(self, request: PreparedRequest) -> None:
        logger = cast(Any, self).get_logger()
        curl_cmd = self._curlify_request(request)
        logger.info("HTTP(s) request: %s", curl_cmd)


class SensitiveCurlLoggingMixin(CurlLoggingMixin):
    SANITIZED_PLUG = "<SENSITIVE_DATA>"

    def _sanitize_body(self, body: Any) -> str:
        return self.SANITIZED_PLUG
