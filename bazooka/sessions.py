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

import time
from typing import Any, Optional

import yretry
from requests import Response
from requests import exceptions
from requests import sessions

from bazooka import exceptions as exc


def retry_on_network_failure(error: Exception) -> bool:
    """Return True on retriable error"""
    return (
        isinstance(error, exc.BaseHTTPException)
        and error.code in yretry.network.RETRY_HTTP_CODES
    ) or yretry.network.is_network_failure(error)


class ReliableSession(sessions.Session):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(ReliableSession, self).__init__(*args, **kwargs)
        # By default request time profiling is disabled.
        self._log_duration = False

    @property
    def log_duration(self) -> bool:
        return self._log_duration

    @log_duration.setter
    def log_duration(self, flag: bool) -> None:
        self._log_duration = flag

    def _log_response(
        self, response: Response, request_time: Optional[float] = None
    ) -> None:
        """Default handler for response logging.

        request_time(float) contains time of request (in seconds) execution or
                            None if request time profiling is disabled.
        """
        pass

    @yretry.network.retry(retry_on=retry_on_network_failure)
    def request(
        self,
        method: str,
        url: str,
        params: Any = None,
        data: Any = None,
        headers: Any = None,
        cookies: Any = None,
        files: Any = None,
        auth: Any = None,
        timeout: Any = None,
        allow_redirects: bool = True,
        proxies: Any = None,
        hooks: Any = None,
        stream: Optional[bool] = None,
        verify: Any = None,
        cert: Any = None,
        json: Any = None,
    ) -> Response:
        """See documentation for requests.sessions.Session.request

        Raises exception if status code isn't 2xx
        """
        # Save flag in local stack (user can change this flag using
        # set_profile_request_time property.
        log_duration = self.log_duration

        start_time: Optional[float] = None
        request_time: Optional[float] = None

        if log_duration:
            start_time = time.time()

        response = super(ReliableSession, self).request(
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

        if log_duration and start_time is not None:
            request_time = time.time() - start_time

        self._log_response(response, request_time)
        try:
            response.raise_for_status()
        except exceptions.HTTPError as error:
            exc.wrap_to_bazooka_exception(error)
        return response
