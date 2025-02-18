#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2020 Alexandr Popov
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

import mock
from six import moves

import bazooka.exceptions
import bazooka.sessions
from bazooka.tests import base


class FakeResponse(object):
    def __init__(self):
        self.call_count = 0

    def raise_for_status(self):
        self.call_count += 1
        raise bazooka.exceptions.BaseHTTPException(
            mock.Mock(response=mock.MagicMock(status_code=500))
        )


class RetryableSessionTestCase(base.TestCase):

    @mock.patch("time.sleep", return_value=None)
    def test_request_get_retry(self, _patched_sleep):
        """Check that request played more than once on error"""
        moves.reload_module(bazooka.sessions)
        session = bazooka.sessions.ReliableSession()
        response = FakeResponse()

        with mock.patch(
            "requests.sessions.Session.request", return_value=response
        ):
            with self.assertRaises(bazooka.exceptions.BaseHTTPException):
                session.request("GET", "")
        self.assertGreater(response.call_count, 1)
