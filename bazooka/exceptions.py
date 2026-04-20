# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2018 Mail.ru Group
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from typing import NoReturn

from requests import Response
from requests import exceptions
from six.moves import http_client as httplib


class BaseHTTPException(Exception):
    def __init__(self, cause: exceptions.HTTPError) -> None:
        super(BaseHTTPException, self).__init__(str(cause))
        self._cause = cause
        response = self._response_from_error(cause)
        self._code = response.status_code

    @staticmethod
    def _response_from_error(cause: exceptions.HTTPError) -> Response:
        if cause.response is None:
            raise ValueError("HTTPError must contain a response")
        return cause.response

    @property
    def cause(self) -> exceptions.HTTPError:
        return self._cause

    @property
    def code(self) -> int:
        return self._code


class ClientError(BaseHTTPException):
    pass


class NotFoundError(ClientError):
    pass


class ConflictError(ClientError):
    pass


class BadRequestError(ClientError):
    pass


class ForbiddenError(ClientError):
    pass


class UnauthorizedError(ClientError):
    pass


def wrap_to_bazooka_exception(cause: Exception) -> NoReturn:
    if isinstance(cause, exceptions.HTTPError):
        response = BaseHTTPException._response_from_error(cause)
        if httplib.NOT_FOUND == response.status_code:
            raise NotFoundError(cause)
        elif httplib.UNAUTHORIZED == response.status_code:
            raise UnauthorizedError(cause)
        elif httplib.CONFLICT == response.status_code:
            raise ConflictError(cause)
        elif httplib.BAD_REQUEST == response.status_code:
            raise BadRequestError(cause)
        elif httplib.FORBIDDEN == response.status_code:
            raise ForbiddenError(cause)
        raise BaseHTTPException(cause)
    raise cause
