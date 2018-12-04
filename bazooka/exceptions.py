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

from requests import exceptions
from six.moves import http_client as httplib


class BaseHTTPException(Exception):

    def __init__(self, cause):
        super(BaseHTTPException, self).__init__(str(cause))
        self._cause = cause
        self._code = self._cause.response.status_code

    @property
    def cause(self):
        return self._cause

    @property
    def code(self):
        return self._code


class ClientError(BaseHTTPException):
    pass


class NotFoundError(ClientError):
    pass


class ConflictError(ClientError):
    pass


def wrap_to_bazooka_exception(cause):
    if isinstance(cause, exceptions.HTTPError):
        if httplib.NOT_FOUND == cause.response.status_code:
            raise NotFoundError(cause)
        elif httplib.CONFLICT == cause.response.status_code:
            raise ConflictError(cause)
        raise BaseHTTPException(cause)
    raise cause
