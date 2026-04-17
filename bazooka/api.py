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

from typing import Any

from requests import Response

from bazooka import sessions


def request(method: str, url: str, **kwargs: Any) -> Response:
    """See documentation for requests.api.request."""
    with sessions.ReliableSession() as session:
        return session.request(method=method, url=url, **kwargs)


def get(url: str, params: Any = None, **kwargs: Any) -> Response:
    """See documentation for requests.api.get."""
    kwargs.setdefault("allow_redirects", True)
    return request("get", url, params=params, **kwargs)


def options(url: str, **kwargs: Any) -> Response:
    """See documentation for requests.api.options."""
    kwargs.setdefault("allow_redirects", True)
    return request("options", url, **kwargs)


def head(url: str, **kwargs: Any) -> Response:
    """See documentation for requests.api.head."""
    kwargs.setdefault("allow_redirects", False)
    return request("head", url, **kwargs)


def post(
    url: str,
    data: Any = None,
    json: Any = None,
    **kwargs: Any,
) -> Response:
    """See documentation for requests.api.post."""
    return request("post", url, data=data, json=json, **kwargs)


def put(url: str, data: Any = None, **kwargs: Any) -> Response:
    """See documentation for requests.api.put."""
    return request("put", url, data=data, **kwargs)


def patch(url: str, data: Any = None, **kwargs: Any) -> Response:
    """See documentation for requests.api.patch."""
    return request("patch", url, data=data, **kwargs)


def delete(url: str, **kwargs: Any) -> Response:
    """See documentation for requests.api.delete."""
    return request("delete", url, **kwargs)
